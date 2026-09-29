---
name: outline
description: "Create a structured, hierarchical outline for a document, talk or project"
argument-hint: "[topic] [format]"
disable-model-invocation: true
---

Create an outline for the input.

- Hierarchical headings (I / A / 1 or nested bullets), in a logical order: intro, main sections, conclusion.
- Each point gets a short phrase describing what it covers.
- Tailor it to the format named (article, talk, report, course, book); default to an article.
- Note the intended audience and core message at the top.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
