#!/usr/bin/env bash
# PreToolUse (Bash): block recursive force deletes. Exit 2 blocks the call.
command -v jq >/dev/null || { echo "Blocked: jq is required by the rm guard hook." >&2; exit 2; }
cmd=$(jq -r '.tool_input.command // empty')

# Split on shell separators, drop quotes/backslashes, then check every rm call
# (rm, /bin/rm, \rm, "rm", sudo/xargs/find -exec rm) for -r and -f anywhere after it.
segments=$(printf '%s' "$cmd" | tr ';&|()`' '\n\n\n\n\n\n' | tr -d "\"'\\\\")
while read -r -a words; do
  for ((i = 0; i < ${#words[@]}; i++)); do
    [[ "${words[i]##*/}" == rm ]] || continue
    r=0 f=0
    for w in "${words[@]:i+1}"; do
      [[ $w == -- ]] && break
      # A $-argument (rm $x, rm $'-rf') could expand to flags; require `rm -- "$var"`.
      [[ $w == *\$* ]] && { echo "Blocked: rm with a \$-argument before '--'. Use: rm -- \"\$var\"" >&2; exit 2; }
      case $w in
        --r*) r=1 ;;            # --recursive (rm accepts abbreviations)
        --f*) f=1 ;;            # --force
        --*) ;;
        -*) [[ $w == *[rR]* ]] && r=1; [[ $w == *f* ]] && f=1 ;;
      esac
    done
    if ((r && f)); then
      echo "Blocked: rm -rf is not allowed in this repo. Ask the user to run it." >&2
      exit 2
    fi
  done
done <<< "$segments"
exit 0
