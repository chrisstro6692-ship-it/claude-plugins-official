# File Organizer

Eight workflows for tidying folders on your own computer. Each one is a skill you can call by
name, or just describe what you want ("clean up my Downloads by file type").

| Skill | What it does | Changes files? |
| --- | --- | --- |
| `/file-organizer:sort-by-type <folder>` | Sorts top-level files into Documents, Spreadsheets, Images, Presentations and Other | Moves (undoable) |
| `/file-organizer:rename-descriptive <folder>` | Reads each file and renames it `YYYY-MM-DD_Description_Client.ext`; logs to `rename_log.csv` | Renames (undoable) |
| `/file-organizer:find-duplicates <folder>` | Writes `duplicate_report.txt` (identical content, plus same name with different content) | No |
| `/file-organizer:inventory <folder>` | Writes `folder_inventory.csv` and a one-paragraph summary | No |
| `/file-organizer:project-structure <name> <parent>` | Creates `01_Contracts` to `08_Archive`, each with a README.txt | Creates folders |
| `/file-organizer:archive-old <folder> <months>` | Moves files older than N months into `Archive_<date>/`, keeping their paths | Moves (undoable) |
| `/file-organizer:find-by-content <folder> <phrase>` | Searches text, Office files and PDFs; writes `search_results.txt` | No |
| `/file-organizer:flatten <source> <output>` | Copies all nested files into one folder, prefixed with their subfolder path | Copies only |

## Safety

- **Dry run first, every time.** Claude shows you the plan and waits for your OK before it
  moves, renames or creates anything.
- **Nothing is deleted or overwritten.** A name collision becomes `name (2).ext`. The
  duplicate finder only writes a report. If you then ask Claude to remove files, they go to
  the Trash.
- **Every move and rename is logged** (`_organizer_*.csv` or `rename_log.csv`) and can be
  reversed:

  ```
  python3 <plugin>/scripts/organize.py undo "<log file>" --apply
  ```

  Or just ask Claude to undo the last change.
- Hidden files (such as `.DS_Store`) and symlinks are skipped.

## Requirements

- `python3`. It comes with Xcode Command Line Tools on macOS (`xcode-select --install`) and
  is standard on Linux. The helper uses only the standard library.
- Optional, for better PDF search: `pdftotext` (Poppler). On macOS, Spotlight is used as a
  fallback.
