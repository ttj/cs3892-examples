# FIGURE: figures/add2.svg   (session 9's add-2 counter, drawn -- scripts/draw_models.py)
"""Session 20 -- session 9's add-2 machine: true, and not inductive. Now in Lean.

add-2 starts at 0 and adds 2 forever. P: x is never 5. P is TRUE -- every reachable x is even
-- but it is NOT INDUCTIVE: the step half of "inductive" asks about every state in P, reachable
or not, and 3 is in P and steps to 5. 3 is a counterexample to induction (a CTI): no run ever
reaches it, so it is not a bug. It says P is too weak to prove itself.

In Lean, "not inductive" is a theorem: assume it is inductive, apply the step half to 3 and 5,
and derive P 5, i.e. 5 != 5.

Expected: the assertions at the bottom hold.
"""
from lean_cli import lean, goals, show, show_goals

F = "S20/Add2.lean"
show(F, "add2-def")
show(F, "add2-cti")
rc, out = lean(F)
assert rc == 0 and out == "", out
print("Lean's goal at each step:")
show_goals(F, "add2-cti")
g = dict(goals(F, "add2-cti"))
assert g["intro h"] == "⊢ ¬InductiveInvariant add2 P"
assert g["exact h5 rfl"] == "h : InductiveInvariant add2 P\nh5 : P 5\n⊢ False"
print("CTI: 3 satisfies x != 5 and steps to 5 -- and 3 is never reached")
