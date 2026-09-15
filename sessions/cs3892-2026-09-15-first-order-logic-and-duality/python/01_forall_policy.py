"""Slide 21 -- a policy that covers users you have never seen.

One assertion covers every user at once. `bob` is created AFTER the rule and
the rule still binds him, which the propositional encoding on slide 15 could
not do: it had to name every user in advance.

Expected: unsat -- no such user can exist, so the policy is enforced.
"""

from z3 import Function, ForAll, Implies, Int, IntSort, BoolSort, Not, Solver, unsat

months   = Function("months",   IntSort(), IntSort())
approved = Function("approved", IntSort(), BoolSort())

u = Int("u")
s = Solver()
s.add(ForAll([u], Implies(months(u) >= 12, approved(u))))

bob = Int("bob")
s.add(months(bob) == 18)
s.add(Not(approved(bob)))

print(s.check())
assert s.check() == unsat, "expected unsat"
print("No 18-month user can be unapproved. Z3 never enumerated the domain --")
print("it instantiated the quantifier with the one term it needed: bob.")
