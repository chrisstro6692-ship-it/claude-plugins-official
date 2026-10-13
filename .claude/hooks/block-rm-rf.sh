#!/usr/bin/env bash
# PreToolUse (Bash): block recursive force deletes. Exit 2 blocks the call.
command -v jq >/dev/null || { echo "Blocked: jq is required by the rm guard hook; all Bash is blocked until jq is installed." >&2; exit 2; }
cmd=$(jq -r '.tool_input.command // empty')

# A: command substitution in command position ($(echo rm) -rf, `echo rm` -rf) hides what runs.
if printf '%s' "$cmd" | grep -Eq '(^|[;&|(`])[[:space:]]*(\$\(|`)'; then
  echo "Blocked: command name comes from a substitution; write the command out literally." >&2
  exit 2
fi

# Split on shell separators, drop quotes/backslashes, then check every rm call
# (rm, /bin/rm, \rm, "rm", sudo/xargs/find -exec rm) for -r and -f anywhere after it.
segments=$(printf '%s' "$cmd" | tr ';&|()`' '\n\n\n\n\n\n' | tr -d "\"'\\\\")
while read -r -a words; do
  # B: the command word (first non-assignment word) must not contain $ ($x, rm${IFS}-rf).
  for w in "${words[@]}"; do
    [[ $w =~ ^[A-Za-z_][A-Za-z0-9_]*= ]] && continue
    [[ $w == *\$* ]] && { echo "Blocked: command name contains \$ ($w); write the command out literally." >&2; exit 2; }
    # C: braces/globs in the command word ({rm,-rf,x}, /bin/r[m]) hide what runs.
    # Bare { (group), [ and [[ (test commands) are fine.
    [[ $w != "{" && $w != "[" && $w != "[[" && $w == *[\{\[\?\*]* ]] && { echo "Blocked: braces or globs in the command name ($w)." >&2; exit 2; }
    break
  done
  for ((i = 0; i < ${#words[@]}; i++)); do
    [[ "${words[i]##*/}" == rm ]] || continue
    r=0 f=0
    for w in "${words[@]:i+1}"; do
      [[ $w == -- ]] && break
      # A $-argument (rm $x, rm $'-rf') could expand to flags; require `rm -- "$var"`.
      [[ $w == *\$* ]] && { echo "Blocked: rm with a \$-argument before '--'. Use: rm -- \"\$var\"" >&2; exit 2; }
      # Brace expansion can produce flags (rm {-r,-f} x) when an alternative starts with '-'.
      [[ $w == *\{* && $w == *[\{,]-* ]] && { echo "Blocked: rm with a {brace} argument that can expand to a flag." >&2; exit 2; }
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
