"""Session 25 -- an LLM writes VNN-LIB from English; a checker, not the reader, decides if it is right.

Three English properties of the toy network went to Claude Haiku 4.5 (llm/run.md: no tools, an
empty directory, one attempt, saved verbatim). This script extracts the three VNN-LIB files from the
saved reply, parses them with HW5's own parser (sized here for 2 inputs and 2 outputs), and compares
each against a reference written by hand: the input box, and the counterexample region. Then the
exact MILP decides each property.

This time the files are right. The reply's prose is not: for Q3 it says, in one comment, that a gap
of exactly 0.4 is flagged as a violation and, at the end, that it is acceptable. The file follows the
first reading. Read the file, not the explanation, and check the file mechanically.

Expected: the assertions at the bottom hold.
"""
import re
import sys
from pathlib import Path

import numpy as np

import milp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "homework" / "hw5-nn-verification"))
import hw5lib  # noqa: E402

hw5lib.N_IN, hw5lib.N_OUT = 2, 2           # HW5's parser, sized for the toy network

REPLY = (HERE.parent / "llm" / "response.txt").read_text()
files = re.findall(r"```(?:[a-z]*)\n(.*?)```", REPLY, re.S)
assert len(files) == 3, len(files)


def ref(lo, hi, out):
    decl = "".join(f"(declare-const {v} Real)\n" for v in ("X_0", "X_1", "Y_0", "Y_1"))
    box = "".join(f"(assert (>= X_{i} {lo[i]})) (assert (<= X_{i} {hi[i]}))\n" for i in range(2))
    return decl + box + out


REFERENCE = {   # the counterexample region each English property describes
    "Q1": ref((0.35, 0.45), (0.55, 0.65), "(assert (>= Y_1 Y_0))"),
    "Q2": ref((0.6, 0.1), (0.8, 0.3), "(assert (>= Y_1 Y_0))"),
    "Q3": ref((0.25, 0.25), (0.35, 0.35), "(assert (<= Y_0 (+ Y_1 0.4)))"),
}
for (name, want_txt), got_txt in zip(REFERENCE.items(), files):
    got, want = hw5lib.parse_vnnlib(got_txt), hw5lib.parse_vnnlib(want_txt)
    diffs = hw5lib.compare_specs(got, want)
    status, m, _ = milp.solve(got.lo, got.hi)
    print(f"{name}: box {np.round(got.lo, 2).tolist()} .. {np.round(got.hi, 2).tolist()};"
          f" differences from the reference: {diffs or 'none'}")
    print(f"     min margin y0 - y1 over the box {m:+.2f}")
    assert diffs == [], (name, diffs)
assert "flags gaps < 0.4 and exactly = 0.4" in REPLY and "treats a gap of exactly 0.4 as acceptable" in REPLY
print("\nall three files match the references; Q3's prose contradicts itself about the boundary")
