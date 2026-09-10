"""Slide 31 -- arithmetic your machine does not do.

Is x + 1 > x ever false? In mathematics, no. On a machine, yes. The solver
returns the exact value where it breaks: signed 8-bit 127 + 1 = -128. This is
the class of bug that destroyed Ariane 5 flight 501 in 1996.

Expected: sat, x = 127.
"""

from z3 import BitVec, BitVecVal, Not, Solver, sat

x = BitVec("x", 8)          # a fixed-width machine word, not a number
s = Solver()
s.add(Not(x + 1 > x))       # > on a BitVec is SIGNED comparison

print(s.check())
assert s.check() == sat, "expected sat"

m = s.model()
val = m[x].as_signed_long()
print("model:", m, "-> signed", val)
assert val == 127, f"expected the wraparound point, got {val}"
print(f"x = {val}; x + 1 wraps to {(val + 1 + 128) % 256 - 128}. "
      "The counterexample is not a hint -- it is the input.")
