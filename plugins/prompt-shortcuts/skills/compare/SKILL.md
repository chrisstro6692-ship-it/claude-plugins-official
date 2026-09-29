---
name: compare
description: "Compare options side by side and give a recommendation"
argument-hint: "[option A] vs [option B] ..."
disable-model-invocation: true
---

Compare the options in the input.

- Pick the 5–8 criteria that matter most for this decision.
- Show a side-by-side markdown table.
- Summarize key differences, when each option is the better choice, and a recommendation (stating assumptions about the user's needs).
- Be accurate and fair; flag anything that may be out of date.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
