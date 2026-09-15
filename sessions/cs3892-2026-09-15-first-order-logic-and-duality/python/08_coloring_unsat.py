"""Slide 32 -- the same encoding, one edge richer.

Four regions, every one adjacent to every other, three colours. There is no
legal colouring, and `unsat` is a PROOF of that -- not "I looked and did not
find one".

In today's language: the set of legal colourings is EMPTY. That is what unsat
means, and it is why unsat is the answer you want when you are trying to show
something cannot happen.

Expected: unsat.
"""

from itertools import combinations

from z3 import Int, Solver, unsat

r = [Int(f"r{i}") for i in range(4)]

s = Solver()
for x in r:
    s.add(x >= 1, x <= 3)
for a, b in combinations(r, 2):               # every pair adjacent
    s.add(a != b)

print(s.check())
assert s.check() == unsat, "expected unsat"
print("No colouring exists. unsat is a proof of impossibility, and the set")
print("of legal colourings is the empty set.")
