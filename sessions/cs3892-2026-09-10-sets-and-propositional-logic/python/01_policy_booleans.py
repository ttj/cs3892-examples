"""Slide 27 -- the policy, encoded. Propositional logic, nothing more.

An employee may take extended leave if employed at least twelve months and
holding unused leave. Contractors are never eligible. The model has told a
contractor with eleven months' service they are eligible.

Expected: unsat -- the answer contradicts the policy, and the solver proves it.
"""

from z3 import Bool, And, Not, Solver, unsat

e = Bool("e")  # employed 12 months or more
u = Bool("u")  # unused leave remains
c = Bool("c")  # is a contractor
L = Bool("L")  # eligible

s = Solver()
s.add(L == And(e, u, Not(c)))          # the policy
s.add(c, Not(e), L)                    # the claim

print(s.check())
assert s.check() == unsat, "expected unsat"
print("The claim contradicts the policy. No world satisfies all four at once.")
