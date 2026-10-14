#!/usr/bin/env python3
"""Deterministic file operations for the file-organizer plugin.

Every command that changes files is a dry run unless --apply is given.
Nothing is ever overwritten: a name collision gets a " (2)", " (3)", ... suffix.
Every applied change is logged to a CSV next to the files so it can be undone.
Hidden files, symlinks, and this tool's own logs and reports are skipped.

Standard library only; Python 3.8+.
"""
import argparse
import csv
import hashlib
import os
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timedelta

CATEGORIES = {
    "Documents": {".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".md", ".pages"},
    "Spreadsheets": {".xls", ".xlsx", ".xlsm", ".csv", ".tsv", ".ods", ".numbers"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".heic", ".webp", ".bmp", ".tif", ".tiff", ".svg"},
    "Presentations": {".ppt", ".pptx", ".odp", ".key"},
}
OWN_PREFIX = "_organizer_"
OWN_FILES = {"duplicate_report.txt", "folder_inventory.csv", "rename_log.csv", "search_results.txt"}


def stamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def is_own(name):
    return name.startswith(OWN_PREFIX) or name in OWN_FILES


def visible(name):
    return not name.startswith(".") and not is_own(name)


def walk_files(root, skip_dirs=()):
    """Yield absolute paths of regular, non-hidden files under root (no symlinks)."""
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames
            if not d.startswith(".")
            and not os.path.islink(os.path.join(dirpath, d))
            and os.path.join(dirpath, d) not in skip_dirs
        )
        for f in sorted(filenames):
            p = os.path.join(dirpath, f)
            if visible(f) and os.path.isfile(p) and not os.path.islink(p):
                yield p


def top_files(root):
    for f in sorted(os.listdir(root)):
        p = os.path.join(root, f)
        if visible(f) and os.path.isfile(p) and not os.path.islink(p):
            yield p


def free_name(path, taken):
    """Return path, or path with ' (n)' before the extension, not on disk and not in taken."""
    base, ext = os.path.splitext(path)
    cand, n = path, 2
    while os.path.exists(cand) or cand in taken:
        cand = f"{base} ({n}){ext}"
        n += 1
    taken.add(cand)
    return cand


def category(path):
    ext = os.path.splitext(path)[1].lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "Other"


def human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def run_plan(root, plan, action, apply, log_name):
    """plan: list of (src, dst). action: 'move' or 'copy'. Prints and optionally applies."""
    verb = "MOVE" if action == "move" else "COPY"
    for src, dst in plan:
        print(f"{verb}\t{os.path.relpath(src, root)}\t->\t{os.path.relpath(dst, root)}")
    if not apply:
        print(f"\nDRY RUN: {len(plan)} file(s) would be {action}d. Re-run with --apply to do it.")
        return None
    log = os.path.join(root, f"{OWN_PREFIX}{log_name}_{stamp()}.csv")
    with open(log, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["action", "source", "destination"])
        for src, dst in plan:
            if os.path.exists(dst):  # appeared since planning; never overwrite
                dst = free_name(dst, set())
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if action == "move":
                shutil.move(src, dst)
            else:
                shutil.copy2(src, dst)
            w.writerow([action, src, dst])
            fh.flush()
    print(f"\nDONE: {len(plan)} file(s) {action}d. Log: {log}")
    return log


# ---------------------------------------------------------------- commands

def cmd_sort(a):
    root = os.path.abspath(a.folder)
    taken, plan, counts = set(), [], defaultdict(int)
    for p in top_files(root):
        cat = category(p)
        plan.append((p, free_name(os.path.join(root, cat, os.path.basename(p)), taken)))
        counts[cat] += 1
    run_plan(root, plan, "move", a.apply, "sort")
    print("\nPer folder:")
    for cat in list(CATEGORIES) + ["Other"]:
        print(f"  {cat}: {counts.get(cat, 0)}")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cmd_dupes(a):
    root = os.path.abspath(a.folder)
    by_size = defaultdict(list)
    by_name = defaultdict(list)
    for p in walk_files(root):
        by_size[os.path.getsize(p)].append(p)
        by_name[os.path.basename(p).lower()].append(p)
    groups = []
    for size, paths in by_size.items():
        if len(paths) < 2 or size == 0:
            continue
        by_hash = defaultdict(list)
        for p in paths:
            by_hash[sha256(p)].append(p)
        for same in by_hash.values():
            if len(same) > 1:
                # Oldest is the "original"; on a tie, the shortest name ("x.pdf" over "x copy.pdf").
                same.sort(key=lambda p: (os.path.getmtime(p), len(os.path.basename(p)), p))
                groups.append((size, same))
    groups.sort(key=lambda g: -g[0] * (len(g[1]) - 1))
    dup_paths = {p for _, g in groups for p in g}
    name_only = [ps for ps in by_name.values() if len(ps) > 1 and not set(ps) <= dup_paths]

    out = os.path.join(root, "duplicate_report.txt")
    wasted = sum(size * (len(g) - 1) for size, g in groups)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(f"Duplicate report for {root}\nGenerated {datetime.now():%Y-%m-%d %H:%M}\n")
        fh.write("Nothing has been deleted.\n\n")
        fh.write(f"IDENTICAL CONTENT: {len(groups)} group(s), {human(wasted)} reclaimable\n")
        fh.write("(byte-for-byte identical; the oldest file is listed as the original)\n\n")
        for i, (size, g) in enumerate(groups, 1):
            fh.write(f"[{i}] {human(size)} each\n")
            fh.write(f"  ORIGINAL   {os.path.relpath(g[0], root)}\n")
            for p in g[1:]:
                fh.write(f"  DUPLICATE  {os.path.relpath(p, root)}\n")
            fh.write("\n")
        fh.write(f"SAME NAME, DIFFERENT CONTENT: {len(name_only)} group(s)\n")
        fh.write("(probably different versions -- not safe to treat as duplicates)\n\n")
        for ps in name_only:
            for p in sorted(ps, key=os.path.getmtime):
                mod = datetime.fromtimestamp(os.path.getmtime(p))
                fh.write(f"  {os.path.relpath(p, root)}  ({human(os.path.getsize(p))}, "
                         f"modified {mod:%Y-%m-%d})\n")
            fh.write("\n")
    print(f"{len(groups)} identical-content group(s), {human(wasted)} reclaimable; "
          f"{len(name_only)} same-name group(s) with different content.\nReport: {out}")


def cmd_inventory(a):
    root = os.path.abspath(a.folder)
    out = os.path.join(root, "folder_inventory.csv")
    by_type = defaultdict(lambda: [0, 0])
    n = 0
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["file_name", "file_type", "size_bytes", "size", "date_modified", "folder_path"])
        for p in walk_files(root):
            st = os.stat(p)
            ext = os.path.splitext(p)[1].lower().lstrip(".") or "(none)"
            rel_dir = os.path.relpath(os.path.dirname(p), root)
            w.writerow([os.path.basename(p), ext, st.st_size, human(st.st_size),
                        datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "." if rel_dir == "." else rel_dir])
            by_type[ext][0] += 1
            by_type[ext][1] += st.st_size
            n += 1
    print(f"{n} file(s) inventoried. CSV: {out}\n\nTop file types (count, total size):")
    for ext, (c, s) in sorted(by_type.items(), key=lambda kv: -kv[1][0])[:15]:
        print(f"  .{ext}: {c} file(s), {human(s)}")


def cmd_archive(a):
    root = os.path.abspath(a.folder)
    archive = os.path.join(root, f"Archive_{datetime.now():%Y-%m-%d}")
    cutoff = datetime.now() - timedelta(days=a.months * 30.44)
    existing_archives = {
        os.path.join(root, d) for d in os.listdir(root)
        if d.startswith("Archive_") and os.path.isdir(os.path.join(root, d))
    }
    taken, plan = set(), []
    for p in walk_files(root, skip_dirs=existing_archives | {archive}):
        if datetime.fromtimestamp(os.path.getmtime(p)) < cutoff:
            plan.append((p, free_name(os.path.join(archive, os.path.relpath(p, root)), taken)))
    print(f"Cutoff: not modified since {cutoff:%Y-%m-%d} ({a.months} months)\n")
    run_plan(root, plan, "move", a.apply, "archive")


def cmd_flatten(a):
    src_root = os.path.abspath(a.folder)
    out = os.path.abspath(a.output)
    if out == src_root or out.startswith(src_root + os.sep):
        sys.exit("Output folder must be outside the source folder.")
    taken, plan = set(), []
    for p in walk_files(src_root):
        rel_dir = os.path.relpath(os.path.dirname(p), src_root)
        prefix = "" if rel_dir == "." else rel_dir.replace(os.sep, "__") + "__"
        plan.append((p, free_name(os.path.join(out, prefix + os.path.basename(p)), taken)))
    for s, d in plan:
        print(f"COPY\t{os.path.relpath(s, src_root)}\t->\t{d}")
    if not a.apply:
        print(f"\nDRY RUN: {len(plan)} file(s) would be copied to {out}. "
              "Re-run with --apply to do it. The source folder is never changed.")
        return
    os.makedirs(out, exist_ok=True)
    log = os.path.join(out, f"{OWN_PREFIX}flatten_{stamp()}.csv")
    with open(log, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["action", "source", "destination"])
        for s, d in plan:
            if os.path.exists(d):
                d = free_name(d, set())
            shutil.copy2(s, d)
            w.writerow(["copy", s, d])
    print(f"\nDONE: {len(plan)} file(s) copied. Source untouched. Log: {log}")


def cmd_scaffold(a):
    parent = os.path.abspath(a.parent)
    base = os.path.join(parent, a.name)
    folders = [
        ("01_Contracts", "Signed agreements, SOWs, NDAs, and contract amendments."),
        ("02_Briefs", "Project briefs, requirements, and scope documents from the client."),
        ("03_Research", "Background research, references, data, and competitor material."),
        ("04_Drafts", "Work in progress and internal review versions."),
        ("05_Final_Deliverables", "Approved, final versions delivered to the client."),
        ("06_Invoices", "Invoices sent, receipts, and payment records."),
        ("07_Communications", "Saved emails, meeting notes, and call summaries."),
        ("08_Archive", "Superseded or inactive material kept for reference."),
    ]
    if os.path.exists(base) and os.listdir(base) and not a.apply:
        print(f"NOTE: {base} already exists and is not empty; existing files are left alone.")
    for d, text in folders:
        readme = os.path.join(base, d, "README.txt")
        state = "exists, kept" if os.path.exists(readme) else "create"
        print(f"{d}/README.txt\t({state})\t{text}")
        if a.apply:
            os.makedirs(os.path.dirname(readme), exist_ok=True)
            if not os.path.exists(readme):
                with open(readme, "w", encoding="utf-8") as fh:
                    fh.write(text + "\n")
    print(f"\n{'DONE' if a.apply else 'DRY RUN'}: {len(folders)} folders in {base}"
          + ("" if a.apply else ". Re-run with --apply to create them."))


def cmd_apply_renames(a):
    """Plan CSV columns: old_name,new_name (names relative to folder)."""
    root = os.path.abspath(a.folder)
    with open(a.plan, newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("old_name") and r.get("new_name")]
    taken, plan = set(), []
    for r in rows:
        src = os.path.join(root, r["old_name"])
        new = r["new_name"].strip()
        if os.sep in new or (os.altsep and os.altsep in new) or new.startswith("."):
            print(f"SKIP (invalid new name)\t{r['old_name']}\t{new}")
            continue
        if not os.path.isfile(src):
            print(f"SKIP (not found)\t{r['old_name']}")
            continue
        if os.path.splitext(new)[1].lower() != os.path.splitext(src)[1].lower():
            new += os.path.splitext(src)[1]
        dst = os.path.join(os.path.dirname(src), new)
        if os.path.abspath(dst) == os.path.abspath(src):
            continue
        plan.append((src, free_name(dst, taken)))
    for s, d in plan:
        print(f"RENAME\t{os.path.relpath(s, root)}\t->\t{os.path.relpath(d, root)}")
    if not a.apply:
        print(f"\nDRY RUN: {len(plan)} file(s) would be renamed. Re-run with --apply to do it.")
        return
    log = os.path.join(root, "rename_log.csv")
    new_log = not os.path.exists(log)
    with open(log, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new_log:
            w.writerow(["timestamp", "old_name", "new_name"])
        for s, d in plan:
            if os.path.exists(d):
                d = free_name(d, set())
            os.rename(s, d)
            w.writerow([datetime.now().isoformat(timespec="seconds"),
                        os.path.relpath(s, root), os.path.relpath(d, root)])
    print(f"\nDONE: {len(plan)} file(s) renamed. Log: {log}")


def cmd_undo(a):
    """Reverse a move log (sort/archive) or rename_log.csv."""
    log = os.path.abspath(a.log)
    root = os.path.dirname(log)
    with open(log, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    plan = []
    for r in reversed(rows):
        if r.get("action") == "move":
            plan.append((r["destination"], r["source"]))
        elif "old_name" in r:
            plan.append((os.path.join(root, r["new_name"]), os.path.join(root, r["old_name"])))
        elif r.get("action") == "copy":
            sys.exit("This log records copies; the originals were never changed. "
                     "Delete the output folder instead if you want to undo.")
    problems = [s for s, d in plan if not os.path.exists(s)] + [d for s, d in plan if os.path.exists(d)]
    for s, d in plan:
        print(f"RESTORE\t{s}\t->\t{d}")
    if problems:
        print("\nCannot undo safely; these paths are missing or already occupied:")
        for p in problems:
            print(f"  {p}")
        sys.exit(1)
    if not a.apply:
        print(f"\nDRY RUN: {len(plan)} file(s) would be restored. Re-run with --apply to do it.")
        return
    emptied = set()
    for s, d in plan:
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.move(s, d)
        emptied.add(os.path.dirname(s))
    # Remove folders the original run created and that are now empty (never root itself).
    for folder in sorted(emptied, key=len, reverse=True):
        while folder.startswith(root + os.sep) and os.path.isdir(folder) and not os.listdir(folder):
            os.rmdir(folder)
            folder = os.path.dirname(folder)
    os.rename(log, log + ".undone")
    print(f"\nDONE: {len(plan)} file(s) restored. Log renamed to {log}.undone")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, *args):
        p = sub.add_parser(name)
        for spec in args:
            p.add_argument(*spec[0], **spec[1])
        p.set_defaults(fn=fn)
        return p

    apply = (["--apply"], {"action": "store_true", "help": "actually make changes"})
    folder = (["folder"], {})
    add("sort", cmd_sort, folder, apply)
    add("dupes", cmd_dupes, folder)
    add("inventory", cmd_inventory, folder)
    add("archive", cmd_archive, folder, (["--months"], {"type": int, "required": True}), apply)
    add("flatten", cmd_flatten, folder, (["output"], {}), apply)
    add("scaffold", cmd_scaffold, (["parent"], {}), (["name"], {}), apply)
    add("apply-renames", cmd_apply_renames, folder, (["plan"], {}), apply)
    add("undo", cmd_undo, (["log"], {}), apply)

    a = ap.parse_args()
    for attr in ("folder", "parent"):
        path = getattr(a, attr, None)
        if path is not None and not os.path.isdir(path):
            sys.exit(f"Not a folder: {path}")
    a.fn(a)


if __name__ == "__main__":
    main()
