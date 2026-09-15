"""Slide 21 -- the same policy with 18 changed to 6.

`sat` is not the solver failing. The rule only said what happens at twelve
months or more, so a six-month user who is not approved is entirely consistent
with it. The solver has found a hole in the specification.

Expected: sat, with a model.
"""

from z3 import Function, ForAll, Implies, Int, IntSort, BoolSort, Not, Solver, sat

months   = Function("months",   IntSort(), IntSort())
approved = Function("approved", IntSort(), BoolSort())

u = Int("u")
s = Solver()
s.add(ForAll([u], Implies(months(u) >= 12, approved(u))))

bob = Int("bob")
s.add(months(bob) == 6)
s.add(Not(approved(bob)))

print(s.check())
assert s.check() == sat, "expected sat"
print(s.model())
print("When you expected a proof and got a model, read the model:")
print("the policy never said anything about service under twelve months.")
