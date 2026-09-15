"""Slide 18 -- quantifier order, the direction that does NOT hold.

Sess(u, s) is true exactly when s == u: every user has their own session and
no two users share one. Then

    ForAll u. Exists s. Sess(u, s)    holds -- take s = u
    Exists s. ForAll u. Sess(u, s)    fails -- no single s equals every u

`sat` is the proof that the two orderings are different specifications. In a
security property, the difference between them is usually the vulnerability.

Expected: sat.
"""

from z3 import Exists, ForAll, Int, Not, Solver, sat

u, v = Int("u"), Int("v")


def Sess(user, session):
    """Each user's own session, and nobody else's."""
    return user == session


solver = Solver()
solver.add(ForAll([u], Exists([v], Sess(u, v))))
solver.add(Not(Exists([v], ForAll([u], Sess(u, v)))))

print(solver.check())
assert solver.check() == sat, "expected sat"
print("ForAll-Exists does NOT imply Exists-ForAll. Swapping them is a")
print("different specification, not a rearrangement of the same one.")
