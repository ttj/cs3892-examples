# FIGURE: figures/add2.svg   (session 9's add-2 counter, drawn -- scripts/draw_models.py)
"""Session 20 -- strengthening: prove a STRONGER invariant, then derive the one you wanted.

P (x != 5) failed because it admits 3, which is not reachable. "x is even" admits fewer
states -- none of them odd -- and it is inductive: 0 is even, and even + 2 is even. Then P
follows, because no even number is 5. The same pattern as session 9's Z3 proof, now checked by
Lean: `inductive_invariant_holds` turns "Even is inductive" into "every reachable x is even".

HW4 Part 3 asks for exactly this move, on a different system.

Expected: the assertions at the bottom hold.
"""
from lean_cli import lean, goals, show, show_goals

F = "S20/Add2.lean"
show(F, "add2-strengthen")
rc, out = lean(F)
assert rc == 0 and out == "", out
print("Lean's goal at each step:")
show_goals(F, "add2-strengthen")
g = dict(goals(F, "add2-strengthen"))
assert g["show x % 2 = 0"].endswith("hx : x = 0\n⊢ Even x")
assert g["show y % 2 = 0"].endswith("hx : x % 2 = 0\nhy : y = x + 2\n⊢ Even y")
assert g["unfold Even at he"].endswith("he : Even x\n⊢ P x")
assert g["omega"].endswith("he : x % 2 = 0\n⊢ x ≠ 5")             # the last omega
print("x is even is inductive, and it implies x != 5: P holds in every reachable state")
