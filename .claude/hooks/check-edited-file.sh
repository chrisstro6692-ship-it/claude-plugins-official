#!/usr/bin/env bash
# PostToolUse (Edit|Write): validate the file Claude just edited.
# Exit 2 sends stderr back to Claude so it fixes the problem.
f=$(jq -r '.tool_input.file_path // empty')
[ -f "$f" ] || exit 0
case "$f" in
  *.json)
    out=$(jq empty "$f" 2>&1) || { echo "Invalid JSON in $f: $out" >&2; exit 2; } ;;
  */SKILL.md|*/agents/*.md|*/commands/*.md)
    out=$(bun "$CLAUDE_PROJECT_DIR/.github/scripts/validate-frontmatter.ts" "$f" 2>&1) \
      || { echo "$out" >&2; exit 2; } ;;
esac
exit 0
