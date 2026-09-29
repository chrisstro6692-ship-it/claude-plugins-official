---
name: eli5
description: "Explain something as if to a five-year-old, using simple words and analogies"
argument-hint: "[concept]"
disable-model-invocation: true
---

Explain the input as if to a curious five-year-old.

- Short sentences, everyday words, no jargon.
- Use one vivid analogy from a child's world (toys, food, playground, animals).
- Keep it under ~150 words, then add one line starting "Grown-up version:" with the accurate one-sentence explanation.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
