"""Slide 32 -- encode a problem, ask for a witness.

Five regions in a ring, each adjacent to the next, three colours. The formula
says nothing about how to colour it -- only what a legal colouring is. The
solver finds one. This is the shape of most of HW1.

Expected: sat, with a model.
"""

from z3 import Int, Solver, sat

r = [Int(f"r{i}") for i in range(5)]

s = Solver()
for x in r:
    s.add(x >= 1, x <= 3)                     # three colours, named 1 2 3
for i in range(5):
    s.add(r[i] != r[(i + 1) % 5])             # neighbours differ, around the ring

print(s.check())
assert s.check() == sat, "expected sat"
m = s.model()
print("a legal colouring:", [m[x].as_long() for x in r])
print("Five regions in a ring need three colours, and the solver found one")
print("without being told a single thing about how to search.")
