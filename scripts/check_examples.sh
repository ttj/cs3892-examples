#!/usr/bin/env bash
# Run every example in every session folder and check it against its own
# recorded expectation. This is what CI runs, and it is what you should run
# before pushing.
#
#   bash scripts/check_examples.sh                     # everything
#   bash scripts/check_examples.sh sessions/cs3892-2026-09-10-*   # one session
#
# .smt2  -- verdict must match the `; EXPECT:` line in the file header.
# .py    -- must exit 0. Each script asserts its own result, so a wrong answer
#           is an AssertionError rather than a silently different number.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${PYTHON:-python3}"
cd "$ROOT"

targets=("$@")
[[ ${#targets[@]} -eq 0 ]] && targets=(sessions/*/)

fail=0; n=0
for d in "${targets[@]}"; do
  d="${d%/}"
  [[ -d "$d" ]] || { echo "no such session: $d" >&2; fail=1; continue; }
  echo "== $d"

  for f in "$d"/smt2/*.smt2; do
    [[ -e "$f" ]] || continue
    n=$((n+1))
    if ! "$PY" scripts/run_smt2.py "$f"; then fail=1; fi
  done

  for f in "$d"/python/*.py; do
    [[ -e "$f" ]] || continue
    n=$((n+1))
    echo "$f:"
    if out=$("$PY" "$f" 2>&1); then
      echo "$out" | sed 's/^/  /'
      echo "  ok"
    else
      echo "$out" | sed 's/^/  /'
      echo "  !! FAILED" >&2
      fail=1
    fi
  done
done

echo
if [[ $fail -eq 0 ]]; then
  echo "PASSED — $n example(s), every verdict as recorded"
else
  echo "FAILED" >&2
fi
exit $fail
