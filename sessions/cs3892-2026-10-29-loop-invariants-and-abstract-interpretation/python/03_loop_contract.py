# FIGURE: figures/add2.svg   (session 9's add-2 counter, drawn -- scripts/draw_models.py)
"""Session 18 -- the same three conditions, checked by CBMC on a C loop: loop contracts.

c/add2_loop.c is session 9's add-2 counter as a loop, followed by assert(x != 5).
__CPROVER_loop_invariant(Inv) states an invariant; goto-instrument
--apply-loop-contracts replaces the loop by: check Inv on entry; from an ARBITRARY state
satisfying Inv, run one iteration and check Inv again; then continue after the loop
from an arbitrary state satisfying Inv and not the loop condition. No unwinding bound.

With Inv = x != 5 (the property itself) the "preserved" check fails, and CBMC's trace
shows the counterexample to induction: x = 3, then x = 5. With Inv = 0 <= x <= 1000 and
x even (the cap keeps x + 2 from overflowing) everything holds, for every number of
iterations.

Expected: the assertions at the bottom hold.
"""
import tempfile
from pathlib import Path

from cbmc_cli import run

C = Path(__file__).resolve().parent.parent / "c"


def contract(inv=None):
    with tempfile.TemporaryDirectory() as d:
        gb, gb2 = Path(d) / "a.gb", Path(d) / "a2.gb"
        run("goto-cc", C / "add2_loop.c", "-o", gb, *(["-DINV=" + inv] if inv else []))
        note = run("goto-instrument", "--apply-loop-contracts", gb, gb2)
        return note + run("cbmc", gb2, "--trace")


weak = contract("x != 5")
print("Inv: x != 5")
for l in weak.splitlines():
    if "loop invariant" in l or "assertion x" in l:
        print("   " + l.strip())
xs = []
for l in weak[weak.index("Trace for main.3"):].splitlines():
    if l.strip().startswith("x="):
        xs.append(int(l.split("=")[1].split()[0]))
    if "Check that loop invariant is preserved" in l and xs:
        break
print("   counterexample to induction: x =", " -> ".join(map(str, xs)))
assert "Check that loop invariant is preserved: FAILURE" in weak
assert xs[-2:] == [3, 5]

strong = contract()
print("\nInv: 0 <= x <= 1000 and x % 2 == 0")
for l in strong.splitlines():
    if "loop invariant" in l or "assertion x" in l or "VERIFICATION" in l:
        print("   " + l.strip())
assert "Check that loop invariant is preserved: SUCCESS" in strong
assert "assertion x != 5: SUCCESS" in strong and "VERIFICATION SUCCESSFUL" in strong
print("\n   CBMC also warns that the loop has no decreases clause: this proves partial")
print("   correctness (IF the program gets past the loop, x != 5), not termination.")
assert "does not have a decreases clause" in strong
