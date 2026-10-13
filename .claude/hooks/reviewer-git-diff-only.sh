#!/usr/bin/env bash
# PreToolUse (Bash) for code-reviewer: allow only plain `git diff`. Exit 2 blocks.
cmd=$(jq -r '.tool_input.command // empty')
case "$cmd" in
  "git diff"|"git diff "*) ;;
  *) echo "Blocked: code-reviewer may only run 'git diff'." >&2; exit 2 ;;
esac
# No chaining, substitution, redirects, newlines, or diff options that write files / run programs.
# Git accepts abbreviated long options, so match prefixes (--no-i, --o, --ext, --textc).
# Paths outside the repo (absolute, ~, ../) make git diff fall back to --no-index.
if [[ "$cmd" == *$'\n'* ]] || printf '%s' "$cmd" | grep -Eq \
  '[;&|`$<>(){}]|--no-i|--o|--ext|--textc|(^|[[:space:]=])(/|~)|(^|[[:space:]=/])\.\./'; then
  echo "Blocked: plain 'git diff' only (no shell operators, --no-index, --output, --ext-diff, --textconv, or paths outside the repo)." >&2
  exit 2
fi
exit 0
