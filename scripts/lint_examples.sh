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
for f in sessions/*/smt2/*.smt2 sessions/*/python/*.py sessions/*/smv/*.smv \
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
for base in $(grep -rhoE '"[0-9]{2}_[a-z0-9_]+\.(smt2|py|smv)"' notebooks/ | tr -d '"' | sort -u); do
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

# THE STATE-MACHINE RULE. A transition-system example shown in slides or Colab
# always comes with a graph of its state machine -- guards and updates on the
# edges when it has data variables. Every SMV model must declare one with a
# header line  `-- FIGURE: figures/<name>.svg`  (Python / SMT-LIB examples of a
# transition system use `# FIGURE:` / `; FIGURE:`), the figure must exist, and
# the session's notebook must display it. Figures are drawn by
# scripts/draw_models.py. Homework starters are exempt on purpose: HW2 Part 1
# asks students to derive the transition relation themselves.
for f in sessions/*/smv/*.smv; do
  [[ -e "$f" ]] || continue
  grep -qE '^\s*--\s*FIGURE:' "$f" || { echo "!! $f is a transition system with no FIGURE: header (draw it: scripts/draw_models.py)" >&2; fail=1; }
done
for f in $(grep -lE '^\s*(--|;|#)\s*FIGURE:' sessions/*/smv/*.smv sessions/*/python/*.py sessions/*/smt2/*.smt2 2>/dev/null); do
  sess="${f#sessions/}"; sess="${sess%%/*}"
  fig=$(grep -m1 -oE 'FIGURE:\s*\S+' "$f" | sed -E 's/FIGURE:\s*//')
  [[ -f "sessions/$sess/$fig" ]] || { echo "!! $f declares $fig, which does not exist" >&2; fail=1; continue; }
  grep -qF "$(basename "$fig")" "notebooks/$sess.ipynb" 2>/dev/null \
    || { echo "!! notebooks/$sess.ipynb never displays $(basename "$fig") (declared by $f)" >&2; fail=1; }
done

# Instructor-only solutions live in the private instructor repo and carry this
# marker. This repository is public: refuse any file that has it.
if grep -rlI --exclude-dir=.git -e "INSTRUCTOR ONLY" -E -e "HW[0-9]+ SOLUTION" . | grep -v "^./scripts/lint_examples.sh$" | grep -q .; then
  grep -rlI --exclude-dir=.git -e "INSTRUCTOR ONLY" -E -e "HW[0-9]+ SOLUTION" . | grep -v "^./scripts/lint_examples.sh$" | sed 's/^/!! solution marker in a PUBLIC repo: /' >&2
  fail=1
fi

echo
[[ $fail -eq 0 ]] && echo "PASSED — $n example(s), all wired to a notebook and all contracted" \
                  || echo "FAILED" >&2
exit $fail
