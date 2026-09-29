---
name: human
description: "Rewrite text so it sounds natural and human-written, not AI-generated"
argument-hint: "[text to humanize]"
disable-model-invocation: true
---

Rewrite the input so it reads like a thoughtful person wrote it.

- Vary sentence length; use contractions and plain words.
- Cut filler and AI tells: "delve", "tapestry", "in today's fast-paced world", "it's important to note", "moreover", stacked em-dashes, rule-of-three lists, and closing summaries that restate everything.
- Prefer concrete specifics over generic claims. Keep the author's voice, meaning and facts intact; don't add new claims.
- Output only the rewritten text.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
