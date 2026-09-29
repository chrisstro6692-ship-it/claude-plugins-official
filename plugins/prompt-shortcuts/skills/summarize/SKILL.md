---
name: summarize
description: "Summarize content into key points, takeaways and action items"
argument-hint: "[text, file or URL]"
disable-model-invocation: true
---

Summarize the input.

- One-sentence TL;DR.
- 3–7 key points as bullets, in order of importance.
- Action items or decisions, if any.
- Preserve numbers, names and dates accurately; don't add information that isn't in the source. If the input is a file path or URL, read it first.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
