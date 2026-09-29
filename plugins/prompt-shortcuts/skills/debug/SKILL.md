---
name: debug
description: "Find the root cause of a bug or error and propose a fix"
argument-hint: "[error, code or symptom]"
disable-model-invocation: true
---

Debug the input.

1. Restate the symptom and the expected behavior.
2. Identify the most likely root cause, pointing at the exact line(s) or condition; list other candidates if uncertain.
3. Give the fix as corrected code or a diff.
4. Explain why it failed and how to verify the fix (and, if useful, a test that would have caught it).

If you have access to the code and a shell, reproduce the problem and verify the fix rather than guessing.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
