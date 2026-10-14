# Optional channels: what to tell the user first

Install only the channel the user asked for. Before running
`agent-reach install --env=local --system --channels=<name>`, give them that channel's notes.

**For every login-based channel:**
- Cookies and browser sessions give full access to the account, and platforms may restrict or
  ban accounts used this way. Recommend a **secondary account**.
- The user runs any `agent-reach configure ...` command in their own Terminal. Never ask them
  to paste cookies or keys into the chat.

| Channel | Needs | Notes |
| --- | --- | --- |
| `opencli` | Chrome plus the OpenCLI extension, which the user installs by hand | Reuses the sessions already logged in to the user's Chrome. Covers Reddit, Facebook, Instagram, Twitter (as a fallback) and Xiaohongshu. Anything that can drive the extension acts as the user on those sites |
| `twitter` | Cookies exported with Cookie-Editor | User runs `agent-reach configure twitter-cookies`. Commands also need `TWITTER_AUTH_TOKEN` and `TWITTER_CT0` set in the environment |
| `reddit` | A logged-in session, through OpenCLI or `rdt-cli` | `rdt login` reads browser cookies automatically |
| `facebook`, `instagram` | OpenCLI, and logged in to Chrome | Read-only. Instagram search finds users, not posts |
| `xueqiu` | Logged in to xueqiu.com in Chrome | `agent-reach configure --from-browser chrome --platform xueqiu` reads only Xueqiu's cookies |
| `xiaohongshu` | OpenCLI on desktop, or `xiaohongshu-mcp` on a server | Never logs in on the user's behalf |
| `bilibili` | Nothing for the basics | `bili-cli` from PyPI, unpinned |
| `xiaoyuzhou` | A free Groq API key | User runs `agent-reach configure groq-key`. Podcast audio is sent to Groq for transcription |
| `linkedin` | `uv`, plus a one-time browser login | Runs `mcp-server-linkedin@latest` through `uvx`, unpinned, and stores the login in `~/.linkedin-mcp/profile/` |
| `boss` | A dedicated Chrome started with remote debugging on port 9222 | Any program on the computer can control that Chrome while it's running. Bind it to `127.0.0.1`, use a separate profile, and close it after use. Desktop only |

Don't offer `--channels=all`. If the user asks for it, list the channels and confirm each one.
