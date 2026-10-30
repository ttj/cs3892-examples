# FIGURE: figures/switch.svg   (the counter with a power switch, drawn -- scripts/draw_models.py)
"""Session 20 -- the running counter with a power switch, proved for EVERY cap N.

The state is a structure (`on`, `x`). A step is an inductive relation with one constructor per
transition -- tick, wrap, off, on -- each carrying its guard. So "every step keeps x <= N" is a
`cases` on the step: one goal per transition, with the state's fields filled in by the
constructor. `show` restates a goal Lean has not simplified ({ on := true, x := x }.x is just
x) so that `omega` can read it.

The proof never mentions a value of N. nuXmv checks one cap at a time; this is all of them.

Expected: the assertions at the bottom hold.
"""
from lean_cli import lean, goals, show, show_goals

F = "S20/Switch.lean"
show(F, "switch-def")
show(F, "switch-proof")
rc, out = lean(F)
assert rc == 0 and out == "", out
print("Lean's goal at each step:")
show_goals(F, "switch-proof")
g = dict(goals(F, "switch-proof"))
assert g["cases hst with"].endswith("hst : CtrStep N s t\n⊢ t.x ≤ ↑N")
tick = g["| tick h => show _ + 1 ≤ (N : Int); omega"]
assert tick.startswith("case right.tick") and "h : x✝ < ↑N" in tick
assert tick.endswith("⊢ { on := true, x := x✝ + 1 }.x ≤ ↑N")
assert g["| wrap h => show (0 : Int) ≤ N; omega"].endswith("⊢ { on := true, x := 0 }.x ≤ ↑N")
assert g["| off => show (0 : Int) ≤ N; omega"].endswith("⊢ { on := false, x := 0 }.x ≤ ↑N")
assert g["| on => exact hs"].endswith(
    "hs : { on := false, x := x✝ }.x ≤ ↑N\n⊢ { on := true, x := x✝ }.x ≤ ↑N")
print("x <= N in every reachable state, for every cap N: one proof, four transitions")
