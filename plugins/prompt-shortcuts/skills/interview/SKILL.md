---
name: interview
description: "Prepare for an interview, or run a mock interview, for a role"
argument-hint: "[role/company] [mock]"
disable-model-invocation: true
---

Help the user prepare for an interview for the input role.

- Default: provide likely questions (behavioral, role-specific/technical, and about the company), what a strong answer covers for each, 2–3 sample STAR-format answers, and smart questions to ask the interviewer.
- If the user says "mock" or asks to practice: act as the interviewer, ask one question at a time, wait for their answer, then give specific feedback and a stronger version before the next question.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
