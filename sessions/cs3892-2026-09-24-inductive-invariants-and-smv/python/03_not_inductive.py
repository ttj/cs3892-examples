"""Session 9, demo 3 -- invariant, but NOT inductive. The distinction, in one machine.

    I(x)      x = 0
    T(x,x')   x' = x + 2          count up by TWO
    P(x)      x != 5

P is an INVARIANT: every reachable state is even, and 5 is odd, so no run
ever reaches 5. True, and a bounded check agrees at every k you try.

P is NOT INDUCTIVE, and the difference is the whole lecture. Consecution asks

    P(x) and T(x,x')  =>  P(x')

about EVERY x satisfying P -- reachable or not. Take x = 3. It satisfies
P (3 != 5). One step lands on 5. Consecution fails.

x = 3 is a COUNTEREXAMPLE TO INDUCTION, a CTI: a state that satisfies the
property, steps outside it, and is not reachable at all. Induction does not
know about reachability. That is exactly what makes it cheap, and exactly
what makes it fail here.
"""

from z3 import And, Int, Not, Or, Solver, sat, unsat

x, xp = Int("x"), Int("xp")


def I(v):
    return v == 0


def T(a, b):
    return b == a + 2


def P(v):
    return v != 5


def check(name, claim):
    s = Solver()
    s.add(Not(claim))
    r = s.check()
    print(f"  {name:<42} negation: {str(r):<6} {'HOLDS' if r == unsat else 'FAILS'}")
    return r, (s.model() if r == sat else None)


def bmc(k):
    """The bounded check, for contrast: it never finds anything."""
    xs = [Int(f"x{i}") for i in range(k + 1)]
    s = Solver()
    s.add(xs[0] == 0)
    for i in range(k):
        s.add(T(xs[i], xs[i + 1]))
    s.add(Or([Not(P(xi)) for xi in xs]))
    return s.check()


if __name__ == "__main__":
    print("  Bounded model checking says nothing is wrong:")
    for k in (5, 10, 40):
        r = bmc(k)
        print(f"    k={k:>3}: {r}")
        assert r == unsat
    print("    ...and it is right. P really is an invariant.\n")

    print("  Now try to PROVE it by induction, with Inv = P:")
    r1, _ = check("INITIATION    I(x) => P(x)", Or(Not(I(x)), P(x)))
    r2, m = check("CONSECUTION   P(x) & T(x,x') => P(x')",
                  Or(Not(And(P(x), T(x, xp))), P(xp)))

    assert r1 == unsat, "initiation should hold"
    assert r2 == sat, "consecution must FAIL -- that is the point of this file"
    print(f"\n    CTI: x = {m[x]}  ->  x' = {m[xp]}")
    print("    x = 3 satisfies P, and one step leaves P. So P is not inductive.")
    print("    But 3 is NOT REACHABLE -- every reachable value is even.")
    print("    Induction was asked about a state the machine can never be in.")
    print("\n    The fix is not a better solver. It is a STRONGER invariant:")
    print("    see 04_strengthen.py.")
