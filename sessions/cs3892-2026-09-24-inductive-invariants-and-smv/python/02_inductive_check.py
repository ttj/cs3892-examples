"""Session 9, demo 2 -- two queries that settle every k at once.

BMC asks "is there a bad run of length <= k?" once per k, forever. Induction
asks two questions that mention no k at all:

    INITIATION   I(x)  =>  Inv(x)                  true at the start
    CONSECUTION  Inv(x) and T(x,x')  =>  Inv(x')   preserved by every step

and one more to connect it to what you actually wanted:

    SUFFICIENCY  Inv(x)  =>  P(x)                  strong enough to matter

Each is a VALIDITY question, so each becomes an unsatisfiability question --
exactly the move from session 7. Assert the negation; `unsat` means it holds.

Here Inv IS P: for the canonical counter, x <= 10 is already inductive.
"""

from z3 import And, Int, Not, Or, Solver, sat, unsat

CAP = 10
x, xp = Int("x"), Int("xp")


def I(v):
    return v == 0


def T(a, b):
    return Or(And(a < CAP, b == a + 1),
              And(a >= CAP, b == 0))


def P(v):
    return v <= CAP


def valid(claim):
    """Assert the negation. unsat == the claim is valid."""
    s = Solver()
    s.add(Not(claim))
    r = s.check()
    return r, (s.model() if r == sat else None)


if __name__ == "__main__":
    Inv = P          # the property is its own invariant here

    checks = [
        ("INITIATION    I(x) => Inv(x)",
            Or(Not(I(x)), Inv(x))),
        ("CONSECUTION   Inv(x) & T(x,x') => Inv(x')",
            Or(Not(And(Inv(x), T(x, xp))), Inv(xp))),
        ("SUFFICIENCY   Inv(x) => P(x)",
            Or(Not(Inv(x)), P(x))),
    ]

    all_ok = True
    for name, claim in checks:
        r, m = valid(claim)
        ok = (r == unsat)
        all_ok &= ok
        print(f"  {name:<44} negation: {str(r):<6} {'HOLDS' if ok else 'FAILS'}")
        if m is not None:
            print(f"      counterexample: {m}")

    assert all_ok, "x <= 10 should be inductive for the canonical counter"
    print("\n  All three unsat, so x <= 10 is an INDUCTIVE INVARIANT.")
    print("  That is a proof for every k simultaneously -- no bound anywhere in it.")
    print("  Two solver calls replaced the infinite family BMC was working through.")
