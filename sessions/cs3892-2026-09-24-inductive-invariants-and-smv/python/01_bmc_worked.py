"""Session 9, demo 1 -- the BMC encoding written out, one k at a time.

Tuesday gave the shape:

    I(x0)  and  AND_{i<k} T(x_i, x_{i+1})  and  OR_{i<=k} not P(x_i)

This prints the actual formula at each k so you can SEE it grow, rather than
reading the big-AND notation and taking it on faith.

The machine is the CANONICAL counter -- guard and reset both present:

    I(x)      x = 0
    T(x,x')   (x < 10 and x' = x+1)  or  (x >= 10 and x' = 0)
    P(x)      x <= 10

(HW1 Part 3 uses the variant with no guard and no reset. Work that one
yourself; the method is identical and the threshold is the graded part.)

Every k comes back `unsat`. Note what that does and does not buy you -- it is
the whole reason the next three files exist.
"""

from z3 import And, Int, Or, Solver, sat, unsat

CAP = 10


def trans(a, b):
    """T(a,b): the canonical counter's transition relation, as one formula."""
    return Or(And(a < CAP, b == a + 1),
              And(a >= CAP, b == 0))


def unroll(k):
    """Build the k-step BMC query, and the same thing as readable text."""
    x = [Int(f"x{i}") for i in range(k + 1)]
    s = Solver()

    init = x[0] == 0
    s.add(init)
    lines = [f"I(x0)              {init}"]

    for i in range(k):
        t = trans(x[i], x[i + 1])
        s.add(t)
        lines.append(f"T(x{i},x{i+1})          {t}")

    bad = Or([xi > CAP for xi in x])
    s.add(bad)
    lines.append(f"OR not P(x_i)      {bad}")
    return s, x, lines


if __name__ == "__main__":
    for k in (1, 2):
        s, x, lines = unroll(k)
        print(f"  --- k = {k} " + "-" * 50)
        for ln in lines:
            print("   ", ln)
        print(f"    check-sat          {s.check()}\n")

    print("  --- push the bound out " + "-" * 39)
    for k in (3, 10, 11, 25, 50):
        s, _, _ = unroll(k)
        r = s.check()
        print(f"    k={k:>3}: {r}")
        assert r == unsat, f"the canonical machine must be safe, got {r} at k={k}"

    print("\n    Fifty bounds, fifty `unsat`. That is fifty facts about runs of")
    print("    length <= 50 -- and NOT a proof. There are infinitely many k and")
    print("    we have checked fifty of them. 02_inductive_check.py settles all")
    print("    of them at once, with two queries and no k at all.")
