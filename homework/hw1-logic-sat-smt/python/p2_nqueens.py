"""HW1 part 2 -- n-queens, the other starter. COMPLETE; scale it up.

An integer encoding rather than a boolean one: q[i] is the row of the queen in
column i. Note how much smaller this is than the boolean version -- choosing
the encoding is most of the work in part 2, and the timing table is where you
show it mattered.
"""

from z3 import Distinct, Int, Solver, sat


def nqueens(n: int) -> Solver:
    q = [Int(f"q{i}") for i in range(n)]
    s = Solver()
    for i in range(n):
        s.add(q[i] >= 0, q[i] < n)          # on the board
    s.add(Distinct(q))                      # no two in a row
    for i in range(n):                      # nor on a diagonal
        for j in range(i + 1, n):
            s.add(q[i] - q[j] != i - j, q[i] - q[j] != j - i)
    return s


if __name__ == "__main__":
    for n in (3, 4, 8):
        s = nqueens(n)
        r = s.check()
        print(f"  {n}-queens: {r}" + (f"  rows={[s.model()[Int(f'q{i}')] for i in range(n)]}"
                                      if r == sat else ""))
    assert nqueens(3).check().r == -1, "3-queens must be unsat"
    assert nqueens(8).check().r == 1, "8-queens must be sat"
