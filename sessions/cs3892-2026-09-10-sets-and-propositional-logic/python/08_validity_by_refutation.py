"""Slide 23 -- the identity every verifier is built on.

    phi is valid  <=>  (not phi) is unsatisfiable

A solver has no "is it valid?" button. To show p OR (not p) is a tautology you
assert its NEGATION and watch the solver fail to satisfy it.

Expected: unsat -- therefore the formula is valid.
"""

from z3 import Bool, Not, Or, Solver, sat, unsat

p = Bool("p")
phi = Or(p, Not(p))

s = Solver()
s.add(Not(phi))                 # ask for a counterexample to phi
r = s.check()
print(r)
assert r == unsat, "expected unsat"
print("No interpretation falsifies it, so p OR (not p) is VALID.")

# And the converse direction, to show the two questions are different:
s2 = Solver()
s2.add(phi)
assert s2.check() == sat
print("It is also satisfiable -- but satisfiable and valid are not the same "
      "question, and only one of them a solver answers directly.")
