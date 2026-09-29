---
name: research
description: "Research a topic thoroughly and report findings with sources and confidence"
argument-hint: "[topic or question]"
disable-model-invocation: true
---

Research the input topic and report what you find.

- If web search or other tools are available, use them and cite sources with links; prefer primary and recent sources.
- If no tools are available, say you're answering from training knowledge, which may be out of date.
- Report: a short answer, key findings (with sources), where sources disagree, open questions, and your confidence level.
- Separate established facts from opinions and speculation. Never fabricate citations.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
