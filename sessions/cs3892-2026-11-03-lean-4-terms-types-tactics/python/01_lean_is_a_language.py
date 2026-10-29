# FIGURE: figures/counter.svg   (the running counter, drawn -- scripts/draw_models.py)
"""Session 19 -- Lean is a programming language, and a theorem is about a program.

The running counter: below 10 it counts up, otherwise it resets to 0. In Lean it is a
function `step`, and `run 0 n` is where it is after n moves. `#eval` runs it; `#check` gives
a type, and a statement such as `step 3 = 4` has a type too: Prop.

Then three theorems. `step_3` holds by computation (rfl). `step_le` holds for every x: if
x <= 10 then step x <= 10 -- the "preserved" condition of Thursday's loop invariant. `run_le`
holds for every number of moves, by induction: the base case is "established", the step
case uses step_le. No bound, no unwinding: this is what CBMC could not say.

Expected: the assertions at the bottom hold.
"""
from lean_cli import lean, goals, show, show_goals

F = "S19/Counter.lean"
show(F, "counter-def")
rc, out = lean(F)
print("Lean says:\n  " + out.replace("\n", "\n  ") + "\n")
assert rc == 0 and "warning" not in out and "error" not in out, out
assert out.split("\n") == ["4", "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 1]",
                           "S19.step (x : Nat) : Nat", "step 3 = 4 : Prop"], out

show(F, "counter-theorems")
print("Lean's goal at each step:")
show_goals(F, "counter-theorems")
g = dict(goals(F, "counter-theorems"))
assert g["by_cases hx : x < 10"].endswith("⊢ (if x < 10 then x + 1 else 0) ≤ 10")
assert g["omega"].endswith("hx : x < 10\n⊢ x ≤ 9")              # what simp [hx] left
assert g["| zero => decide"] == "case zero\n⊢ run 0 0 ≤ 10"
assert g["| succ n ih => exact step_le (run 0 n) ih"] == \
    "case succ\nn : Nat\nih : run 0 n ≤ 10\n⊢ run 0 (n + 1) ≤ 10"
print("every number of moves: run 0 n ≤ 10 for all n, proved; the counter stays at or below 10")
