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
   ```

   Then set a dashboard password at `http://127.0.0.1:20128`.

3. In the dashboard:
   - Create an API key. Give it only the MCP scopes you want Claude to use. Read-only
     scopes are a reasonable start.
   - Enable MCP under Settings, with the transport set to `streamable-http`.

4. Export the key and install the plugin:

   ```bash
   export OMNIROUTE_API_KEY="<your key>"
   # optional, if not on the default port
   export OMNIROUTE_URL="http://127.0.0.1:20128"
   ```

   ```
   /plugin install omniroute@claude-plugins-official
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
- **MCP scopes aren't enforced by default.** Unless `OMNIROUTE_MCP_ENFORCE_SCOPES=true`,
  every API key can call all of the gateway's MCP tools, including the ones that write.
  `/api/mcp/*` is loopback-only unless a key has the `manage` scope.
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
