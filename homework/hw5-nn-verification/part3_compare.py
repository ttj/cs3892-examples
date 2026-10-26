"""HW5 Part 3 -- two verifiers on the same queries.

CROWN (auto_LiRPA; sound, incomplete) and an exact MILP (HiGHS; sound and complete) on every
(image, eps) of the grid below, with their verdicts and times. The queries come from your Part 1
make_vnnlib.

Then set FINDING to one (image, eps) of the grid where CROWN says "unknown" and the MILP
decides, and answer the questions about it in the handout. The checker re-runs your FINDING.

    python3 part3_compare.py
"""
from __future__ import annotations

import sys

from hw5lib import load_images, load_net, lirpa_check, milp_check, parse_vnnlib
from part1_query import make_vnnlib

IMAGES = list(range(10))
EPS = [0.01, 0.02, 0.03]
FINDING = None           # PLACEHOLDER -- e.g. (image, eps), a pair from the grid


def main() -> int:
    W = load_net()
    X, Y, _ = load_images()
    print(f"{'image':>5} {'eps':>5}   {'CROWN':<9}{'time':>8}   {'MILP':<10}{'time':>8}")
    for i in IMAGES:
        for eps in EPS:
            text = make_vnnlib(X[i], int(Y[i]), eps)
            if text is None:
                print("Part 1's make_vnnlib is still the placeholder")
                return 1
            spec = parse_vnnlib(text)
            c, m = lirpa_check(W, spec, "CROWN"), milp_check(W, spec)
            print(f"{i:>5} {eps:>5}   {c.verdict:<9}{c.seconds:>7.3f}s   {m.verdict:<10}{m.seconds:>7.3f}s")
            if c.verdict == "verified" and m.verdict == "falsified":
                print("  !! CROWN verified a query the MILP falsified: one of them is unsound")
    print(f"\nFINDING = {FINDING}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
