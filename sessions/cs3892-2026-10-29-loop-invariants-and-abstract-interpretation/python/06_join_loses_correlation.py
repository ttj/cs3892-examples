"""Session 18 -- what a non-relational domain loses at a join, and a false alarm.

    if (*) { x := 1; y := 1 } else { x := 2; y := 2 };   assert x - y + 1 != 0

On every run x = y, so x - y + 1 = 1 and the division in c/correlated.c is safe.
Intervals keep each variable's range separately. After the join x is in [1, 2] and y is
in [1, 2] -- both true -- but the fact "x = y" is gone, so x - y + 1 is in [0, 2] and the
analysis must report a possible division by zero: a FALSE ALARM. Sound (it never misses
a real division by zero) and imprecise (it reports one that cannot happen).

A RELATIONAL domain keeps constraints between variables. The simplest useful one keeps
bounds on differences (x - y in [a, b]); octagons add sums; polyhedra keep any linear
inequality. Here x - y is in [0, 0] on both branches, so it is [0, 0] after the join,
and x - y + 1 = 1.

The real tools agree: goto-analyzer's interval domain says UNKNOWN; CBMC, which checks
each path exactly, says SUCCESS.

Expected: the assertions at the bottom hold.
"""
from pathlib import Path

from absint import Analysis, Intervals, show
from cbmc_cli import run

prog = ("seq",
        ("if", ("nondet",),
         ("seq", ("assign", "x", ("const", 1)), ("assign", "y", ("const", 1))),
         ("seq", ("assign", "x", ("const", 2)), ("assign", "y", ("const", 2)))),
        ("assert", ("!=", ("+", ("-", ("var", "x"), ("var", "y")), ("const", 1)), ("const", 0))))

A = Analysis(Intervals())
env = A.run(prog, {})
d = Intervals().binop("+", Intervals().binop("-", env["x"], env["y"]), (1, 1))
print("intervals:   x = %s   y = %s   x - y + 1 = %s   -> %s"
      % (show(env["x"]), show(env["y"]), show(d), "ALARM (possible 0)" if A.alarms else "safe"))
assert env["x"] == (1, 2) and env["y"] == (1, 2) and d == (0, 2) and A.alarms

# the relational view: track the difference x - y on each branch, then join that
diff = Intervals().join((1 - 1, 1 - 1), (2 - 2, 2 - 2))
d_rel = Intervals().binop("+", diff, (1, 1))
print("relational:  x - y = %s   x - y + 1 = %s   -> safe" % (show(diff), show(d_rel)))
assert diff == (0, 0) and d_rel == (1, 1)

concrete = {x - y + 1 for x, y in ((1, 1), (2, 2))}
print("concrete:    x - y + 1 is one of", sorted(concrete), " -- the alarm is false")
assert concrete == {1}

C = Path(__file__).resolve().parent.parent / "c"
ga = run("goto-analyzer", C / "correlated.c", "--verify", "--intervals")
cb = run("cbmc", C / "correlated.c")
print("\n$ goto-analyzer correlated.c --verify --intervals")
print("   " + next(l for l in ga.splitlines() if "assertion x" in l).strip())
print("$ cbmc correlated.c")
print("   " + next(l for l in cb.splitlines() if "assertion" in l).strip())
assert "assertion x - y + 1 != 0: UNKNOWN" in ga
assert "assertion x - y + 1 != 0: SUCCESS" in cb
