#!/usr/bin/env bash
# PreToolUse (Bash) for code-reviewer: allow only plain `git diff`. Exit 2 blocks.
cmd=$(jq -r '.tool_input.command // empty')
case "$cmd" in
  "git diff"|"git diff "*) ;;
  *) echo "Blocked: code-reviewer may only run 'git diff'." >&2; exit 2 ;;
esac
# No chaining, substitution, redirects, newlines, or diff options that write files / run programs.
if [[ "$cmd" == *$'\n'* ]] || printf '%s' "$cmd" | grep -Eq '[;&|`$<>(){}]|--output|--ext-diff|--textconv'; then
  echo "Blocked: plain 'git diff' only (no shell operators, --output, --ext-diff, --textconv)." >&2
  exit 2
fi
exit 0
