"""HW5 Part 2 -- the eps frontier.

For each image, find by binary search
    eps_C  the largest eps that CROWN verifies,
    r*     the exact robustness radius, bracketed by the MILP (the largest eps it verifies and the
           smallest it falsifies),
    eps_A  the smallest eps at which the PGD attack finds a counterexample,
each to within TOL. The queries come from your Part 1 make_vnnlib.

Write binary_search(pred, lo, hi, tol). pred is MONOTONE: True for every eps up to some
threshold, False after it. Given pred(lo) True and pred(hi) False, return (a, b) with pred(a)
True, pred(b) False and b - a <= tol, calling pred as few times as you reasonably can.

    python3 part2_frontier.py
"""
from __future__ import annotations

import sys

from hw5lib import load_images, load_net, lirpa_check, milp_check, parse_vnnlib, pgd_attack
from part1_query import make_vnnlib

IMAGES = [0, 9]
LO, HI, TOL = 0.0, 0.08, 0.001


def binary_search(pred, lo: float, hi: float, tol: float):
    """(a, b): pred(a) is True, pred(b) is False, and b - a <= tol."""
    return None          # PLACEHOLDER -- replace with your code


def main() -> int:
    W = load_net()
    X, Y, _ = load_images()
    if binary_search(lambda e: e < 0.5, 0.0, 1.0, 0.1) is None:
        print("binary_search is still the placeholder")
        return 1
    for i in IMAGES:
        def spec(eps, i=i):
            return parse_vnnlib(make_vnnlib(X[i], int(Y[i]), eps))
        crown = binary_search(lambda e: lirpa_check(W, spec(e), "CROWN").verdict == "verified", LO, HI, TOL)
        milp = binary_search(lambda e: milp_check(W, spec(e)).verdict == "verified", LO, HI, TOL)
        pgd = binary_search(lambda e: pgd_attack(W, spec(e)).verdict != "falsified", LO, HI, TOL)
        print(f"image {i}: eps_C = {crown[0]:.4f}   r* in [{milp[0]:.4f}, {milp[1]:.4f}]   "
              f"eps_A = {pgd[1]:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
