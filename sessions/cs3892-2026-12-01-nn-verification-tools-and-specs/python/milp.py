"""An exact verifier for the toy network: a mixed-integer linear program, solved by HiGHS.

Each unstable ReLU h = max(z, 0) with z in [l, u] becomes four linear constraints and one binary
variable a (a = 1: active, h = z; a = 0: inactive, h = 0):

    h >= 0,   h >= z,   h <= z - l (1 - a),   h <= u a

These are exact, not a relaxation: for a = 0 they force h = 0 (so z <= 0), for a = 1 they force
h = z (so z >= 0). Minimising the margin over the box then gives the TRUE minimum, so the MILP is
sound AND complete -- the price is a search over the binaries, exponential in the worst case. HW5
uses the same encoding (with CROWN's bounds as l and u) on a network with 64 ReLUs.
"""
from __future__ import annotations

import highspy
import numpy as np

import toy


def solve(lo, hi, time_limit=None):
    """Minimise the margin y0 - y1 over the box [lo, hi]. -> (status, min margin, argmin x)."""
    l, u = toy.pre_bounds(np.asarray(lo, float), np.asarray(hi, float))
    # plain floats (numpy scalars break highspy's expressions), and 1e-16 rounding noise snapped to 0:
    # HiGHS rejects a coefficient that small, and a bound of exactly 0 means the neuron is stable.
    l = [0.0 if abs(v) < 1e-9 else float(v) for v in l]
    u = [0.0 if abs(v) < 1e-9 else float(v) for v in u]
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    if time_limit is not None:
        h.setOptionValue("time_limit", float(time_limit))
    inf = highspy.kHighsInf
    x = [h.addVariable(lb=float(lo[j]), ub=float(hi[j])) for j in range(2)]
    hs = []
    for i in range(2):
        z = float(toy.W1[i, 0]) * x[0] + float(toy.W1[i, 1]) * x[1] + float(toy.b1[i])
        if l[i] >= 0:                                  # stable, active
            hi_ = h.addVariable(lb=-inf, ub=inf)
            h.addConstr(hi_ == z)
        elif u[i] <= 0:                                # stable, inactive
            hi_ = h.addVariable(lb=0, ub=0)
        else:                                          # unstable: the big-M encoding
            hi_ = h.addVariable(lb=0, ub=inf)
            a = h.addIntegral(lb=0, ub=1)
            h.addConstr(hi_ >= z)
            h.addConstr(hi_ <= z - l[i] * (1 - a))
            h.addConstr(hi_ <= u[i] * a)
        hs.append(hi_)
    h.minimize(float(toy.C[0]) * hs[0] + float(toy.C[1]) * hs[1] + float(toy.D))
    status = h.modelStatusToString(h.getModelStatus())
    if status != "Optimal":
        return "timeout" if "limit" in status.lower() else status, None, None
    sol = h.getSolution().col_value
    return "optimal", float(h.getInfo().objective_function_value), np.array(sol[:2])


def verify(x0, eps, time_limit=None):
    """'verified' (min margin > 0), 'falsified' (with an input), or 'timeout'."""
    lo, hi = np.asarray(x0, float) - eps, np.asarray(x0, float) + eps
    status, m, x = solve(lo, hi, time_limit)
    if status != "optimal":
        return "timeout", None, None
    return ("verified" if m > 0 else "falsified"), m, x
