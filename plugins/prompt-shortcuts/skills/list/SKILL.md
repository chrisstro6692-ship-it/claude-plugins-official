---
name: list
description: "Format the answer or content as a clear, well-organized list"
argument-hint: "[topic or content]"
disable-model-invocation: true
---

Present the input as a clean list.

- Use a numbered list if order or ranking matters, bullets otherwise.
- One idea per item, parallel phrasing, bold lead-in words when items have explanations.
- Group into sections with headings if there are more than ~10 items.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
