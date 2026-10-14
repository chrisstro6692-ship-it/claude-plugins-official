# Claude Desktop MCP config

Claude Desktop doesn't install Claude Code plugins. To use the Scrapling and OmniRoute MCP
servers there, add the entries from
[`claude_desktop_config.example.json`](claude_desktop_config.example.json) to your
Claude Desktop config file, then restart Claude Desktop:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

If the file already has an `mcpServers` object, add these two entries to it. Don't replace
the whole file.

## scrapling

Matches `external_plugins/scrapling/.mcp.json` and is pinned to the same version.

- Needs [uv](https://docs.astral.sh/uv/).
- Download the browsers once:
  `uvx --from "scrapling[ai]==0.4.15" scrapling install`
- Claude Desktop may not see your shell's `PATH`. If the server fails to start, replace
  `"uvx"` with the full path from `which uvx`.
- When you upgrade, change the version here and in the plugin's `.mcp.json`.

## omniroute

Uses OmniRoute's stdio MCP server (`omniroute --mcp`), which OmniRoute documents for
Claude Desktop. It needs `npm install -g omniroute`. If Desktop can't find the command,
use the full path from `which omniroute`.

This differs from the Claude Code plugin, which connects over HTTP to a running gateway
with a scoped API key. The stdio server opens OmniRoute's local database directly and has
no API key, so the entry sets its permissions through environment variables instead:

- `OMNIROUTE_MCP_ENFORCE_SCOPES=true` turns permission checks on. They're off by default,
  which would let Claude call every tool.
- `OMNIROUTE_MCP_SCOPES` lists what Claude is allowed to do. The example allows only
  reading health, models, combos, usage, quota and the catalog.

To let Claude make changes, add scopes such as `write:combos` or `execute:completions`. The
full list is in OmniRoute's `docs/frameworks/MCP-SERVER.md`. Treat these settings as a
safety default rather than a hard security boundary: OmniRoute gives scopes sent by the
MCP client priority over this list. Read the security notes in
`external_plugins/omniroute/README.md` before you widen the scopes.

This entry hasn't been tested against a live OmniRoute install.
