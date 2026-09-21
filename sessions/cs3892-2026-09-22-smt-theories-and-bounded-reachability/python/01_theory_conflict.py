"""Session 8, demo 1 -- why a SAT solver alone is not enough.

The boolean SKELETON of an SMT formula is what a SAT solver sees: every atom
becomes an opaque boolean. Here the skeleton is trivially satisfiable and the
formula is not, and the gap between those two facts is the entire job of
DPLL(T).

    (x > 5)  and  (x < 3)

Skeleton:  p and q      -- sat, take p = q = True.
Theory:    no integer is both > 5 and < 3.

The SAT solver proposes p = q = True. The THEORY solver for linear integer
arithmetic checks that assignment against what the symbols mean, finds it
impossible, and hands back a lemma -- `not (p and q)` -- which the SAT solver
adds as a clause and never proposes again. That loop is DPLL(T).
"""

from z3 import Bool, Int, Solver, sat, unsat


def skeleton_only():
    """What a plain SAT solver sees: two unrelated booleans."""
    p, q = Bool("p"), Bool("q")
    s = Solver()
    s.add(p, q)
    return s.check()


def with_theory():
    """What Z3 sees: the same two atoms, with their arithmetic meaning."""
    x = Int("x")
    s = Solver()
    s.add(x > 5, x < 3)
    return s.check()


if __name__ == "__main__":
    a, b = skeleton_only(), with_theory()
    print(f"  boolean skeleton  p and q      : {a}")
    print(f"  with the theory   x>5 and x<3  : {b}")
    assert a == sat, "the skeleton must be satisfiable -- that is the point"
    assert b == unsat, "LIA must refute it"
    print("\n  The skeleton is SAT and the formula is UNSAT. The theory solver is")
    print("  what closes that gap, by returning the lemma  not (p and q).")
