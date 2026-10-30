# cs3892-2026-11-19-nn-verification-robustness

Session 24: neural-network verification I. Local robustness as a formal query, and three ways to
answer it, on a network small enough to check by hand: 2 inputs → 2 ReLU neurons → 2 outputs
(`python/nnv.py`). At x0 = (0.45, 0.55) class 0 wins with margin 0.4. Is it still class 0 for every
input within ε (infinity norm)?

| File | Shows | Result |
|---|---|---|
| `python/nnv.py` | the network; IBP, CROWN (hand-written, about 20 lines), the exact minimum margin (vertex enumeration, possible in 2-D), input-splitting branch and bound, binary search for a frontier, the query in VNN-LIB, and auto_LiRPA's bounds for comparison | — |
| `python/01_robustness_query.py` | robustness as a statement about every input in a box; the VNN-LIB query | margin 0.4 at x0 |
| `python/02_ibp_crown_exact.py` | IBP vs CROWN vs exact at ε = 0.05, 0.10, 0.15, 0.25, checked against auto_LiRPA | IBP loses even at 0.05; CROWN to 0.10; exact: robust to 0.15, falsified at 0.25 |
| `python/03_frontier_and_bab.py` | the ε frontier of each method; branch and bound; α-CROWN | IBP 0.04, CROWN 0.125, true radius 0.2; BaB verifies 0.15 in 3 boxes, falsifies 0.25 |

Tools: HW5's pinned set (torch 2.11.0 CPU, auto_LiRPA 0.8.0, numpy), installed by the notebook from
`homework/hw5-nn-verification/requirements*.txt`. This is not HW5's network or input: HW5 uses a
196 → 32 → 32 → 10 MNIST classifier.

Run them all:

```bash
bash scripts/check_examples.sh sessions/cs3892-2026-11-19-nn-verification-robustness
```
