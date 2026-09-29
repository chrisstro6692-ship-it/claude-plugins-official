---
name: code
description: "Write clean, working code for a task with brief usage notes"
argument-hint: "[what to build] [language]"
disable-model-invocation: true
---

Write code for the input task.

- If you're in a project, match its language, style and conventions; otherwise pick the most suitable language (or the one named).
- Produce complete, working, readable code with sensible error handling — no placeholders for core logic.
- Briefly explain how to run or use it and any dependencies.
- State any assumptions you made about unclear requirements.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
