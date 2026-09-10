#!/usr/bin/env bash
# Scaffold a session folder and its notebook, named to match the slide deck.
#
#   bash scripts/new_session.sh 2026-09-17-sat-solving-and-refutation
#
# The folder name is the slide filename without the `cs3892-` prefix and the
# extension, so `sessions/` sorts by date and every folder is unambiguous about
# which lecture it belongs to.
set -euo pipefail

[[ $# -eq 1 ]] || { echo "usage: $0 YYYY-MM-DD-slug" >&2; exit 2; }
slug="cs3892-$1"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
d="$ROOT/sessions/$slug"
[[ -e "$d" ]] && { echo "$d already exists" >&2; exit 1; }

mkdir -p "$d/smt2" "$d/python"
cat > "$d/README.md" <<MD
# $slug

Worked examples for the lecture of the same name.

| File | Shows | Verdict |
|---|---|---|
| | | |

Run them all:

\`\`\`bash
bash scripts/check_examples.sh sessions/$slug
\`\`\`
MD

cat > "$d/smt2/01_example.smt2" <<'MD'
; EXPECT: unsat
; What this shows, and which slide it is on.

(declare-const p Bool)
(assert (and p (not p)))
(check-sat)
MD

cat > "$d/python/01_example.py" <<'MD'
"""What this shows, and which slide it is on.

Expected: unsat.
"""

from z3 import Bool, And, Not, Solver, unsat

p = Bool("p")
s = Solver()
s.add(And(p, Not(p)))

print(s.check())
assert s.check() == unsat, "expected unsat"
MD

echo "created $d"
echo
echo "Next:"
echo "  1. write the examples, each .smt2 with a '; EXPECT:' header line"
echo "  2. copy notebooks/<a previous session>.ipynb to notebooks/$slug.ipynb"
echo "     and point its SESSION constant at '$slug'"
echo "  3. bash scripts/check_examples.sh sessions/$slug"
echo "  4. bash scripts/lint_examples.sh   # fails until the notebook lists them"
