# agent-reach-setup

Installs [Agent-Reach](https://github.com/Panniantong/agent-reach) (MIT) on your computer
with safer defaults than its own install guide. Agent-Reach is a command-line tool that lets an
AI agent read and search the web, YouTube, GitHub and RSS without any account. With your
accounts, it adds Reddit, Twitter/X, Facebook, Instagram, LinkedIn, Bilibili, Xiaohongshu and
more.

This plugin doesn't contain Agent-Reach itself. It adds one skill that installs and manages it.

```
/plugin marketplace add chrisstro6692-ship-it/claude-plugins-official
/plugin install agent-reach-setup@chrisstro-plugins
```

Then run `/agent-reach-setup:install`, or ask Claude to "install Agent-Reach".
`/agent-reach-setup:install status` and `/agent-reach-setup:install uninstall` also work.

## What it does differently

| Agent-Reach's own guide | This plugin |
| --- | --- |
| Installs whatever is on the `main` branch | Installs a reviewed, pinned commit (`94f06c1`, v1.5.0) |
| Your agent follows `install.md` / `update.md` fetched live from GitHub | Never follows those files |
| `--system` also adds a "MUST USE for any link" skill to `~/.claude/skills/` without saying so in the preview | Warns you first, then asks whether to keep it |
| You paste exported cookies to the agent | You run the `configure` commands in your own Terminal, so cookies never enter the chat |
| Offers `--channels=all` | One channel at a time, each with its warnings |
| Suggests a daily cron job | No scheduled jobs |

The review behind these choices is in
[`skills/install/references/review.md`](skills/install/references/review.md).

## Before you enable login-based channels

They use your browser sessions or cookies, which give full access to those accounts, and the
platforms may ban accounts used this way. Use a secondary account. Per-channel notes are in
[`skills/install/references/channels.md`](skills/install/references/channels.md).

For reading ordinary web pages, the Scrapling plugin in this marketplace needs no accounts and
no third-party reader service.
