"""HW3 Part 2b -- try loop invariants on c/converge.c with CBMC's loop contracts.

    python3 hw3_part2_converge.py "your invariant"      e.g.  "i <= j"
    python3 hw3_part2_converge.py                       (the placeholder INV = 1)

It compiles converge.c with -DINV="...", applies the loop contract, runs CBMC with --trace,
and prints the three checks: the invariant holds on entry; one iteration preserves it;
the assertion after the loop. If one fails, it prints the values of i and j in the
trace. Read them: they are the counterexample.

Exits 0 whatever the verdict, so you can iterate.
"""
import re
import sys
import tempfile
from pathlib import Path

from cbmc_cli import run

C = Path(__file__).resolve().parent.parent / "c"


def try_invariant(inv):
    with tempfile.TemporaryDirectory() as d:
        gb, gb2 = Path(d) / "c.gb", Path(d) / "c2.gb"
        run("goto-cc", C / "converge.c", "-o", gb, "-DINV=" + inv)
        note = run("goto-instrument", "--apply-loop-contracts", gb, gb2)
        out = run("cbmc", gb2, "--trace")
    print("INV:", inv)
    for l in out.splitlines():
        if "loop invariant" in l or "assertion i == j" in l or "VERIFICATION" in l:
            print("   " + l.strip())
    trace = [l.strip().split(" (")[0] for l in out.splitlines() if re.match(r"\s+[ij]=", l)]
    if "FAILURE" in out and trace:
        print("   trace:", " ".join(trace))
    if "error" in (note + out).lower() and "VERIFICATION" not in out:
        print(note + out)
    print()


if __name__ == "__main__":
    try_invariant(sys.argv[1] if len(sys.argv) > 1 else "1")
