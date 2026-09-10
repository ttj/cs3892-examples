"""Slide 29 -- one atom becomes arithmetic.

`e` was an opaque boolean. `months >= 12` is a constraint. Nobody tells Z3 that
11 < 12: the Int sort carries a theory of arithmetic with it.

Expected: unsat.
"""

from z3 import Bool, Int, And, Not, Solver, unsat

months = Int("months")
u, c, L = Bool("u"), Bool("c"), Bool("L")

s = Solver()
s.add(L == And(months >= 12, u, Not(c)))
s.add(months == 11)
s.add(L)

print(s.check())
assert s.check() == unsat, "expected unsat"
print("11 >= 12 is false, and Z3 worked that out on its own.")
