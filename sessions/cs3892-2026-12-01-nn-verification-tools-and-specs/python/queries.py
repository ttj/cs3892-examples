"""The 25 robustness queries session 25 asks of the toy network: 5 points x 5 radii.

Every point is classified 0; no query sits exactly on the boundary (|min margin| >= 0.04), so
"verified" and "falsified" are never a matter of rounding.
"""
import numpy as np

POINTS = [(0.45, 0.55), (0.6, 0.5), (0.3, 0.3), (0.5, 0.65), (0.2, 0.4)]
RADII = [0.04, 0.08, 0.12, 0.16, 0.22]
QUERIES = [(np.array(p), e) for p in POINTS for e in RADII]
