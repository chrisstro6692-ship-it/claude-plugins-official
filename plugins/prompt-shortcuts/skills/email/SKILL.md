---
name: email
description: "Write a clear, well-toned email ready to send"
argument-hint: "[purpose] [recipient] [tone]"
disable-model-invocation: true
---

Write an email for the input.

- Include a subject line.
- Put the purpose or ask in the first two sentences; keep it concise and skimmable.
- Match tone to the recipient and situation (default: friendly-professional).
- End with a clear next step. Use [placeholders] for any details you don't know rather than inventing them.

If no input is given, apply this to the most recent substantive content in the conversation (your last answer, or the text the user last shared).

Input: $ARGUMENTS
