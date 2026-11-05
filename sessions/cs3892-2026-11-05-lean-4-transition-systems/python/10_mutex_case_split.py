# FIGURE: figures/mutex.svg   (the state machine, drawn -- scripts/draw_models.py)
"""Session 20 -- mutual exclusion for session 11's mutex, proved in Lean by a case split.

The pair (a, b) before the step is one of 3 x 3 = 9. `cases a <;> cases b` makes one goal for
each, and `simp` evaluates the step's if-chains: what is left in each goal is what that step
can do, as a hypothesis about the next state. (critical, critical) is ruled out by the
invariant. In the other eight a step cannot end with both critical: a guard fails
(b != critical keeps a out while b is in), or both would have to move, which needs
move = 1 and move = 2 at once. `simp_all` closes all eight.

Expected: the assertions at the bottom hold.
"""
from lean_cli import lean, goals, show

F = "S20/MutexProofs.lean"
show(F, "mutex-proof")
rc, out = lean(F)
assert rc == 0 and out == "", out

g = dict(goals(F, "mutex-proof"))
eight = g["all_goals simp_all"]
blocks = eight.split("case right.")[1:]
names = [b.split("\n", 1)[0] for b in blocks]
assert names == ["idle.idle", "idle.trying", "idle.critical", "trying.idle", "trying.trying",
                 "trying.critical", "critical.idle", "critical.trying"], names   # 9 - 1
print("After the split and simp: what one step can do, from each (a, b)")
for b in blocks:
    lines = b.split("\n")
    ha = next(ln for ln in lines if ln.startswith("ha :"))
    hb = next(ln for ln in lines if ln.startswith("hb :"))
    print(f"  ({lines[0].replace('.', ', ')}):  {ha.replace('AVal.', '')}   {hb.replace('BVal.', '')}")
tc = blocks[names.index("trying.critical")]
assert "ha : t.a = AVal.trying" in tc            # the guard b != critical failed: a stays trying
tt = blocks[names.index("trying.trying")]
assert "ha : if move = 1 then t.a = AVal.critical" in tt and "hb : if move = 2 then t.b = BVal.critical" in tt
assert g[""] == "no goals"
print("\n(critical, critical) is ruled out by the invariant; the other 8 by a guard or by move")
