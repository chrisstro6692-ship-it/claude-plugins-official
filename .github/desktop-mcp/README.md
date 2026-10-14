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

Claude Desktop connects to a running OmniRoute gateway through
[`mcp-remote`](https://www.npmjs.com/package/mcp-remote), pinned to 0.14.3. This uses the
same HTTP endpoint and API key as the Claude Code plugin.

1. Start the gateway (`omniroute serve`) and harden it as described in
   `external_plugins/omniroute/README.md`. In particular, change the dashboard password:
   every npm install starts with `CHANGEME`.
2. In the dashboard, turn MCP on with the `streamable-http` transport, then create an API key
   with the **`manage`** scope.
3. Replace `YOUR_OMNIROUTE_MANAGE_KEY` in the config with that key, keeping the `Bearer `
   prefix. Claude Desktop stores the key in plain text in its config file.

Needs Node.js, for `npx`. If Desktop can't find `npx`, use the full path from `which npx`.

**Access:** OmniRoute's MCP endpoint only accepts keys with the `manage` scope. In testing
against OmniRoute 3.8.51, keys with read-only scopes or `mcp:connect` were refused with
`403 Invalid management token`. A key's own scopes also aren't applied to MCP tool calls
(OmniRoute reports `source=none`). What Claude may do is therefore controlled by the
**gateway's** environment, not by the key or by this config.

Set these in `~/.omniroute/.env` and restart the gateway:

```
OMNIROUTE_MCP_ENFORCE_SCOPES=true
OMNIROUTE_MCP_SCOPES=read:health,read:models,read:combos,read:usage,read:quota,read:catalog
```

| Gateway settings | Result in testing |
| --- | --- |
| Neither setting | Every tool works, including the ones that change settings |
| `ENFORCE_SCOPES=true` only | Claude connects, but **every** tool call fails with "Insufficient MCP scopes" |
| Both settings | The read tools listed work. Write tools such as `omniroute_set_routing_strategy` are refused ("Missing: write:combos") |

To allow changes, add scopes such as `write:combos` to `OMNIROUTE_MCP_SCOPES`. The full list
is in OmniRoute's `docs/frameworks/MCP-SERVER.md`.

**Why not `omniroute --mcp`?** OmniRoute documents a stdio server for Claude Desktop, but in
the published npm package (3.8.51) it crashes on startup, because the bundled `undici`
dependency contains only its `package.json`
(`ERR_MODULE_NOT_FOUND ... dist/node_modules/undici/index.js`). Switch back if a later
release fixes it.

Tested on 2026-10-14 against a local OmniRoute 3.8.51 gateway with a `manage` key: this
entry connected, listed 99 tools, and with the gateway settings above, read calls worked and
write calls were refused. It hasn't been tested inside Claude Desktop itself.
