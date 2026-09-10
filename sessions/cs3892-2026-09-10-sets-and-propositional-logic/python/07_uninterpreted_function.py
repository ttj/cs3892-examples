"""Slide 32 -- reasoning about code you cannot see.

Z3 has never seen `f`: no body, no definition. It knows exactly one thing --
f is a function, so equal inputs give equal outputs (congruence). That alone
refutes this, and it is how a verifier reasons about a library call it has no
source for.

Expected: unsat.
"""

from z3 import Function, Int, IntSort, Not, Solver, unsat

f = Function("f", IntSort(), IntSort())   # uninterpreted: no body at all
a, b = Int("a"), Int("b")

s = Solver()
s.add(a == b)
s.add(Not(f(a) == f(b)))

print(s.check())
assert s.check() == unsat, "expected unsat"
print("Congruence alone is enough. No definition of f was ever needed.")
