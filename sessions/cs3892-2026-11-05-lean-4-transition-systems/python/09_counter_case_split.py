# FIGURE: figures/modes_efsm.svg   (the two-mode counter, drawn -- scripts/draw_models.py)
"""Session 20 -- the two-mode counter's INVARSPECs, settled in Lean by case splits.

x <= 10: `split at hx` makes one goal per line of next(x)'s `case` (count up; reset; hold),
and omega closes each one.

mode = off -> x = 0: `cases mode <;> cases press` makes one goal per (mode, press), and
`simp` evaluates the step's if-chains for each. Two of the four are closed by a contradiction
(the step would have turned the counter on, but the goal says it is off); one splits again,
on x < 10.

x < 10 is false, as NuSMV says: Lean proves its negation from a reachable state with x = 10,
built step by step -- NuSMV's counterexample trace, as a proof.

Expected: the assertions at the bottom hold.
"""
from lean_cli import lean, goals, show, show_goals

F = "S20/CounterProofs.lean"
for r in ("inv1", "inv2", "inv3"):
    show(F, r)
rc, out = lean(F)
assert rc == 0 and out == "", out
print("Lean's goal before each step of the second proof:")
show_goals(F, "inv2")

g = goals(F, "inv1")
after = [state for line, state in g if line in ("· omega", "· split at hx")]
assert after[0].startswith("case right.isTrue") and "hx : t.x = s.x + 1" in after[0]     # count up
assert after[1].startswith("case right.isFalse") and "hx : if s.mode = on" in after[1]   # the rest
assert after[2].startswith("case right.isFalse.isTrue") and "hx : t.x = 0" in after[2]   # reset
assert after[3].startswith("case right.isFalse.isFalse") and "hx : t.x = s.x" in after[3] # hold

g2 = dict(goals(F, "inv2"))
four = g2["· omega"]                                 # the goals right after the case split
assert [ln for ln in four.split("\n") if ln.startswith("case ")] == [
    "case right.off.false", "case right.off.true", "case right.on.false", "case right.on.true"]
assert "hm : t.mode = on" in four.split("case right.off.true")[1].split("case right.on.false")[0]
assert "hm : if x < 10 then t.mode = on" in four.split("case right.on.false")[1]
assert four.split("case right.on.true")[1].rstrip().endswith("hx : t.x = 0\n⊢ t.x = 0")
print("\nx <= 10: three goals, one per case line; (mode = off -> x = 0): four, one per (mode, press)")
print("x < 10: false, and Lean proves the negation with NuSMV's trace to x = 10")
