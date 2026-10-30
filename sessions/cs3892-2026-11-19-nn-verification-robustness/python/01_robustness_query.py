"""Session 24 -- local robustness as a formal query, on a network small enough to check by hand.

The toy network (nnv.py): 2 inputs -> 2 ReLU neurons -> 2 outputs. At x0 = (0.45, 0.55) class 0
wins with margin y0 - y1 = 0.4. "Robust at radius eps" is a statement about INFINITELY many inputs:
for every x with |x - x0|_inf <= eps, class 0 still wins. VNN-LIB, the competition format, writes the
COUNTEREXAMPLE region: inputs in the box AND class 1 at least as large. Robust iff that is empty.

Expected: the assertions at the bottom hold.
"""
import numpy as np

import nnv

y = nnv.forward(nnv.X0)
print("W1 =", nnv.W1.tolist(), " b1 =", nnv.b1.tolist())
print("W2 =", nnv.W2.tolist(), " b2 =", nnv.b2.tolist())
print(f"x0 = {nnv.X0.tolist()}   y = {np.round(y, 3).tolist()}   margin y0 - y1 = {nnv.margin(nnv.X0):.2f}")
print("\nThe query at eps = 0.1, in VNN-LIB:\n")
q = nnv.vnnlib(0.1)
print(q)
assert abs(nnv.margin(nnv.X0) - 0.4) < 1e-12 and y.argmax() == 0
assert "(assert (>= X_0 0.35)) (assert (<= X_0 0.55))" in q and "(assert (>= Y_1 Y_0))" in q
print("\nrobust at eps  <=>  no input in the box makes Y_1 >= Y_0  <=>  the VNN-LIB region is empty")
