---
name: flatten
description: Copy every file from a deeply nested folder into one flat output folder, prefixing each file name with its original subfolder path so its origin is traceable. The source folder is never changed. Use when the user wants to flatten, consolidate, or collect files from many subfolders into one place.
argument-hint: "<source folder> <output folder>"
allowed-tools: [Bash]
---

# Flatten a nested folder

Arguments: $ARGUMENTS

1. Work out the source and output folders. The output must be outside the source; the helper refuses otherwise. Ask if the output folder is missing, and suggest `<source>_flat` next to it.
2. Dry run: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/organize.py" flatten "<source>" "<output>"`. Each file gets its subfolder path as a prefix, with `__` as the separator. For example, `Clients/Acme/2024/invoice.pdf` becomes `Clients__Acme__2024__invoice.pdf`.
3. Before copying, check there's enough free space with `du -sh` on the source and `df -h` on the output.
4. Once the user confirms, run the same command with `--apply`. Report the number of files copied and the log path.
5. Remind the user that the original folder is untouched.
