---
name: setup-routing
description: Configure Claude Code to send its model requests through a local OmniRoute gateway (sets ANTHROPIC_BASE_URL in Claude Code settings), or undo that configuration. Use when the user asks to route Claude Code through OmniRoute, point Claude Code at OmniRoute, or stop routing through it.
argument-hint: "[enable|disable] [--project]"
allowed-tools: [Read, Edit, Write, Bash]
---

# Route Claude Code through OmniRoute

The user invoked this with: $ARGUMENTS

Default action is `enable`. With `--project`, write to `.claude/settings.local.json` in the
current project instead of the user-level `~/.claude/settings.json`.

## Enable

1. **Check the gateway is reachable on loopback.** Use `OMNIROUTE_URL` if set, otherwise
   `http://127.0.0.1:20128`:

   ```bash
   curl -sS -o /dev/null -w '%{http_code}\n' "${OMNIROUTE_URL:-http://127.0.0.1:20128}/v1/models" \
     -H "Authorization: Bearer $OMNIROUTE_API_KEY"
   ```

   If the connection fails, stop and tell the user to start it (`omniroute serve`). If the
   response is 401, the key is wrong or missing. Don't continue in either case.

2. **Check the gateway is hardened.** OmniRoute's shipped defaults listen on `0.0.0.0` with
   `REQUIRE_API_KEY=false`, so anyone on the same network can send requests that spend the
   user's provider credentials. Send an empty inference request *without* a key. The body is
   deliberately invalid, so no provider is called:

   ```bash
   curl -sS -o /dev/null -w '%{http_code}\n' -X POST \
     "${OMNIROUTE_URL:-http://127.0.0.1:20128}/v1/chat/completions" \
     -H 'Content-Type: application/json' --data '{}'
   ```

   Any status other than 401 means anonymous inference is allowed. In that case, warn the user and recommend these settings in `~/.omniroute/.env`,
   followed by a restart:

   ```
   OMNIROUTE_SERVER_HOST=127.0.0.1
   REQUIRE_API_KEY=true
   OMNIROUTE_MCP_ENFORCE_SCOPES=true
   ```

   Ask the user whether to continue before you go on.

3. **Never write the API key to a settings file.** Claude Code reads `ANTHROPIC_AUTH_TOKEN`
   from the environment. Tell the user to export it from their shell profile or secret
   manager, for example `export ANTHROPIC_AUTH_TOKEN="$OMNIROUTE_API_KEY"`.

4. **Back up, then merge.** Copy the target settings file to `<file>.bak-omniroute` if it
   exists. Merge only these keys into its `env` object and keep everything else as it is:

   ```json
   { "env": { "ANTHROPIC_BASE_URL": "http://127.0.0.1:20128" } }
   ```

   Use the `OMNIROUTE_URL` value instead if one is set. If the user named a model or combo,
   also set `ANTHROPIC_MODEL` to it. List the available IDs with `GET /v1/models`.

5. **Warn about an existing API key.** If `ANTHROPIC_API_KEY` is set in the shell, tell the
   user that Claude Code will send it to OmniRoute instead of the OmniRoute key, and that
   they should unset it for sessions routed through the gateway.

6. Tell the user to restart Claude Code. A new session will route through the gateway.

## Disable

Remove `ANTHROPIC_BASE_URL`, and `ANTHROPIC_MODEL` if this skill set it, from the `env` object
of the same settings file. Leave the backup in place and tell the user where it is.

## Notes for the user

- Every prompt and every file Claude Code reads goes through the gateway and on to whichever
  provider it routes to. OmniRoute also stores truncated, PII-redacted request and response
  payloads in its local SQLite database.
- OmniRoute's OAuth and web-cookie providers reuse consumer subscriptions such as Claude
  Pro/Max, ChatGPT and Copilot. OmniRoute itself warns that this is not authorized for
  proxy use and can get those accounts restricted or banned. Prefer API-key providers.
