"""Slide 22 -- where every counterexample comes from.

    Not(ForAll x. P(x))   ===   Exists x. Not P(x)

De Morgan, one level up: a ForAll is a conjunction over the domain and an
Exists is a disjunction. Asserting that the two sides DIFFER is unsat, which is
the machine-checked version of the proof done on the board on September 10.

This equivalence is the verification loop itself. "For every reachable state,
nothing bad" negates into "there exists a reachable state where something bad",
and that is the query the solver is actually given.

Expected: unsat.
"""

from z3 import BoolSort, Exists, ForAll, Function, Int, IntSort, Not, Solver, unsat

P = Function("P", IntSort(), BoolSort())
x = Int("x")

lhs = Not(ForAll([x], P(x)))
rhs = Exists([x], Not(P(x)))

s = Solver()
s.add(Not(lhs == rhs))          # can the two sides ever disagree?

print(s.check())
assert s.check() == unsat, "expected unsat"
print("They can never disagree. Negating a property IS forming the")
print("counterexample query -- there is no separate step.")
