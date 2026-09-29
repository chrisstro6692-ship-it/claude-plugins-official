---
name: promptengineer
description: "Turn a rough request into a clear, effective prompt for an AI model"
argument-hint: "[rough prompt or goal]"
disable-model-invocation: true
---

Rewrite the input into a high-quality prompt for an AI model.

The improved prompt should include, where relevant: role/context, the task stated clearly, relevant background and constraints, the desired output format and length, examples, and success criteria.

Output:
1. The improved prompt in a code block, ready to copy.
2. Brief notes on what you changed and why.
3. Any missing information the user should fill in (marked as [placeholders] in the prompt).

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
