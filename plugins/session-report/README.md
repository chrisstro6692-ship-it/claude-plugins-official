# Session Report

Generate an explorable HTML report of your Claude Code usage — tokens, cache
efficiency, subagents, skills, and the most expensive prompts — from the session
transcripts in `~/.claude/projects` on this machine.

## Install

```
/plugin install session-report@claude-plugins-official
```

## Use

Ask Claude for a session report, optionally with a time window:

```
/session-report          # last 7 days (default)
/session-report 24h
/session-report 30d
/session-report all
```

The report is saved as `session-report-<date>-<time>.html` in the current
directory. It's a single self-contained file: sortable tables, expandable
drill-downs, and a short list of findings and optimization suggestions written
from your actual numbers.

## What's in it

- **Totals** — input, output, and cached tokens across the window.
- **By project, subagent type, and skill** — where your tokens went.
- **Cache breaks** — places where prompt caching stopped helping.
- **Top prompts** — the single prompts that cost the most.
- **Findings** — 3–5 one-line observations (e.g. one project using a large
  share, low cache-hit rate), plus 1–4 concrete suggestions.

## Privacy

The analyzer (`analyze-sessions.mjs`) reads your local transcripts and runs on
your machine. The report file stays in your working directory; nothing is
published.
