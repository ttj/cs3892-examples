# FIGURE: figures/counter.svg   (the running counter, drawn -- scripts/draw_models.py)
"""Session 17 -- a C program is a transition system: the running counter, checked by CBMC.

c/counter.c is the counter from every earlier session, written as a loop. Its states
are (program location, x). CBMC unrolls the loop up to a bound, turns the unrolled
program into one formula over the values x takes, and asks a SAT solver whether any
assertion can fail -- bounded model checking, as in session 16, with the program
itself as the model.

Then the formula itself. By default CBMC folds this input-free loop by constant
propagation, so --show-vcc is nearly empty. With --no-propagation --no-simplify it prints
the formula it would hand the solver. At bound 2: one copy of x per assignment (static
single assignment), a Boolean guard per condition, and the assertion after the second
iteration last. That is session 16's I(x0) ∧ T(x0,x1) ∧ T(x1,x2) ∧ ¬P, for a program.

Expected: the assertions at the bottom hold.
"""
import re
from pathlib import Path

from cbmc_cli import run

C = Path(__file__).resolve().parent.parent / "c"

out = run("cbmc", C / "counter.c", "--unwind", 31)
print("$ cbmc counter.c --unwind 31")
print("\n".join("   " + l for l in out.splitlines() if "assertion" in l or "VERIFICATION" in l))
assert "assertion x <= 10: SUCCESS" in out and "VERIFICATION SUCCESSFUL" in out

print("\n   The counter has no inputs, so CBMC settles it while unrolling (constant")
print("   propagation) and the solver gets nothing to do. 02 and 03 have inputs.")

# --- the formula CBMC builds, at bound 2 ------------------------------------------
vcc = run("cbmc", C / "counter.c", "--unwind", 2, "--no-unwinding-assertions",
          "--show-vcc", "--no-propagation", "--no-simplify")
body = vcc[vcc.index("VERIFICATION CONDITIONS"):]
blocks = re.split(r"\n(?=file \S*counter.c line \d+ function main\n)", body)
last = [b for b in blocks if "assertion x <= 10" in b][-1]   # the check after iteration 2


def short(l):
    l = re.sub(r"main::1::(?:1::)?(\w+)!0@1#(\d+)", r"\1_\2", l)
    l = l.replace("goto_symex::\\guard#", "g")
    return re.sub(r"^\{-?\d+\}\s*", "", l).strip()


keep = [short(l) for l in last.splitlines()
        if re.search(r"main::1::|guard#", l) and "CPROVER" not in l]
print("\n$ cbmc counter.c --unwind 2 --no-unwinding-assertions --show-vcc --no-propagation --no-simplify")
print("   (the check after iteration 2; names shortened)")
print("\n".join("   " + l for l in keep))
expect = ["x_2 = 0", "step_2 = 0", "g1 ⇔ (step_2 < 30)", "g2 ⇔ (x_2 < 10)",
          "x_3 = x_2 + 1", "x_4 = 0", "x_5 = (g1 ∧ g2 ? x_3 : x_4)",
          "step_3 = step_2 + 1", "g3 ⇔ (step_3 < 30)", "g4 ⇔ (x_5 < 10)",
          "x_6 = x_5 + 1", "x_7 = 0", "x_8 = (g4 ? x_6 : x_7)",
          "(g1 ∧ g3) ⇒ (x_8 ≤ 10)"]
assert keep == expect, keep
