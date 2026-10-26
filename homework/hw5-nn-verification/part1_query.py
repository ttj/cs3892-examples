"""HW5 Part 1 -- local robustness as a formal query, in VNN-LIB.

Write make_vnnlib(x0, label, eps). It returns the VNN-LIB text for the property

    every input within L-infinity distance eps of x0, with every pixel value kept in [0, 1],
    is classified as `label` (its logit for `label` is the highest)

The network has inputs X_0 .. X_195 (the 14x14 pixels) and outputs Y_0 .. Y_9 (the logits).
Remember what a VNN-LIB file states: the input box, and the output region where the property
FAILS. A verifier answers "unsat" (verified) when no input in the box reaches that region.

    python3 part1_query.py      # writes one .vnnlib per query and runs all three tools on it
"""
from __future__ import annotations

import sys

from hw5lib import load_images, load_net, lirpa_check, milp_check, parse_vnnlib, pgd_attack

QUERIES = [(4, 0.02), (4, 0.03), (4, 0.05)]          # (image, eps)


def make_vnnlib(x0, label: int, eps: float) -> str | None:
    """The VNN-LIB text for the robustness property above. x0: the 196 pixel values of the image."""
    return None          # PLACEHOLDER -- replace with your code; return the text as one string


def main() -> int:
    W = load_net()
    X, Y, _ = load_images()
    for i, eps in QUERIES:
        text = make_vnnlib(X[i], int(Y[i]), eps)
        if text is None:
            print("make_vnnlib is still the placeholder")
            return 1
        path = f"part1_image{i}_eps{eps}.vnnlib"
        with open(path, "w") as fh:
            fh.write(text)
        spec = parse_vnnlib(text)
        crown, milp, pgd = lirpa_check(W, spec, "CROWN"), milp_check(W, spec), pgd_attack(W, spec)
        print(f"image {i} (a {Y[i]}), eps {eps}:  CROWN {crown.verdict:8} | MILP {milp.verdict:9} "
              f"({milp.seconds:.2f}s) | PGD {pgd.verdict}   -> {path}")
    i, eps = QUERIES[1]
    short = milp_check(W, parse_vnnlib(make_vnnlib(X[i], int(Y[i]), eps)), time_limit=0.01)
    print(f"\nimage {i}, eps {eps}, MILP with a 0.01 s time limit: {short.verdict} ({short.detail})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
