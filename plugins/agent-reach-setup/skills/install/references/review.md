# Agent-Reach review notes

Reviewed commit `94f06c1969dfc1834001269d79d3ad0972d9dee6` (v1.5.0, 2026-10-08), MIT
licensed, about 9,400 lines of Python, shell scripts and Markdown. Checked on 2026-10-14 by
reading the source and running the installer in a throwaway home folder.

## Good

- **Safe default.** `agent-reach install` with no `--system` only checks. In testing, check-only
  mode and `--system --dry-run` both changed no files.
- **No shell injection.** All 27 `subprocess` calls in the package use argument lists, with no
  `shell=True`, `os.system` or `curl | sh`.
- **Scoped cookie reading.** `cookie_extract.py` reads only each platform's own domains
  (`.x.com`/`.twitter.com`, `.xiaohongshu.com`, `.bilibili.com`, `.xueqiu.com`), from the
  browser the user names.
- **Private config files.** Secrets in `~/.agent-reach/` are written with mode `0600`, in a
  `0700` folder.
- **No telemetry.** Its outbound calls go to the platforms themselves, GitHub (for update
  checks), Jina Reader, Exa, and Groq or OpenAI for podcast transcription.
- **Upstream packages check out.** `twitter-cli`, `bilibili-cli` and `@jackwener/opencli`
  are published by the same upstream author (jackwener), and `mcporter` by openclaw. The
  `rdt-cli` and `boss-agent-cli` sources are pinned to commits.

## Risks this plugin works around

| Risk | What this plugin does |
| --- | --- |
| The official install line uses `archive/main.zip`, so whatever is on `main` at that moment gets installed | Installs the reviewed commit only |
| `install.md` and `update.md` are instructions for an AI agent, fetched live from `main`. Whoever controls that branch can change what your agent is told to do | The skill never follows them |
| `--system` copies a skill into `~/.claude/skills/agent-reach` whose description says "MUST USE" for any web research or link. The dry run doesn't mention this | The skill warns first, then asks whether to keep it |
| `--system` runs `npm install -g` for unpinned latest versions of `mcporter`, `undici` and `@jackwener/opencli`, and installs `twitter-cli` and `bilibili-cli` from PyPI unpinned | The skill tells the user before running it |
| Web pages are read through Jina Reader and searches go through Exa, both third parties | The skill tells the user |
| Social channels use the user's own logged-in sessions or cookies, and platforms may ban accounts for it | See `channels.md`. One channel at a time, on request only, with a secondary account recommended |
| The OpenClaw guide suggests a daily cron job | The skill never creates scheduled jobs |
