"""Slide 21 -- quantifier order, the direction that DOES hold.

    Exists s. ForAll u. Sess(u, s)    "one session serves everyone"
    ForAll u. Exists s. Sess(u, s)    "everyone has a session, maybe their own"

The first implies the second. Assert the first and the negation of the second;
unsat means no counterexample exists, so the implication is valid.

Expected: unsat.
"""

from z3 import Bool, BoolSort, Const, DeclareSort, Exists, ForAll, Function, Not, Solver, unsat

U = DeclareSort("U")          # users
S = DeclareSort("S")          # sessions
Sess = Function("Sess", U, S, BoolSort())

u, s_ = Const("u", U), Const("s", S)

solver = Solver()
solver.add(Exists([s_], ForAll([u], Sess(u, s_))))
solver.add(Not(ForAll([u], Exists([s_], Sess(u, s_)))))

print(solver.check())
assert solver.check() == unsat, "expected unsat"
print("Exists-ForAll implies ForAll-Exists. This direction is free.")
