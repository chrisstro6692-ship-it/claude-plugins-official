---
name: sort-by-type
description: Sort the files directly inside a folder into Documents, Spreadsheets, Images, Presentations, and Other subfolders by file type, then report counts per folder. Use when the user wants to tidy or clean up a folder such as Downloads or Desktop by file type.
argument-hint: "<folder path>"
allowed-tools: [Bash, Read]
---

# Sort files by type

Folder: $ARGUMENTS

Only the files at the top level of the folder are moved. Subfolders and hidden files stay where they are.

| Folder | Extensions |
| --- | --- |
| Documents | pdf, doc, docx, odt, rtf, txt, md, pages |
| Spreadsheets | xls, xlsx, xlsm, csv, tsv, ods, numbers |
| Images | jpg, jpeg, png, gif, heic, webp, bmp, tif, tiff, svg |
| Presentations | ppt, pptx, odp, key |
| Other | everything else |

1. Dry run: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/organize.py" sort "<folder>"`. Summarize the plan as counts per folder, plus any renames caused by name collisions. Show the full list only if it's short or the user asks.
2. Once the user confirms, run the same command with `--apply`.
3. Report how many files went into each folder and the path of the log.
4. Tell the user they can undo with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/organize.py" undo "<log path>" --apply`.

## Safety rules (always)

- Run the dry run first and show the user the plan. Make changes only after they confirm in this conversation.
- Never delete or overwrite a file. The helper adds " (2)" to a name that is already taken.
- If the folder path is missing, ask for it. Expand `~` and quote paths with spaces.
- If `python3` is missing (macOS: run `xcode-select --install`), tell the user rather than improvising shell moves.
