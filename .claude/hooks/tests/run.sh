#!/usr/bin/env bash
# Runs block-rm-rf.cases against ../block-rm-rf.sh. Exits 1 if any case fails.
# Usage: bash .claude/hooks/tests/run.sh
here=$(cd "$(dirname "$0")" && pwd)
hook="$here/../block-rm-rf.sh"
pass=0 fail=0
while IFS= read -r line; do
  [[ -z $line || $line == \#* ]] && continue
  expect=${line%% *} c=${line#* }
  jq -n --arg c "$c" '{tool_input:{command:$c}}' | "$hook" 2>/dev/null
  got=$?
  case $expect in
    BLOCK) want=2 ;;
    ALLOW|GAP) want=0 ;;
    *) echo "bad label: $line"; fail=$((fail + 1)); continue ;;
  esac
  if [[ $got == "$want" ]]; then
    pass=$((pass + 1))
  else
    echo "FAIL ($expect, got exit $got): $c"
    fail=$((fail + 1))
  fi
done < "$here/block-rm-rf.cases"
echo "block-rm-rf: $pass passed, $fail failed"
((fail == 0))
