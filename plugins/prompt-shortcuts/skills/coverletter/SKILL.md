---
name: coverletter
description: "Write a tailored cover letter matching experience to a job"
argument-hint: "[job description] [resume or background]"
disable-model-invocation: true
---

Write a cover letter from the input.

- Tailor it to the specific role and company: mirror the top 3 requirements and match each to concrete evidence from the candidate's background, with results where available.
- Structure: strong opening hook, 2–3 body paragraphs, confident close with a call to action. Keep it under one page (~250–400 words).
- Don't invent experience, employers or numbers. Use [placeholders] for missing details and list what the user should fill in.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
