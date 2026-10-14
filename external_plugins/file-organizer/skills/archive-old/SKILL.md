---
name: archive-old
description: Move files not modified in more than N months into an Archive_YYYY-MM-DD subfolder, keeping their relative paths, with a log of every move and no deletions. Use when the user wants to archive, declutter, or set aside old or stale files.
argument-hint: "<folder path> <months>"
allowed-tools: [Bash, Read]
---

# Archive old files

Arguments: $ARGUMENTS

1. Work out the folder and the number of months. Ask if the number of months is missing; don't assume one.
2. Dry run: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/organize.py" archive "<folder>" --months <N>`. Files keep their subfolder path inside `Archive_<today>/`, so the rest of the folder structure stays as it is. Earlier `Archive_*` folders are skipped.
3. Summarize the plan: the number of files, their total size, and the oldest and newest dates.
4. Once the user confirms, run the same command with `--apply`. Report the path of the log.
5. Tell the user they can undo with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/organize.py" undo "<log path>" --apply`.

Copying files or syncing from the cloud can reset modified dates. If almost nothing qualifies, mention this possibility.

## Safety rules (always)

- Run the dry run first and show the user the plan. Make changes only after they confirm in this conversation.
- Never delete or overwrite a file. The helper adds " (2)" to a name that is already taken.
- If the folder path is missing, ask for it. Expand `~` and quote paths with spaces.
- If `python3` is missing (macOS: run `xcode-select --install`), tell the user rather than improvising shell moves.
