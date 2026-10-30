# FIGURE: figures/switch.svg   (the counter with a power switch, drawn -- scripts/draw_models.py)
"""Session 20 -- the other direction: BUILD a reachable state, one step at a time.

An invariant says what every reachable state satisfies. To show a bound is TIGHT you need a
reachable state that meets it, and a `Reachable` proof is built forward from its constructors:
`.init` for the start, then `.step` with a transition. `reach_k` does it for every k <= N, by
induction on k: switch on, then tick k times. `bound_tight` uses ⟨true, N⟩ as the witness of
an `∃`.

Note the goal in the succ case: Lean wants x := ↑(k + 1), and `.tick` produces x := ↑k + 1.
They are equal by computation, so `exact` accepts it.

Expected: the assertions at the bottom hold.
"""
from lean_cli import goals, show, show_goals

F = "S20/Switch.lean"
show(F, "forward")
print("Lean's goal at each step:")
show_goals(F, "forward")
g = dict(goals(F, "forward"))
assert g["| zero => intro _; exact .step (.init rfl) .on"] == \
    "case zero\nN : Nat\n⊢ 0 ≤ N → Reachable (counter N) { on := true, x := ↑0 }"
last = g["exact .step hr (.tick (by omega))"]
assert last.endswith("hr : Reachable (counter N) { on := true, x := ↑k }\n"
                     "⊢ Reachable (counter N) { on := true, x := ↑(k + 1) }"), last
print("every ⟨true, k⟩ with k <= N is reachable, so the bound N is reached: it is tight")
