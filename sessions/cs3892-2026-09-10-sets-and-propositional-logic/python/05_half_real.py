"""Slide 30 -- the theory is not decoration (second half).

The SAME formula over the reals. One word changed; opposite answer. This is why
"is it satisfiable?" is not well formed until you say satisfiable in WHAT.

Expected: sat, x = 1/2.
"""

from z3 import Real, Solver, sat

x = Real("x")
s = Solver()
s.add(2 * x == 1)

print(s.check())
assert s.check() == sat, "expected sat"

m = s.model()
print("model:", m)
assert m[x].as_fraction() == __import__("fractions").Fraction(1, 2)
print(f"x = {m[x]} -- exact, not a float. Z3 reasons over the rationals here.")
