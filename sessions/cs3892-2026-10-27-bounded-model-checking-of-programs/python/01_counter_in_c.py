# FIGURE: figures/counter.svg   (the running counter, drawn -- scripts/draw_models.py)
"""Session 17 -- a C program is a transition system: the running counter, checked by CBMC.

c/counter.c is the counter from every earlier session, written as a loop. Its states
are (program location, x). CBMC unrolls the loop up to a bound, turns the unrolled
program into one formula over the values x takes, and asks a SAT solver whether any
assertion can fail -- bounded model checking, as in session 16, with the program
itself as the model.

Expected: the assertions at the bottom hold.
"""
from pathlib import Path

from cbmc_cli import run

C = Path(__file__).resolve().parent.parent / "c"

out = run("cbmc", C / "counter.c", "--unwind", 31)
print("$ cbmc counter.c --unwind 31")
print("\n".join("   " + l for l in out.splitlines() if "assertion" in l or "VERIFICATION" in l))
assert "assertion x <= 10: SUCCESS" in out and "VERIFICATION SUCCESSFUL" in out

print("\n   The counter has no inputs, so CBMC settles it while unrolling (constant")
print("   propagation) and the solver gets nothing to do. 02 and 03 have inputs.")
