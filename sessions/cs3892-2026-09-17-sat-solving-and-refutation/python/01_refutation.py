"""Slide 24 -- proof by refutation.

The contrapositive law proved by hand on September 10:

    (not q -> not p)  ===  (p -> q)

To prove it, do not try to show it is true everywhere. Assert that it is FALSE
-- that the two sides differ -- and ask whether that is satisfiable. `unsat`
means no interpretation makes them differ, which is exactly what "valid" means.

Expected: unsat.
"""

from z3 import Bool, Implies, Not, Solver, unsat

p, q = Bool("p"), Bool("q")

contrapositive = Implies(Not(q), Not(p))
original = Implies(p, q)

s = Solver()
s.add(Not(contrapositive == original))      # can the two sides ever differ?

print(s.check())
assert s.check() == unsat, "expected unsat"
print("They can never differ, so the law is valid.")
print("Note what was actually asked: not 'is it true?' but 'can it be false?'")
