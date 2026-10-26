"""HW5 Part 4 -- IBP vs CROWN vs alpha-CROWN: precision against cost.

For each query, each method's sound LOWER bound on the worst margin min_j (Y_label - Y_j) over
the input box (the property is verified when it is above 0), and the time it took. Nothing to
edit: run it and answer the questions in the handout.

    python3 part4_bounds.py
"""
from __future__ import annotations

import sys

from hw5lib import load_images, load_net, lirpa_check, parse_vnnlib
from part1_query import make_vnnlib

QUERIES = [(3, 0.02), (3, 0.03), (9, 0.02), (0, 0.015), (0, 0.02)]
METHODS = ["IBP", "CROWN", "alpha-CROWN"]


def main() -> int:
    W = load_net()
    X, Y, _ = load_images()
    print(f"{'image':>5} {'eps':>6}   " + "   ".join(f"{m:>22}" for m in METHODS))
    for i, eps in QUERIES:
        text = make_vnnlib(X[i], int(Y[i]), eps)
        if text is None:
            print("Part 1's make_vnnlib is still the placeholder")
            return 1
        spec = parse_vnnlib(text)
        cells = []
        for m in METHODS:
            r = lirpa_check(W, spec, m)
            worst = min(r.bounds)           # bounds[j] = lower bound of Y_label - Y_j
            cells.append(f"{worst:>9.3f} {r.verdict[:3]} {r.seconds:>6.3f}s")
        print(f"{i:>5} {eps:>6}   " + "   ".join(f"{c:>22}" for c in cells))
    return 0


if __name__ == "__main__":
    sys.exit(main())
