#!/usr/bin/env bash
# PostToolUse (Edit|Write): validate the file Claude just edited.
# Exit 2 sends stderr back to Claude so it fixes the problem.
command -v jq >/dev/null || { echo "check-edited-file: jq not installed; edit checks skipped" >&2; exit 1; }
f=$(jq -r '.tool_input.file_path // empty')
[ -f "$f" ] || exit 0
case "$f" in
  *.json)
    out=$(jq empty "$f" 2>&1) || { echo "Invalid JSON in $f: $out" >&2; exit 2; } ;;
  */SKILL.md|*/agents/*.md|*/commands/*.md)
    if [[ $f == */SKILL.md ]]; then
      dir=$(basename "$(dirname "$f")")
      name=$(sed -n '2,/^---$/s/^name:[[:space:]]*//p' "$f" | head -1 | tr -d "\"'")
      [ -n "$name" ] && [ "$name" != "$dir" ] && { echo "SKILL.md name '$name' must match its folder '$dir'" >&2; exit 2; }
    fi
    command -v bun >/dev/null || exit 0   # no bun: skip rather than block a fine file
    out=$(bun "$CLAUDE_PROJECT_DIR/.github/scripts/validate-frontmatter.ts" "$f" 2>&1)
    rc=$?
    # Block only on real validation errors (the validator ran and printed its summary).
    # A setup failure (e.g. yaml not installed) is reported but never blocks.
    if [ $rc -ne 0 ] && printf '%s' "$out" | grep -q '^Validated '; then
      echo "$out" >&2; exit 2
    elif [ $rc -ne 0 ]; then
      echo "Frontmatter check could not run (not blocking): $out" >&2
    fi ;;
esac
exit 0
