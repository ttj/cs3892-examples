"""Slide 30 -- the theory is not decoration (first half).

2x = 1 has no solution in the integers.

Expected: unsat.
"""

from z3 import Int, Solver, unsat

x = Int("x")
s = Solver()
s.add(2 * x == 1)

print(s.check())
assert s.check() == unsat, "expected unsat"
print("No integer is half of one.")
