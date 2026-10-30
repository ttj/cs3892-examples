"""Session 20 -- a transition system in Lean, and why an inductive invariant holds.

`TS`, `Reachable`, `InductiveInvariant`, `Invariant` and `inductive_invariant_holds` are the
definitions HW4's Defs.lean gives you, with the same names. `Reachable` is an inductive
predicate: a state is reachable because it is initial, or because it is one step from a
reachable state. So a fact about every reachable state is proved by induction on HOW the state
was reached: one case per constructor. In the `init` case the first half of "inductive" closes
the goal; in the `step` case the induction hypothesis says the previous state had P, and the
second half carries P across the step.

Expected: the assertions at the bottom hold.
"""
from lean_cli import lean, goals, show, show_goals

F = "S20/TS.lean"
show(F, "ts-defs")
show(F, "holds-proof")
rc, out = lean(F)
assert rc == 0 and out == "", out
print("Lean's goal at each step:")
show_goals(F, "holds-proof")
g = dict(goals(F, "holds-proof"))
assert g["induction hs with"].endswith("hs : Reachable ts s\n⊢ P s")
assert g["| init hi => exact h.1 _ hi"].startswith("case init")
assert g["| init hi => exact h.1 _ hi"].endswith("hi : ts.init s✝\n⊢ P s✝")
assert g["| step _ hst ih => exact h.2 _ _ ih hst"].startswith("case step")
assert g["| step _ hst ih => exact h.2 _ _ ih hst"].endswith(
    "hst : ts.step s✝ t✝\nih : P s✝\n⊢ P t✝")
print("induction on Reachable: an inductive invariant holds in every reachable state")
