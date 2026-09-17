"""Slide 28 -- a bit-vector question is a SAT question underneath.

Session 5 asked whether `x + 1 > x` can be false for an 8-bit signed value, and
Z3 answered `sat` with x = 127. It did not reason about integers to get there.
It BIT-BLASTED: eight boolean variables for the bits of x, the ripple-carry
adder written out as clauses, the comparison written out as clauses -- and then
a SAT solver on the result.

This runs the same query two ways and shows the boolean problem underneath.

Expected: sat, x = 127, and a CNF with far more variables than the one you wrote.
"""

from z3 import BitVec, BitVecVal, Not, Solver, Tactic, Then, sat

x = BitVec("x", 8)
claim = Not(x + 1 > x)           # can x+1 > x fail?

s = Solver()
s.add(claim)
print(s.check())
assert s.check() == sat, "expected sat"
print("counterexample:", s.model())

# The same formula, pushed through the bit-blaster and into CNF.
cnf = Then(Tactic("simplify"), Tactic("bit-blast"), Tactic("tseitin-cnf"))(claim)
goal = cnf[0]
print(f"\nafter bit-blasting and Tseitin: {len(goal)} clauses")
print("You wrote one line about an 8-bit number. The solver answered a")
print("boolean satisfiability problem with clauses over the individual bits --")
print("which is why everything in Unit 3 comes back to SAT.")
