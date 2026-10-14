# OmniRoute

Connects Claude Code to a self-hosted [OmniRoute](https://github.com/diegosouzapw/OmniRoute)
AI gateway (MIT licensed). OmniRoute puts one OpenAI- and Anthropic-compatible endpoint in
front of many model providers and adds routing, fallback, and usage and cost tracking.

This plugin includes:

- **MCP server** (`omniroute`): connects to the gateway's Streamable HTTP MCP endpoint
  (`/api/mcp/stream`), which provides tools for providers, combos and routing, models, usage,
  cost, and health.
- **Skill** `/omniroute:setup-routing [enable|disable] [--project]`: points Claude Code's own
  model requests at the gateway by setting `ANTHROPIC_BASE_URL`, and can undo the change.

The plugin does not install or run OmniRoute. You run the gateway yourself.

## Setup

1. Install and start OmniRoute:

   ```bash
   npm install -g omniroute
   omniroute serve
   ```

2. **Harden the defaults before adding credentials.** The defaults are open. Out of the box
   OmniRoute listens on `0.0.0.0` and doesn't require an API key for inference, so anyone on
   your network can use your provider accounts. Add the following to `~/.omniroute/.env`
   and restart:

   ```
   OMNIROUTE_SERVER_HOST=127.0.0.1
   REQUIRE_API_KEY=true
   OMNIROUTE_MCP_ENFORCE_SCOPES=true
   OMNIROUTE_MCP_SCOPES=read:health,read:models,read:combos,read:usage,read:quota,read:catalog
   ```

   **Change the dashboard password** at `http://127.0.0.1:20128` (Settings → Security). Every
   npm install starts with the same password, `CHANGEME`, which OmniRoute itself labels
   insecure.

3. In the dashboard:
   - Enable MCP under Settings, with the transport set to `streamable-http`.
   - Create an API key with the **`manage`** scope. The MCP endpoint refuses any other key
     (`403 Invalid management token`), including read-only and `mcp:connect` keys.

   What Claude can do over MCP is set by `OMNIROUTE_MCP_SCOPES` in step 2, not by the key's
   scopes. OmniRoute 3.8.51 doesn't apply a key's scopes to MCP tool calls. With the
   settings above, Claude can read health, models, combos, usage, quota and the catalog, and
   write tools are refused. To allow changes, add scopes such as `write:combos`. If you set
   `OMNIROUTE_MCP_ENFORCE_SCOPES=true` without `OMNIROUTE_MCP_SCOPES`, every tool call
   fails.

4. Export the key and install the plugin:

   ```bash
   export OMNIROUTE_API_KEY="<your key>"
   # optional, if not on the default port
   export OMNIROUTE_URL="http://127.0.0.1:20128"
   ```

   ```
   /plugin marketplace add chrisstro6692-ship-it/claude-plugins-official
   /plugin install omniroute@chrisstro-plugins
   ```

5. Optional: run `/omniroute:setup-routing` to route Claude Code itself through the gateway.

## Routing Claude Code manually

Add this to `~/.claude/settings.json`:

```json
{ "env": { "ANTHROPIC_BASE_URL": "http://127.0.0.1:20128" } }
```

Then export `ANTHROPIC_AUTH_TOKEN="$OMNIROUTE_API_KEY"` in your shell. Unset
`ANTHROPIC_API_KEY` for routed sessions. Remove the `env` entry to stop routing.

## Security notes

These notes come from a review of OmniRoute v3.8.52 (commit `9e0a2f4`):

- **Network exposure (high).** Out of the box OmniRoute listens on `0.0.0.0` and
  `REQUIRE_API_KEY` is `false`, so anonymous inference requests from your LAN are served
  with your stored provider credentials. Apply the settings in step 2.
- **Default dashboard password.** Every npm install starts with `INITIAL_PASSWORD=CHANGEME`.
  Together with the `0.0.0.0` default, anyone on your network can log in to the dashboard
  until you change it.
- **MCP scopes aren't enforced by default.** Unless `OMNIROUTE_MCP_ENFORCE_SCOPES=true` and
  `OMNIROUTE_MCP_SCOPES` are set on the gateway, every MCP tool is callable, including the
  ones that write. Only `manage`-scoped keys can reach `/api/mcp/*`, and their own scopes
  aren't applied to tool calls (tested on 3.8.51).
- **Consumer-account providers.** OmniRoute's "free" capacity comes partly from OAuth and
  web-cookie providers that reuse subscription logins (Claude Pro/Max, ChatGPT, Copilot,
  Cursor, and others). OmniRoute's own warning says this is not authorized for proxy use and
  can get accounts restricted or banned. API-key providers don't have this risk.
- **Optional MITM mode.** The opt-in "AgentBridge" feature asks for your sudo password,
  installs a root CA, and redirects DNS for hosts such as `api.anthropic.com` to intercept
  CLI traffic. Use `ANTHROPIC_BASE_URL` instead. Its routes are loopback-only.
- **Data at rest.** Provider tokens are encrypted with AES-256-GCM, but the key is stored in
  `~/.omniroute/.env` next to the database. Call logs keep truncated (64 KB), PII-redacted
  request and response payloads.
- **Outbound traffic.** OmniRoute checks npm and GitHub for updates and release notes. Radar
  feed sync is opt-in and off by default, and cloud sync only runs when `CLOUD_URL` is set.
  Auto-update runs only when you start it.
- **Install script.** The `postinstall` script only fixes up native modules (it copies
  binaries and may run `npm rebuild better-sqlite3`). On Termux it may reinstall
  `better-sqlite3` from source instead.

Every prompt and every file Claude reads goes through the gateway, and from there to
whichever provider it routes to. Pick providers you trust with that data.
