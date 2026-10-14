---
name: inventory
description: Create folder_inventory.csv listing every file in a folder and its subfolders (name, type, size, date modified, folder path), plus a one-paragraph summary of what the folder contains and is used for. Use when the user asks what is in a folder or wants a file inventory or audit.
argument-hint: "<folder path>"
allowed-tools: [Bash, Read, Write]
---

# Folder inventory

Folder: $ARGUMENTS

1. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/organize.py" inventory "<folder>"`. This only reads files. It writes `folder_inventory.csv` and prints the top file types.
2. Look at the top types, the largest files, the date range and the subfolder names (`head` or `sort` the CSV as needed). Then write a single paragraph covering:
   - which file types dominate, by count and by size
   - how recent the activity is
   - what the folder seems to be used for
3. Save the paragraph to `folder_inventory_summary.txt` next to the CSV and show it to the user. It goes in a separate file because text at the top of the CSV would stop it opening cleanly in Excel or Numbers.
