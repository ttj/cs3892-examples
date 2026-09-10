"""HW1 part 2 -- pigeonhole, parameterised. A COMPLETE starter to scale up.

n+1 pigeons into n holes is unsatisfiable, and famously hard for a solver: any
resolution proof is exponential in n. That makes it the cleanest way to find
"the wall" part 2 asks about -- the wall is real, it is not Z3 being slow, and
it has a name.

Change SIZES, run p2_timing.py, and report where it stops finishing.
"""

from z3 import Bool, Not, Or, Solver


def pigeonhole(pigeons: int, holes: int) -> Solver:
    """Every pigeon in some hole; no hole holding two."""
    s = Solver()
    x = [[Bool(f"p{i}h{j}") for j in range(holes)] for i in range(pigeons)]
    for i in range(pigeons):
        s.add(Or(x[i]))                                  # somewhere
    for j in range(holes):                               # and not two in one
        for i in range(pigeons):
            for k in range(i + 1, pigeons):
                s.add(Or(Not(x[i][j]), Not(x[k][j])))
    return s


if __name__ == "__main__":
    for p, h in ((5, 4), (4, 4), (9, 8)):
        r = pigeonhole(p, h).check()
        print(f"  {p} pigeons into {h} holes: {r}")
    assert pigeonhole(5, 4).check().r == -1, "5 into 4 must be unsat"
    assert pigeonhole(4, 4).check().r == 1, "4 into 4 must be sat"
    print("\nThe clause count is quadratic in `pigeons`. That is the wall.")
