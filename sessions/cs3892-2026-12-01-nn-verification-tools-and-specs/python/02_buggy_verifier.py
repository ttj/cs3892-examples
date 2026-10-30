"""Session 25 -- what the cross-check is for: a verifier with one plausible bug.

`buggy_crown` is CROWN with the chord's intercept dropped: it bounds an unstable ReLU from above by
s*z instead of s*(z - l). That line lies BELOW relu(z) wherever z < 0, so the bound is no longer an
upper bound, and the margin's lower bound comes out too high. The result is a verifier that says
"verified" for properties that are false. Run against the exact MILP on the same 25 queries, the
bug shows twice: as verdicts in the forbidden cell, and as lower bounds ABOVE the true minimum --
the second appears even on queries where the two verdicts happen to agree.

Expected: the assertions at the bottom hold.
"""
import numpy as np

import milp
import toy
from queries import QUERIES


def buggy_crown(eps, x0):
    lo, hi = x0 - eps, x0 + eps
    l, u = toy.pre_bounds(lo, hi)
    a, k = np.zeros(2), toy.D
    for i in range(2):
        if l[i] >= 0:
            s, t = 1.0, 0.0
        elif u[i] <= 0:
            s, t = 0.0, 0.0
        elif toy.C[i] >= 0:
            s, t = (1.0 if u[i] > -l[i] else 0.0), 0.0
        else:
            s, t = u[i] / (u[i] - l[i]), 0.0     # BUG: should be -s * l[i]
        a += toy.C[i] * s * toy.W1[i]
        k += toy.C[i] * (s * toy.b1[i] + t)
    return float(np.minimum(a * lo, a * hi).sum() + k)


unsound, too_high = [], []
for x0, eps in QUERIES:
    b = buggy_crown(eps, x0)
    v, m, x = milp.verify(x0, eps)
    if b > 0 and v == "falsified":
        unsound.append((x0, eps, b, m, x))
    if b > m + 1e-9:
        too_high.append((x0, eps))
print(f"buggy verifier says VERIFIED, the MILP has a counterexample: {len(unsound)} of 25")
for x0, eps, b, m, x in unsound:
    print(f"  x0 {x0.tolist()}  eps {eps:.2f}: bound {b:+.3f}; MILP min {m:+.3f} at {np.round(x, 3).tolist()}"
          f" (margin there {toy.margin(x):+.3f})")
print(f"\nbound above the true minimum (impossible for a sound method): {len(too_high)} of 25")
assert len(unsound) == 4 and all(toy.margin(x) < 0 for *_, x in unsound)
assert len(too_high) > len(unsound)
print("the cross-check catches it -- and the bound check catches it on more queries than the verdicts do")
