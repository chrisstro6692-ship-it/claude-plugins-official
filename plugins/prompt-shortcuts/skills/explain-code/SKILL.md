---
name: explain-code
description: "Explain what a piece of code does, how it works, and any gotchas"
argument-hint: "[code, file or function]"
disable-model-invocation: true
---

Explain the input code.

- Start with a one-paragraph summary of what it does and why.
- Walk through how it works, section by section, in execution order.
- Call out non-obvious parts: tricky logic, side effects, performance characteristics, and potential bugs or edge cases.
- Match depth to the code: brief for small snippets, structured with headings for large files. If given a file path or name, read it first.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
