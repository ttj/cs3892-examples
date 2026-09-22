"""Session 9, demo 4 -- strengthening: make the invariant STRONGER to make it provable.

03 failed because Inv = P admitted x = 3, which is not reachable. The cure is
counter-intuitive the first time you meet it: you do not weaken the claim, you
make it STRONGER, so that it stops admitting states the machine cannot be in.

    P(x)      x != 5                 true, but not inductive
    Inv(x)    x is even              STRONGER (rules out 3, 5, 7, ...)  and inductive

Stronger means a SMALLER set of states. Shrinking Inv until it fits inside the
reachable set is what makes consecution go through -- and `Inv => P` is what
keeps the thing you actually wanted.

This is the pattern behind every proof in Unit 8, and the reason a model
checker that finds invariants for you (IC3, Unit 6) was a big deal.
"""

from z3 import And, Int, Not, Or, Solver, sat, unsat

x, xp = Int("x"), Int("xp")


def I(v):
    return v == 0


def T(a, b):
    return b == a + 2


def P(v):
    return v != 5


def Inv(v):
    return v % 2 == 0        # the strengthening: x is even


def check(name, claim):
    s = Solver()
    s.add(Not(claim))
    r = s.check()
    print(f"  {name:<46} negation: {str(r):<6} {'HOLDS' if r == unsat else 'FAILS'}")
    return r, (s.model() if r == sat else None)


if __name__ == "__main__":
    print("  Inv(x) = 'x is even'. Three obligations:\n")
    r1, _ = check("INITIATION    I(x) => Inv(x)", Or(Not(I(x)), Inv(x)))
    r2, m = check("CONSECUTION   Inv(x) & T(x,x') => Inv(x')",
                  Or(Not(And(Inv(x), T(x, xp))), Inv(xp)))
    r3, _ = check("SUFFICIENCY   Inv(x) => P(x)", Or(Not(Inv(x)), P(x)))

    for r in (r1, r2, r3):
        assert r == unsat, "all three must hold for the strengthening to work"

    print("\n  All three unsat. `x is even` is inductive AND implies `x != 5`,")
    print("  so P holds on every reachable state, for every k, forever.")

    # the CTI from 03 is now excluded -- that is WHY consecution went through
    s = Solver()
    s.add(Inv(x), x == 3)
    assert s.check() == unsat, "3 must no longer satisfy Inv"
    print("\n  The old CTI is gone: x = 3 does not satisfy Inv, so induction is")
    print("  never asked about it. Nothing about the solver changed -- we changed")
    print("  the claim, and a stronger claim was the EASIER one to prove.")
