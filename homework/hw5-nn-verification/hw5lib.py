"""HW5 library: the network, the images, VNN-LIB, and three ways to answer a query.

You do not need to edit this file (the checker pins it by SHA-256). Read it: it is short, and
every verdict in the homework comes from one of the three functions at the bottom.

    load_net()            the network's weights: 196 -> 32 -> ReLU -> 32 -> ReLU -> 10
    load_images()         ten MNIST test images (one per digit), 14x14 = 196 pixels in [0, 1]
    forward(W, x)         the network, in numpy (float64)
    parse_vnnlib(text)    a VNN-LIB property -> Spec (input box + the UNSAFE output region)
    compare_specs(a, b)   do two Specs mean the same thing? (a list of differences)

    lirpa_check(W, spec, method)    auto_LiRPA: IBP / CROWN / alpha-CROWN bounds -- sound,
                                    INCOMPLETE: "verified" or "unknown"
    milp_check(W, spec)             an exact mixed-integer encoding solved by HiGHS -- sound and
                                    COMPLETE: "verified", "falsified" (with a counterexample) or
                                    "timeout"
    pgd_attack(W, spec)             projected gradient descent -- finds counterexamples, proves
                                    nothing: "falsified" or "no counterexample found"

A Spec describes the region a VNN-LIB file asserts: inputs in the box [lo, hi], and outputs in a
union of polyhedra, each a list of constraints a . Y <= b. VNN-LIB states the COUNTEREXAMPLE: the
property holds exactly when that region contains no input-output pair of the network.

The images are from MNIST (Yann LeCun, Corinna Cortes, Christopher J.C. Burges;
http://yann.lecun.com/exdb/mnist/), licensed CC BY-SA 3.0, here 2x2-average-pooled to 14x14.
"""
from __future__ import annotations

import math
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
N_IN, N_OUT = 196, 10
TOL = 1e-6


# --------------------------------------------------------------------------- network and data

def load_net() -> dict:
    """The weights, as float64 numpy arrays W1 b1 W2 b2 W3 b3 (Linear layers: y = W x + b)."""
    with np.load(HERE / "net" / "mnist14_mlp.npz") as z:
        return {k: z[k].astype(np.float64) for k in z.files}


def load_images():
    """x: (10, 196) pixels in [0, 1]; y: (10,) labels -- image i is a digit i; idx: MNIST test index."""
    with np.load(HERE / "data" / "mnist14_test.npz") as z:
        return z["x"].astype(np.float64), z["y"].astype(int), z["idx"].astype(int)


def forward(W: dict, x) -> np.ndarray:
    """The network's 10 logits for one input (196,) or a batch (n, 196)."""
    h = np.maximum(0.0, np.asarray(x, np.float64) @ W["W1"].T + W["b1"])
    h = np.maximum(0.0, h @ W["W2"].T + W["b2"])
    return h @ W["W3"].T + W["b3"]


def torch_net(W: dict):
    import torch
    import torch.nn as nn
    net = nn.Sequential(nn.Linear(196, 32), nn.ReLU(), nn.Linear(32, 32), nn.ReLU(), nn.Linear(32, 10))
    with torch.no_grad():
        for layer, (w, b) in zip([net[0], net[2], net[4]], [("W1", "b1"), ("W2", "b2"), ("W3", "b3")]):
            layer.weight.copy_(torch.tensor(W[w], dtype=torch.float32))
            layer.bias.copy_(torch.tensor(W[b], dtype=torch.float32))
    return net.eval()


# --------------------------------------------------------------------------- VNN-LIB

class VnnlibError(ValueError):
    pass


@dataclass
class Spec:
    lo: np.ndarray                      # (196,)
    hi: np.ndarray                      # (196,)
    disjuncts: list = field(default_factory=list)   # list of list of (a (10,), b): a.Y <= b

    def describe(self) -> str:
        return (f"input box: {N_IN} pixels, widths {np.round(self.hi - self.lo, 4).min()}.."
                f"{np.round(self.hi - self.lo, 4).max()}; unsafe outputs: {len(self.disjuncts)} "
                f"disjunct(s) of {sorted({len(d) for d in self.disjuncts})} constraint(s)")


def _tokens(text: str):
    text = re.sub(r";[^\n]*", " ", text)
    return re.findall(r"\(|\)|[^\s()]+", text)


def _parse_sexprs(tokens):
    out, stack = [], []
    for t in tokens:
        if t == "(":
            stack.append([])
        elif t == ")":
            if not stack:
                raise VnnlibError("unbalanced ')'")
            e = stack.pop()
            (stack[-1] if stack else out).append(e)
        else:
            (stack[-1] if stack else out).append(t)
    if stack:
        raise VnnlibError("unbalanced '(' -- a parenthesis is never closed")
    return out


def _num(t: str):
    try:
        return float(t)
    except ValueError:
        return None


def _linear(e, decl):
    """A linear expression -> (coeffs over X, coeffs over Y, constant)."""
    cx, cy = np.zeros(N_IN), np.zeros(N_OUT)
    if isinstance(e, str):
        v = _num(e)
        if v is not None:
            return cx, cy, v
        m = re.fullmatch(r"([XY])_(\d+)", e)
        if not m or e not in decl:
            raise VnnlibError(f"unknown symbol {e!r} (declare it with declare-const first)")
        (cx if m.group(1) == "X" else cy)[int(m.group(2))] = 1.0
        return cx, cy, 0.0
    if not e:
        raise VnnlibError("empty expression ()")
    op, args = e[0], [_linear(a, decl) for a in e[1:]]
    if op == "+":
        return sum(a[0] for a in args), sum(a[1] for a in args), sum(a[2] for a in args)
    if op == "-":
        if len(args) == 1:
            return -args[0][0], -args[0][1], -args[0][2]
        f = args[0]
        return (f[0] - sum(a[0] for a in args[1:]), f[1] - sum(a[1] for a in args[1:]),
                f[2] - sum(a[2] for a in args[1:]))
    if op == "*":
        consts = [a for a in args if not a[0].any() and not a[1].any()]
        if len(args) != 2 or not consts:
            raise VnnlibError("'*' must multiply by a constant (the property must be linear)")
        k = consts[0][2]
        other = args[1] if consts[0] is args[0] else args[0]
        return k * other[0], k * other[1], k * other[2]
    raise VnnlibError(f"unsupported operator {op!r} in an arithmetic expression")


def _atom(e, decl):
    """(<= a b) / (>= a b) / (< ...) / (> ...) -> (cx, cy, c) meaning cx.X + cy.Y + c <= 0."""
    if not isinstance(e, list) or len(e) != 3 or e[0] not in ("<=", ">=", "<", ">"):
        raise VnnlibError(f"expected a comparison (<= a b) or (>= a b), got {_show(e)}")
    l, r = _linear(e[1], decl), _linear(e[2], decl)
    d = tuple(x - y for x, y in zip(l, r)) if e[0] in ("<=", "<") else tuple(y - x for x, y in zip(l, r))
    return d


def _formula(e, decl):
    """A boolean formula over atoms -> DNF: list of conjunctions (lists of atoms)."""
    if isinstance(e, list) and e and e[0] == "and":
        dnf = [[]]
        for sub in e[1:]:
            dnf = [c + d for c in dnf for d in _formula(sub, decl)]
        return dnf
    if isinstance(e, list) and e and e[0] == "or":
        return [c for sub in e[1:] for c in _formula(sub, decl)]
    return [[_atom(e, decl)]]


def _show(e):
    return e if isinstance(e, str) else "(" + " ".join(_show(x) for x in e) + ")"


def parse_vnnlib(text: str) -> Spec:
    """Parse the VNN-LIB subset the homework uses. Raises VnnlibError with a reason on bad syntax."""
    decl, lo, hi, out_parts = set(), np.full(N_IN, -np.inf), np.full(N_IN, np.inf), []
    for e in _parse_sexprs(_tokens(text)):
        if not isinstance(e, list) or not e:
            raise VnnlibError(f"stray token outside a command: {_show(e)}")
        if e[0] == "declare-const":
            if len(e) != 3 or e[2] != "Real" or not re.fullmatch(r"[XY]_\d+", str(e[1])):
                raise VnnlibError(f"bad declaration {_show(e)} (expected (declare-const X_i Real))")
            decl.add(e[1])
            continue
        if e[0] != "assert" or len(e) != 2:
            raise VnnlibError(f"unsupported command {_show(e)[:60]} (only declare-const and assert)")
        dnf = _formula(e[1], decl)
        x_only = all(not a[1].any() for c in dnf for a in c)
        if x_only and len(dnf) == 1 and len(dnf[0]) == 1:
            cx, _, c = dnf[0][0]
            nz = np.flatnonzero(cx)
            if len(nz) != 1:
                raise VnnlibError(f"an input constraint must bound one X_i at a time: {_show(e[1])}")
            i, k = nz[0], cx[nz[0]]
            if k > 0:
                hi[i] = min(hi[i], -c / k)
            else:
                lo[i] = max(lo[i], -c / k)
        elif all(not a[0].any() for c in dnf for a in c):
            out_parts.append([[(cy, -c) for (_, cy, c) in conj] for conj in dnf])
        else:
            raise VnnlibError(f"a constraint mixes inputs and outputs, or puts an input in or/and: "
                              f"{_show(e[1])[:80]}")
    missing_x = [f"X_{i}" for i in range(N_IN) if f"X_{i}" not in decl]
    missing_y = [f"Y_{j}" for j in range(N_OUT) if f"Y_{j}" not in decl]
    if missing_x or missing_y:
        raise VnnlibError(f"not declared: {(missing_x + missing_y)[:4]}... (the network has "
                          f"{N_IN} inputs X_0..X_{N_IN - 1} and {N_OUT} outputs Y_0..Y_{N_OUT - 1})")
    unb = [i for i in range(N_IN) if not (np.isfinite(lo[i]) and np.isfinite(hi[i]))]
    if unb:
        raise VnnlibError(f"input X_{unb[0]} (and {len(unb) - 1} more) has no lower or upper bound")
    if not out_parts:
        raise VnnlibError("no output constraint: the file says nothing about Y")
    dnf = [[]]
    for part in out_parts:                       # top-level asserts are conjoined
        dnf = [c + d for c in dnf for d in part]
    return Spec(lo, hi, dnf)


# --------------------------------------------------------------------------- meaning

def _canon(conj):
    rows = []
    for a, b in conj:
        s = np.abs(a).max()
        if s < 1e-12:
            rows.append(("const", round(float(np.sign(-b)), 0)))   # 0 <= b: true/false constant
            continue
        rows.append((tuple(np.round(a / s, 6)), round(float(b / s), 6)))
    return frozenset(rows)


def _in_region(dnf, Y):
    """Boolean mask: which rows of Y (n, 10) lie in the union of polyhedra."""
    inside = np.zeros(len(Y), bool)
    for conj in dnf:
        m = np.ones(len(Y), bool)
        for a, b in conj:
            m &= Y @ a <= b + 1e-9
        inside |= m
    return inside


def output_samples(seed: int = 0) -> np.ndarray:
    """The fixed sample of output vectors Y on which two output regions are compared. (The legacy
    RandomState stream, which NumPy keeps identical across versions, so stored bits stay valid.)"""
    rng = np.random.RandomState(seed)
    return np.concatenate([rng.normal(0, s, (20000, N_OUT)) for s in (1, 3, 10, 30)])


def region_bits(dnf, seed: int = 0) -> np.ndarray:
    """Which sample points lie in the region, packed 8 to a byte (what the checker stores for a
    property whose exact form it does not print)."""
    return np.packbits(_in_region(dnf, output_samples(seed)))


def _box_diffs(got: Spec, lo, hi) -> list[str]:
    diffs = []
    for name, g, w in (("lower", got.lo, lo), ("upper", got.hi, hi)):
        bad = np.flatnonzero(np.abs(g - w) > TOL)
        if len(bad):
            i = bad[0]
            diffs.append(f"input box: {len(bad)} {name} bound(s) differ, e.g. X_{i}: {g[i]:.6g} "
                         f"vs intended {w[i]:.6g}")
    return diffs


def _region_diffs(got_in: np.ndarray, want_in: np.ndarray, Y: np.ndarray) -> list[str]:
    if not (got_in != want_in).any():
        return []
    k = int(np.flatnonzero(got_in != want_in)[0])
    who = "the file calls it UNSAFE and the intended property does not" if got_in[k] \
        else "the intended property calls it UNSAFE and the file does not"
    return [f"output region differs: at Y = {np.round(Y[k], 2).tolist()} {who} "
            f"({got_in.sum()} vs {want_in.sum()} of {len(Y)} sampled points unsafe)"]


def compare_specs(got: Spec, want: Spec, seed: int = 0) -> list[str]:
    """Differences in MEANING between two specs (empty list = same property).

    Inputs: the two boxes must agree pixel by pixel. Outputs: the two unsafe regions must be the
    same set. Equal canonical forms settle it; otherwise a fixed sample of output vectors is
    searched for a witness, a Y that one spec calls unsafe and the other does not.
    """
    diffs = _box_diffs(got, want.lo, want.hi)
    if {_canon(c) for c in got.disjuncts} != {_canon(c) for c in want.disjuncts}:
        Y = output_samples(seed)
        diffs += _region_diffs(_in_region(got.disjuncts, Y), _in_region(want.disjuncts, Y), Y)
    return diffs


def compare_to_bits(got: Spec, lo, hi, bits: np.ndarray, seed: int = 0) -> list[str]:
    """compare_specs against an intended property known only by its box and region_bits."""
    Y = output_samples(seed)
    want_in = np.unpackbits(bits)[:len(Y)].astype(bool)
    return _box_diffs(got, lo, hi) + _region_diffs(_in_region(got.disjuncts, Y), want_in, Y)


# --------------------------------------------------------------------------- verifiers

@dataclass
class Result:
    verdict: str                       # verified / unknown / falsified / timeout / no counterexample found
    seconds: float
    detail: str = ""
    x: np.ndarray | None = None        # a counterexample input, when one was found
    bounds: list = field(default_factory=list)


def _confirm(W, spec, x, tol: float = 1e-9) -> bool:
    """Is x really a counterexample: inside the box, and its outputs inside the unsafe region?"""
    if np.any(x < spec.lo - 1e-9) or np.any(x > spec.hi + 1e-9):
        return False
    Y = forward(W, x)
    return any(all(Y @ a <= b + tol for a, b in conj) for conj in spec.disjuncts)


def _rows(spec):
    A, b, owner = [], [], []
    for d, conj in enumerate(spec.disjuncts):
        for a, bb in conj:
            A.append(a), b.append(bb), owner.append(d)
    return np.array(A), np.array(b), np.array(owner)


_LIRPA_CACHE = {}


def _bounded(W):
    """auto_LiRPA's wrapped copy of the network (built once per weights dict)."""
    import torch
    from auto_LiRPA import BoundedModule
    key = id(W)
    if key not in _LIRPA_CACHE:
        _LIRPA_CACHE[key] = BoundedModule(torch_net(W), torch.zeros(1, N_IN), verbose=0)
    return _LIRPA_CACHE[key]


def lirpa_check(W: dict, spec: Spec, method: str = "CROWN") -> Result:
    """Sound but incomplete: bound every output constraint a.Y over the input box with auto_LiRPA.

    A disjunct is ruled out when some constraint a.Y <= b has lower bound of a.Y above b. If every
    disjunct is ruled out the property is VERIFIED; otherwise the answer is UNKNOWN -- the bound
    was too loose to decide, which says nothing about whether a counterexample exists.
    method: "IBP", "CROWN" or "alpha-CROWN".
    """
    import torch
    from auto_LiRPA import BoundedTensor
    from auto_LiRPA.perturbations import PerturbationLpNorm
    t0 = time.perf_counter()
    A, b, owner = _rows(spec)
    model = _bounded(W)
    lo = torch.tensor(spec.lo, dtype=torch.float32)[None]
    hi = torch.tensor(spec.hi, dtype=torch.float32)[None]
    ptb = PerturbationLpNorm(norm=float("inf"), x_L=lo, x_U=hi)
    C = torch.tensor(A, dtype=torch.float32)[None]
    if method == "alpha-CROWN":
        model.set_bound_opts({"optimize_bound_args": {"iteration": 50, "lr_alpha": 0.1,
                                                      "verbosity": 0}})
    lb, _ = model.compute_bounds(x=(BoundedTensor((lo + hi) / 2, ptb),), C=C, method=method,
                                 bound_upper=False)
    lb = lb.detach().numpy()[0].astype(np.float64)
    ruled_out = [bool(np.any(lb[owner == d] > b[owner == d] + 1e-7)) for d in range(len(spec.disjuncts))]
    verdict = "verified" if all(ruled_out) else "unknown"
    gap = [float(np.max(lb[owner == d] - b[owner == d])) for d in range(len(spec.disjuncts))]
    return Result(verdict, time.perf_counter() - t0,
                  f"{sum(ruled_out)}/{len(ruled_out)} disjuncts ruled out", bounds=gap)


def _ibp(W, lo, hi):
    """Interval bounds on every pre-activation."""
    bounds, l, u = [], lo, hi
    for wk, bk in (("W1", "b1"), ("W2", "b2")):
        Wp, Wn = np.maximum(W[wk], 0), np.minimum(W[wk], 0)
        pl, pu = Wp @ l + Wn @ u + W[bk], Wp @ u + Wn @ l + W[bk]
        bounds.append((pl, pu))
        l, u = np.maximum(pl, 0), np.maximum(pu, 0)
    return bounds


def _pre_bounds(W, spec):
    """Bounds on each hidden layer's pre-activations: the tighter of interval arithmetic and
    CROWN (both sound), widened by 1e-5 so float32 rounding in CROWN cannot cut off a real point.
    These are the big-M constants of the MILP; tighter constants mean fewer 0/1 variables."""
    import torch
    from auto_LiRPA import BoundedTensor
    from auto_LiRPA.perturbations import PerturbationLpNorm
    ibp = _ibp(W, spec.lo, spec.hi)
    model = _bounded(W)
    lo = torch.tensor(spec.lo, dtype=torch.float32)[None]
    hi = torch.tensor(spec.hi, dtype=torch.float32)[None]
    ptb = PerturbationLpNorm(norm=float("inf"), x_L=lo, x_U=hi)
    model.compute_bounds(x=(BoundedTensor((lo + hi) / 2, ptb),), method="CROWN")
    relus = [n for n in model.nodes() if type(n).__name__ == "BoundRelu"]
    out = []
    for (il, iu), r in zip(ibp, relus):
        cl = r.inputs[0].lower.detach().numpy()[0].astype(np.float64) - 1e-5
        cu = r.inputs[0].upper.detach().numpy()[0].astype(np.float64) + 1e-5
        out.append((np.maximum(il, cl), np.minimum(iu, cu)))
    return out


def milp_check(W: dict, spec: Spec, time_limit: float = 60.0) -> Result:
    """Sound and complete (up to the time limit): the network as a mixed-integer linear program.

    Every ReLU whose input can be both negative and positive gets a 0/1 variable (the big-M
    encoding, with the bounds from _pre_bounds). Disjuncts that CROWN already rules out are
    skipped (that is sound). For each remaining disjunct HiGHS looks for an input in the box
    whose outputs satisfy all of its constraints a.Y <= b. Found: a counterexample, checked
    again by a forward pass -- FALSIFIED. None for any disjunct: VERIFIED.
    """
    import highspy
    t0 = time.perf_counter()
    lo, hi = spec.lo.astype(np.float64), spec.hi.astype(np.float64)
    screen = lirpa_check(W, spec, "CROWN")
    todo = [d for d, g in enumerate(screen.bounds) if g <= 1e-7]
    if not todo:
        return Result("verified", time.perf_counter() - t0, "CROWN ruled out every disjunct")
    todo.sort(key=lambda d: screen.bounds[d])           # most likely violated first
    pre = _pre_bounds(W, spec)
    inf = highspy.kHighsInf
    for conj_i in todo:
        conj = spec.disjuncts[conj_i]
        h = highspy.Highs()
        h.setOptionValue("output_flag", False)
        h.setOptionValue("threads", 1)
        h.setOptionValue("random_seed", 0)
        remaining = time_limit - (time.perf_counter() - t0)
        if remaining <= 0:
            return Result("timeout", time.perf_counter() - t0, f"time limit {time_limit}s")
        h.setOptionValue("time_limit", float(remaining))
        col_lo, col_hi, integer, rows = [], [], [], []   # rows: (lb, ub, {col: coef})

        def add(l, u, n, is_int=False):
            start = len(col_lo)
            col_lo.extend(np.broadcast_to(l, n).astype(float)); col_hi.extend(np.broadcast_to(u, n).astype(float))
            if is_int:
                integer.extend(range(start, start + n))
            return np.arange(start, start + n)

        x = add(lo, hi, N_IN)
        prev = x
        for (wk, bk), (pl, pu) in zip((("W1", "b1"), ("W2", "b2")), pre):
            n = len(pl)
            zhat = add(pl, pu, n)
            for k in range(n):                               # zhat = W prev + b
                rows.append((W[bk][k], W[bk][k], np.r_[zhat[k], prev], np.r_[1.0, -W[wk][k]]))
            z = add(0.0, np.maximum(pu, 0.0), n)
            for k in range(n):
                if pl[k] >= 0:                               # always active: z = zhat
                    rows.append((0, 0, [z[k], zhat[k]], [1, -1]))
                elif pu[k] <= 0:                             # always inactive: z = 0
                    rows.append((0, 0, [z[k]], [1]))
                else:                                        # unstable: a 0/1 variable d
                    d = add(0, 1, 1, True)[0]
                    rows.append((0, inf, [z[k], zhat[k]], [1, -1]))                   # z >= zhat
                    rows.append((-inf, -pl[k], [z[k], zhat[k], d], [1, -1, -pl[k]]))  # z <= zhat - l(1-d)
                    rows.append((-inf, 0, [z[k], d], [1, -pu[k]]))                    # z <= u d
            prev = z
        y = add(-inf, inf, N_OUT)
        for k in range(N_OUT):                               # y = W3 prev + b3
            rows.append((W["b3"][k], W["b3"][k], np.r_[y[k], prev], np.r_[1.0, -W["W3"][k]]))
        for a, b in conj:                                    # the disjunct: a.y <= b
            rows.append((-inf, b, y, a))
        h.addVars(len(col_lo), np.array(col_lo), np.array(col_hi))
        for j in integer:
            h.changeColIntegrality(int(j), highspy.HighsVarType.kInteger)
        starts, idx, val, rl, ru = [], [], [], [], []
        for lb_, ub_, ii, vv in rows:
            starts.append(len(idx)); idx.extend(np.asarray(ii, int)); val.extend(np.asarray(vv, float))
            rl.append(lb_); ru.append(ub_)
        h.addRows(len(rows), np.array(rl, float), np.array(ru, float), len(idx),
                  np.array(starts, np.int32), np.array(idx, np.int32), np.array(val, float))
        h.run()
        status = h.modelStatusToString(h.getModelStatus())
        if status == "Infeasible":
            continue
        if status == "Time limit reached":
            return Result("timeout", time.perf_counter() - t0, f"time limit {time_limit}s, disjunct {conj_i}")
        if status != "Optimal":
            return Result("timeout", time.perf_counter() - t0, f"HiGHS stopped: {status}")
        cex = np.clip(np.array(h.getSolution().col_value)[x], lo, hi)
        if _confirm(W, spec, cex, tol=1e-6):
            return Result("falsified", time.perf_counter() - t0, f"counterexample for disjunct {conj_i}", x=cex)
        return Result("timeout", time.perf_counter() - t0,
                      f"the MILP's point for disjunct {conj_i} fails the forward-pass check (numerics)")
    return Result("verified", time.perf_counter() - t0, f"{len(todo)} disjunct(s) unreachable by MILP, "
                  f"{len(spec.disjuncts) - len(todo)} by CROWN")


def pgd_attack(W: dict, spec: Spec, steps: int = 200, restarts: int = 5, seed: int = 0) -> Result:
    """Search for a counterexample by projected gradient descent. Finding one proves the property
    FALSE (it is checked by a forward pass). Not finding one proves nothing."""
    import torch
    t0 = time.perf_counter()
    net = torch_net(W).double()
    lo, hi = torch.tensor(spec.lo), torch.tensor(spec.hi)
    g = torch.Generator().manual_seed(seed)
    for conj in spec.disjuncts:
        A = torch.tensor(np.array([a for a, _ in conj]))
        b = torch.tensor(np.array([bb for _, bb in conj]))
        step = float((hi - lo).max()) / 20 + 1e-12
        for r in range(restarts):
            x = (lo + (hi - lo) * torch.rand(len(lo), generator=g, dtype=torch.float64)).requires_grad_(True)
            for _ in range(steps):
                viol = (A @ net(x) - b).max()            # <= 0 means inside the unsafe region
                if viol.item() <= 0:
                    break
                viol.backward()
                with torch.no_grad():
                    x -= step * x.grad.sign()
                    x.copy_(torch.max(torch.min(x, hi), lo))
                x.grad = None
            cand = x.detach().numpy()
            if _confirm(W, spec, cand):
                return Result("falsified", time.perf_counter() - t0, f"restart {r}", x=cand)
    return Result("no counterexample found", time.perf_counter() - t0,
                  f"{restarts} restarts x {steps} steps per disjunct")
