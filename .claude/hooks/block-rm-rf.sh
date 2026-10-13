#!/usr/bin/env bash
# PreToolUse (Bash): block recursive force deletes. Exit 2 blocks the call.
cmd=$(jq -r '.tool_input.command // empty')
if printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])rm[[:space:]]+(-[[:alnum:]]*[rR][[:alnum:]]*f|-[[:alnum:]]*f[[:alnum:]]*[rR]|(-[rR]|--recursive)[[:space:]]+(-f|--force)|(-f|--force)[[:space:]]+(-[rR]|--recursive))'; then
  echo "Blocked: rm -rf is not allowed in this repo. Ask the user to run it." >&2
  exit 2
fi
exit 0
