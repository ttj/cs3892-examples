"""Slide 23 -- "Only users with an active session may read a document."

    correct:   ForAll u,d. Reads(u,d) => Active(u)
    reversed:  ForAll u,d. Active(u)  => Reads(u,d)

These are not the same claim, and `sat` proves it: there is a world where the
correct reading holds and the reversed one fails. Z3 finds the simplest one --
nobody reads anything and everybody is active.

"Only A may B" becomes B => A, never A => B. The solver will happily prove the
reversed version without ever mentioning that you asked the wrong question.

Expected: sat.
"""

from z3 import BoolSort, ForAll, Function, Implies, Int, IntSort, Not, Solver, sat

Reads  = Function("Reads",  IntSort(), IntSort(), BoolSort())
Active = Function("Active", IntSort(), BoolSort())

u, d = Int("u"), Int("d")

correct  = ForAll([u, d], Implies(Reads(u, d), Active(u)))
reversed_ = ForAll([u, d], Implies(Active(u), Reads(u, d)))

s = Solver()
s.add(correct)
s.add(Not(reversed_))

print(s.check())
assert s.check() == sat, "expected sat"
print(s.model())
print("A world satisfying the requirement and violating the reversed reading.")
print("The direction of the implication is the whole specification.")
