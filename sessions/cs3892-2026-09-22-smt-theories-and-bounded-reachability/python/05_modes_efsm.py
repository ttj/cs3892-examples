"""Session 8, demo 5 -- the two-mode machine, encoded exactly as drawn.

This is the extended state machine on slide 20, taken from ttj/fmaiv,
`day02/examples/counter.smv`. It is the richer relative of the course's
counter: same integer x, plus a mode and a button.

    mode  : {off, on}          press : a FREE INPUT, chosen fresh each step
    x     : Int                init  : mode = off, x = 0

    off, !press               -> off,  x held
    off,  press               -> on,   x held
    on,  !press & x < 10      -> on,   x := x + 1
    on,  (press | x >= 10)    -> off,  x := 0

Two things this file is for.

1. It shows a transition relation with MORE THAN ONE variable. T(x,x') became
   T(mode, x, mode', x'): one conjunct per variable, all of them in the same
   formula. Nothing else about the method changes.

2. It shows the property still holds. `press` is unconstrained, so the solver
   is free to choose the worst button-pressing adversary it can find -- and
   x = 11 is still not reachable, because the only edge that increments is
   guarded by x < 10.

Delete the mode and the two `on` edges collapse into the course's machine,
x' = x+1 if x < 10 else 0. That is the relationship labs/running-example.md
describes.
"""

from z3 import And, Bool, If, Int, Not, Or, Solver, sat, unsat

CAP = 10


def step(mode, x, press, mode_n, x_n):
    """The transition relation, one conjunct per variable. `on` is mode = True."""
    counting = And(mode, Not(press), x < CAP)          # on, counting up
    turning_off = And(mode, Or(press, x >= CAP))       # on, pressed or maxed out
    turning_on = And(Not(mode), press)                 # off + press
    staying_off = And(Not(mode), Not(press))           # off, no press

    next_mode = Or(counting, turning_on)               # exactly when we end up `on`
    next_x = If(counting, x + 1,
             If(turning_off, 0, x))                    # reset on the way out, else hold
    # staying_off and turning_on both hold x, which `next_x`'s else branch covers
    _ = staying_off
    return And(mode_n == next_mode, x_n == next_x)


def reach(target, k):
    """Can x equal `target` within k steps, for SOME sequence of button presses?"""
    mode = [Bool(f"m{i}") for i in range(k + 1)]
    x = [Int(f"x{i}") for i in range(k + 1)]
    press = [Bool(f"p{i}") for i in range(k)]

    s = Solver()
    s.add(Not(mode[0]), x[0] == 0)                     # init: off, x = 0
    for i in range(k):
        s.add(step(mode[i], x[i], press[i], mode[i + 1], x[i + 1]))
    s.add(Or([xi == target for xi in x]))
    return s, mode, x, press


if __name__ == "__main__":
    print("  can x reach 10?  (it should -- press once, then count)")
    for k in (5, 11, 12):
        s, mode, x, press = reach(10, k)
        r = s.check()
        note = ""
        if r == sat:
            m = s.model()
            note = "   x: " + " ".join(str(m[xi]) for xi in x)
        print(f"    k={k:>3}: {r}{note}")

    print("\n  can x reach 11?  (it must NOT -- the guard is x < 10)")
    for k in (12, 20, 30):
        s, *_ = reach(11, k)
        r = s.check()
        print(f"    k={k:>3}: {r}")
        assert r == unsat, f"x = 11 must be unreachable, got {r} at k={k}"

    s, *_ = reach(10, 11)
    assert s.check() == sat, "x = 10 must be reachable"
    print("\n  x = 11 is unreachable at every bound tried, with `press` free for")
    print("  the solver to choose. Bounded means bounded, though: these are")
    print("  three bounds, not a proof. The proof is Thursday's job.")
