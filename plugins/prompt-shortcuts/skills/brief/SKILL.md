---
name: brief
description: "Give the shortest useful answer — no preamble, no padding"
argument-hint: "[question or text]"
disable-model-invocation: true
---

Answer as briefly as possible while staying correct and useful.

- One to three sentences, or up to 5 bullets if the content is a list.
- No preamble, restating the question, caveats that don't change the answer, or closing offers.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
