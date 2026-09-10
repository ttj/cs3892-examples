#!/usr/bin/env bash
# Every example file must be reachable two ways: run by check_examples.sh (which
# globs, so that is automatic) and *referenced from a notebook*, which is not.
#
# This catches the one failure mode that merges cleanly and still breaks the
# course: you add an example, wire it into CI, and forget the notebook -- so the
# Colab link a student clicks from the slides quietly lacks it.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail=0; n=0
for f in sessions/*/smt2/*.smt2 sessions/*/python/*.py \
         homework/*/smt2/*.smt2 homework/*/python/*.py; do
  [[ -e "$f" ]] || continue
  n=$((n+1))
  base="$(basename "$f")"
  if ! grep -rqF "$base" notebooks/; then
    echo "!! $f is in no notebook — a student clicking the Colab link never sees it" >&2
    fail=1
  fi
done

# ...and the reverse: a notebook must not reference a file that no longer exists.
for base in $(grep -rhoE '"[0-9]{2}_[a-z0-9_]+\.(smt2|py)"' notebooks/ | tr -d '"' | sort -u); do
  if ! find sessions homework -name "$base" 2>/dev/null | grep -q .; then
    echo "!! notebooks reference $base, which does not exist" >&2
    fail=1
  fi
done

# Every .smt2 must carry its own expected verdict.
for f in sessions/*/smt2/*.smt2 homework/*/smt2/*.smt2; do
  [[ -e "$f" ]] || continue
  grep -qE '^\s*;\s*EXPECT:\s*(sat|unsat|unknown)\s*$' "$f" || {
    echo "!! $f has no '; EXPECT:' contract in its header" >&2; fail=1; }
done

echo
[[ $fail -eq 0 ]] && echo "PASSED — $n example(s), all wired to a notebook and all contracted" \
                  || echo "FAILED" >&2
exit $fail
