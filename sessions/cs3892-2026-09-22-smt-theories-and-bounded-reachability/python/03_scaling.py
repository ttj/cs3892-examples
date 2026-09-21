"""Session 8, demo 3 -- the promised scaling demo. 2^n is the worst case, not the case.

Thursday's slide said SAT is NP-complete and the worst case is 2^n. That is
true and it is not what you see. Modern solvers eat structured instances with
hundreds of thousands of variables, because CDCL learns and the search never
visits most of the space.

Two families, same solver:

  * a long implication CHAIN -- x0 -> x1 -> ... -> xn, forced true.
    Unit propagation alone decides it. Linear-ish.

  * PIGEONHOLE -- n+1 pigeons into n holes, unsat.
    This one is genuinely hard: resolution has no short proof, which is a
    theorem (Haken 1985), not a solver limitation. It falls over around n=10.

The lesson is not 'SAT is easy'. It is that WHICH instance you have matters
more than how big it is.
"""

import time

from z3 import Bool, Implies, Not, Or, Solver, sat, unsat


def chain(n):
    """x0 and (x0 -> x1) and ... -- n variables, forced, trivially propagated."""
    xs = [Bool(f"x{i}") for i in range(n)]
    s = Solver()
    s.add(xs[0])
    for i in range(n - 1):
        s.add(Implies(xs[i], xs[i + 1]))
    s.add(xs[-1])
    return s


def pigeonhole(n):
    """n+1 pigeons, n holes. Unsat, and provably hard for resolution."""
    p = [[Bool(f"p{i}_{j}") for j in range(n)] for i in range(n + 1)]
    s = Solver()
    for i in range(n + 1):                       # every pigeon gets a hole
        s.add(Or(p[i]))
    for j in range(n):                           # no hole takes two pigeons
        for i in range(n + 1):
            for k in range(i + 1, n + 1):
                s.add(Or(Not(p[i][j]), Not(p[k][j])))
    return s


def timed(s):
    t0 = time.perf_counter()
    r = s.check()
    return r, time.perf_counter() - t0


if __name__ == "__main__":
    print("  implication chain -- structured, propagation does all the work")
    for n in (1000, 10000, 100000):
        r, dt = timed(chain(n))
        print(f"    n={n:>6}  {str(r):>5}   {dt:7.3f}s")

    print("\n  pigeonhole -- n+1 pigeons into n holes, unsat and genuinely hard")
    for n in (5, 7, 9, 10):
        r, dt = timed(pigeonhole(n))
        print(f"    n={n:>6}  {str(r):>5}   {dt:7.3f}s")

    r, _ = timed(chain(100000))
    assert r == sat, "the chain must be satisfiable"
    r, _ = timed(pigeonhole(5))
    assert r == unsat, "pigeonhole must be unsatisfiable"
    print("\n  100,000 variables in well under a second; 11 pigeons is worse.")
    print("  Size is not the difficulty. Structure is.")
