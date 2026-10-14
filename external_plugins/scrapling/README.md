# Scrapling

Runs the [Scrapling](https://github.com/D4Vinci/Scrapling) MCP server (BSD-3-Clause) on your
machine over stdio. It gives Claude 13 web-scraping tools:

| Tool | What it does |
| --- | --- |
| `make_request`, `bulk_get` | Fast HTTP requests with browser TLS impersonation (GET/POST/PUT/DELETE) |
| `fetch`, `bulk_fetch` | Render the page in Chromium, for JavaScript-heavy sites |
| `stealthy_fetch`, `bulk_stealthy_fetch` | Stealth browser for sites with anti-bot protection |
| `open_session`, `open_request_session`, `session_fetch`, `session_make_request`, `list_sessions`, `close_session` | Keep a browser or HTTP session open across calls (cookies, logins) |
| `screenshot` | Capture a page |

Results come back as Markdown, or as only the elements matching a CSS selector, which keeps
token use low.

## Requirements

- [uv](https://docs.astral.sh/uv/). The plugin launches the server with
  `uvx --from "scrapling[ai]==0.4.15" scrapling-mcp`, so you don't need a virtualenv.
- A one-time browser download, needed only by the browser-based tools:

  ```bash
  uvx --from "scrapling[ai]==0.4.15" scrapling install
  ```

  This runs `playwright install chromium` and, on Linux, `playwright install-deps`, which may
  ask for sudo.

Then install the plugin:

```
/plugin marketplace add chrisstro6692-ship-it/claude-plugins-official
/plugin install scrapling@chrisstro-plugins
```

## Using your own install instead

If you already have Scrapling in a virtualenv, you can register it directly instead of using
this plugin:

```bash
claude mcp add -s user ScraplingServer "$HOME/.venv/bin/scrapling-mcp"
```

Don't use both, or Claude will see two copies of every tool.

## Notes

- The version is pinned to 0.4.15. To upgrade, change the version in `.mcp.json` and rerun
  `scrapling install`.
- The server can fetch any URL your machine can reach, including `localhost` and hosts on
  your private network. Keep that in mind when you ask Claude to scrape pages that might
  contain instructions aimed at it. Scrapling strips hidden content and keeps only the main
  content by default (`main_content_only=true`) to reduce prompt-injection risk.
- The stealth tools are designed to get past bot protection. You are responsible for
  following each site's terms of service and robots rules.
