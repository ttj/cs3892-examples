"""Slide 29, second half -- change 11 to 12 and the answer flips.

A `sat` answer comes with a model: the world in which the claim holds.

Expected: sat, with months >= 12, u true, c false.
"""

from z3 import Bool, Int, And, Not, Solver, sat, is_true

months = Int("months")
u, c, L = Bool("u"), Bool("c"), Bool("L")

s = Solver()
s.add(L == And(months >= 12, u, Not(c)))
s.add(months >= 12)
s.add(L)

print(s.check())
assert s.check() == sat, "expected sat"

m = s.model()
print("model:", m)
assert m[months].as_long() >= 12
assert is_true(m[u]) and not is_true(m[c])
print(f"Eligible, and the solver says exactly who: months={m[months]}, "
      f"unused leave={m[u]}, contractor={m[c]}")
