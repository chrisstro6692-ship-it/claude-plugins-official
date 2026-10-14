#!/usr/bin/env python3
"""Package the file-organizer plugin as a single Claude Desktop skill ZIP.

Claude Desktop uploads skills as ZIP files and has no plugin system, so this
bundles the plugin's eight skills into one skill:

  file-organizer/
    SKILL.md              <- .github/desktop-skills/file-organizer/SKILL.md (router)
    workflows/<name>.md   <- external_plugins/file-organizer/skills/<name>/SKILL.md (body only)
    scripts/organize.py   <- external_plugins/file-organizer/scripts/organize.py

Plugin-only syntax is rewritten: ${CLAUDE_PLUGIN_ROOT} paths become "$ORG"
(set up in the router), and $ARGUMENTS lines are dropped.

Only reads the plugin; writes only the output ZIP.

Usage: python3 .github/scripts/build_desktop_skill.py [--out dist/file-organizer-skill.zip]
"""
import argparse
import glob
import os
import re
import sys
import zipfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PLUGIN = os.path.join(REPO, "external_plugins", "file-organizer")
ROUTER = os.path.join(REPO, ".github", "desktop-skills", "file-organizer", "SKILL.md")
FIXED_TIME = (2020, 1, 1, 0, 0, 0)  # stable timestamps so rebuilds give identical ZIPs


def workflow_body(skill_md):
    m = re.match(r"---\n.*?\n---\n(.*)", skill_md, re.S)
    if not m:
        raise ValueError("missing frontmatter")
    body = m.group(1)
    body = body.replace('"${CLAUDE_PLUGIN_ROOT}/scripts/organize.py"', '"$ORG"')
    body = re.sub(r"^(Folder|Arguments): \$ARGUMENTS\n\n", "", body, flags=re.M)
    body = body.replace("the Read tool", "your file-reading tool")
    body = body.replace("the Grep tool", "grep")
    if "CLAUDE_PLUGIN_ROOT" in body or "$ARGUMENTS" in body:
        raise ValueError("plugin-only syntax left after rewriting")
    return body.lstrip()


def add(zf, arcname, data, mode=0o644):
    info = zipfile.ZipInfo(arcname, FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = mode << 16
    zf.writestr(info, data)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=os.path.join(REPO, "dist", "file-organizer-skill.zip"))
    out = os.path.abspath(ap.parse_args().out)

    skills = sorted(glob.glob(os.path.join(PLUGIN, "skills", "*", "SKILL.md")))
    if not skills:
        sys.exit(f"No skills found under {PLUGIN}/skills")

    files = {"file-organizer/SKILL.md": open(ROUTER, encoding="utf-8").read()}
    for path in skills:
        name = os.path.basename(os.path.dirname(path))
        try:
            body = workflow_body(open(path, encoding="utf-8").read())
        except ValueError as e:
            sys.exit(f"{path}: {e}")
        files[f"file-organizer/workflows/{name}.md"] = body
        if f"workflows/{name}.md" not in files["file-organizer/SKILL.md"]:
            sys.exit(f"Router SKILL.md does not mention workflows/{name}.md; add it to {ROUTER}")

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with zipfile.ZipFile(out, "w") as zf:
        for arcname in sorted(files):
            add(zf, arcname, files[arcname])
        with open(os.path.join(PLUGIN, "scripts", "organize.py"), "rb") as fh:
            add(zf, "file-organizer/scripts/organize.py", fh.read(), 0o755)
    print(f"Built {out} ({len(skills)} workflows)")


if __name__ == "__main__":
    main()
