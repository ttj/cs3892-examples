"""Session 24's toy network, and four ways to ask whether it is robust -- small enough to check by hand.

    x = (x1, x2)  ->  z = W1 x + b1  ->  h = ReLU(z)  ->  y = W2 h + b2      (2 -> 2 -> 2)

Class 0 wins at x0 = (0.45, 0.55). ROBUST AT eps means: for every x with |x - x0|_inf <= eps, class 0
still wins, i.e. the margin y0 - y1 stays > 0. Four answers, from cheapest to exact:

    ibp(eps)      interval bound propagation: push the box through, layer by layer
    crown(eps)    CROWN: bound each unstable ReLU by lines, then minimise a LINEAR function of x
    exact(eps)    the true minimum margin: a ReLU network is piecewise linear, so in 2-D the minimum
                  is at a vertex of the pieces inside the box
    bab(eps)      branch and bound: split the box until CROWN verifies every piece (or a piece's
                  centre is a counterexample)

`lirpa(method, eps)` asks auto_LiRPA (the alpha,beta-CROWN team's library, HW5's tool) for the same
bounds, so the hand-written IBP and CROWN can be checked against it. Nothing here is HW5's network.
"""
from __future__ import annotations

import itertools

import numpy as np

W1 = np.array([[-1.0, 1.0], [-1.0, 2.0]])
b1 = np.array([0.0, -0.5])
W2 = np.array([[1.0, -1.0], [-1.0, 1.0]])
b2 = np.array([0.25, -0.25])
X0 = np.array([0.45, 0.55])
C = W2[0] - W2[1]          # margin = C . h + D
D = b2[0] - b2[1]


def forward(x):
    return W2 @ np.maximum(W1 @ np.asarray(x, float) + b1, 0) + b2


def margin(x):
    y = forward(x)
    return float(y[0] - y[1])


def box(eps, x0=X0):
    return x0 - eps, x0 + eps


def pre_bounds(lo, hi):
    """Exact bounds on z = W1 x + b1 over the box (one linear layer: interval arithmetic is exact)."""
    return (np.minimum(W1 * lo, W1 * hi).sum(1) + b1, np.maximum(W1 * lo, W1 * hi).sum(1) + b1)


def ibp(eps, x0=X0):
    """IBP: h in [relu(l), relu(u)] per neuron, then the worst case of C . h + D, neuron by neuron."""
    l, u = pre_bounds(*box(eps, x0))
    hl, hu = np.maximum(l, 0), np.maximum(u, 0)
    return float(D + sum(C[i] * (hl[i] if C[i] >= 0 else hu[i]) for i in range(2)))


def relax(l, u, want_lower):
    """A line a*z + t bounding relu(z) on [l, u], from below (want_lower) or from above."""
    if l >= 0:
        return 1.0, 0.0                     # active: relu(z) = z
    if u <= 0:
        return 0.0, 0.0                     # inactive: relu(z) = 0
    if want_lower:
        return (1.0 if u > -l else 0.0), 0.0   # CROWN's choice of lower slope
    s = u / (u - l)
    return s, -s * l                        # the chord from (l, 0) to (u, u)


def crown(eps, x0=X0, lo=None, hi=None):
    """CROWN: margin >= a . x + k on the box; the minimum of a linear function over a box is exact."""
    if lo is None:
        lo, hi = box(eps, x0)
    l, u = pre_bounds(lo, hi)
    a, k = np.zeros(2), D
    for i in range(2):
        s, t = relax(l[i], u[i], want_lower=C[i] >= 0)   # C[i] < 0 needs relu's UPPER bound
        a += C[i] * s * W1[i]
        k += C[i] * (s * b1[i] + t)
    return float(np.minimum(a * lo, a * hi).sum() + k)


def exact(eps, x0=X0):
    """The true minimum margin over the box: check every vertex of the linear pieces inside it."""
    lo, hi = box(eps, x0)
    pts = [np.array(p) for p in itertools.product([lo[0], hi[0]], [lo[1], hi[1]])]
    for w, b in zip(W1, b1):                       # where a neuron's line z = 0 crosses the box edge
        for j in range(2):
            for v in (lo[j], hi[j]):
                p = np.zeros(2)
                p[j], p[1 - j] = v, -(b + w[j] * v) / w[1 - j]
                if lo[1 - j] - 1e-12 <= p[1 - j] <= hi[1 - j] + 1e-12:
                    pts.append(p)
    p = np.linalg.solve(W1, -b1)                   # where both lines cross
    if np.all(p >= lo - 1e-12) and np.all(p <= hi + 1e-12):
        pts.append(p)
    worst = min(pts, key=margin)
    return margin(worst), worst


def bab(eps, x0=X0, depth=12):
    """Branch and bound on the input box: CROWN each piece; split the unverified ones in two."""
    todo, pieces = [box(eps, x0)], 0
    while todo:
        lo, hi = todo.pop()
        pieces += 1
        if crown(None, lo=lo, hi=hi) > 0:
            continue                               # this piece is verified
        mid = (lo + hi) / 2
        if margin(mid) <= 0:
            return "falsified", pieces, mid
        if (hi - lo).max() < 2.0 ** -depth:
            return "unknown", pieces, None
        j = int(np.argmax(hi - lo))                # split the longer side
        left_hi, right_lo = hi.copy(), lo.copy()
        left_hi[j] = right_lo[j] = mid[j]
        todo += [(lo, left_hi), (right_lo, hi)]
    return "verified", pieces, None


def frontier(lower_bound, top=0.5, steps=40):
    """The largest eps whose lower bound is still > 0 (binary search; the bound shrinks as eps grows)."""
    a, b = 0.0, top
    for _ in range(steps):
        m = (a + b) / 2
        a, b = (m, b) if lower_bound(m) > 0 else (a, m)
    return a


def vnnlib(eps, x0=X0):
    """The query in VNN-LIB: the input box, and the UNSAFE outputs (class 1 at least as large)."""
    lo, hi = box(eps, x0)
    return "\n".join([
        "; robustness of the toy network at x0, radius eps (infinity norm)",
        "(declare-const X_0 Real)", "(declare-const X_1 Real)",
        "(declare-const Y_0 Real)", "(declare-const Y_1 Real)",
        f"(assert (>= X_0 {lo[0]:.2f})) (assert (<= X_0 {hi[0]:.2f}))",
        f"(assert (>= X_1 {lo[1]:.2f})) (assert (<= X_1 {hi[1]:.2f}))",
        "; the counterexample region: class 0 does NOT win",
        "(assert (>= Y_1 Y_0))"])


def lirpa(method, eps, x0=X0):
    """auto_LiRPA's lower bound on the margin: method "IBP", "CROWN" or "alpha-CROWN"."""
    import torch
    from auto_LiRPA import BoundedModule, BoundedTensor
    from auto_LiRPA.perturbations import PerturbationLpNorm
    torch.set_default_dtype(torch.float64)
    net = torch.nn.Sequential(torch.nn.Linear(2, 2), torch.nn.ReLU(), torch.nn.Linear(2, 2))
    with torch.no_grad():
        for layer, (w, b) in zip((net[0], net[2]), ((W1, b1), (W2, b2))):
            layer.weight.copy_(torch.tensor(w)); layer.bias.copy_(torch.tensor(b))
    x = torch.tensor([x0])
    bm = BoundedModule(net, torch.zeros(1, 2), verbose=0)
    bx = BoundedTensor(x, PerturbationLpNorm(norm=np.inf, eps=eps))
    spec = torch.tensor([[[1.0, -1.0]]])                   # y0 - y1
    name = {"IBP": "IBP", "CROWN": "CROWN", "alpha-CROWN": "CROWN-Optimized"}[method]
    return float(bm.compute_bounds(x=(bx,), method=name, C=spec)[0].item())
