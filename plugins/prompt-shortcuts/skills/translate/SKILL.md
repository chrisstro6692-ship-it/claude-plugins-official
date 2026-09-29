---
name: translate
description: "Translate text naturally into a target language, preserving tone and meaning"
argument-hint: "[target language] [text]"
disable-model-invocation: true
---

Translate the input.

- Target language: the one the user names; if none, translate into English (or from English into the language the user has been writing in).
- Translate meaning and tone, not word-for-word; adapt idioms naturally and keep formatting.
- Output the translation, then a short note on any ambiguous phrases or cultural adaptations you made.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
