---
name: project-structure
description: Create a standard client or project folder (01_Contracts, 02_Briefs, 03_Research, 04_Drafts, 05_Final_Deliverables, 06_Invoices, 07_Communications, 08_Archive), each with a one-line README.txt. Use when the user starts a new client, project, or engagement and wants a folder structure.
argument-hint: "<client or project name> <parent folder path>"
allowed-tools: [Bash]
---

# Client / project folder structure

Arguments: $ARGUMENTS

1. Work out the client or project name and the parent folder. Ask if either is missing.
2. Preview: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/organize.py" scaffold "<parent folder>" "<name>"`
3. Once the user confirms, run the same command with `--apply`. If the folder already exists, existing files and READMEs are kept and only missing folders are added.
4. Report the path that was created.
