---
name: simplify
description: "Rewrite text in plain language that anyone can understand"
argument-hint: "[text]"
disable-model-invocation: true
---

Rewrite the input in plain language.

- Short sentences, common words, active voice; define or replace jargon.
- Keep all the important meaning — simplify the wording, not the facts.
- Aim for roughly an 8th-grade reading level unless the user says otherwise.
- Output only the simplified text.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
