---
name: find-duplicates
description: Scan a folder and its subfolders for duplicate files and write duplicate_report.txt listing originals, duplicates, and sizes, without deleting anything. Use when the user wants to find duplicates, free up space, or clean up copies.
argument-hint: "<folder path>"
allowed-tools: [Bash, Read]
---

# Find duplicates (safe mode)

Folder: $ARGUMENTS

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/organize.py" dupes "<folder>"`. It compares SHA-256 hashes of every file, including subfolders, and writes `duplicate_report.txt` in the folder. The report has two sections:
   - **Identical content:** byte-for-byte copies. The oldest copy is listed as the original.
   - **Same name, different content:** usually different versions of a file, not duplicates. Say clearly that these are *not* safe to delete.
2. Summarize: the number of groups, the space that could be reclaimed, and the 5 largest groups.
3. **Do not delete anything.** If the user then names files to remove, repeat the exact list back and ask them to confirm. Then move those files to the system Trash rather than deleting them permanently: on macOS, `osascript -e 'tell application "Finder" to delete POSIX file "<path>"'`; elsewhere, `gio trash <path>` or `trash <path>`. If none of those is available, ask the user before using `rm`.

## Safety rules (always)

- Run the dry run first and show the user the plan. Make changes only after they confirm in this conversation.
- Never delete or overwrite a file. The helper adds " (2)" to a name that is already taken.
- If the folder path is missing, ask for it. Expand `~` and quote paths with spaces.
- If `python3` is missing (macOS: run `xcode-select --install`), tell the user rather than improvising shell moves.
