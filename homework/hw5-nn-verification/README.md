# HW5 — Neural-network verification: starters

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ttj/cs3892-examples/blob/main/notebooks/hw5-nn-verification.ipynb)

Starters for the HW5 handout. **Out Thu Nov 19 · due Fri Dec 4, 11:59 p.m.** The handout, with the
questions and the points, is
[`assignments/hw5.md`](https://github.com/ttj/cs3892-fmstai-fall2026/blob/main/assignments/hw5.md)
in the class repository.

**The network** classifies MNIST digits downsampled to 14×14 (196 pixels in [0, 1]):
196 → 32 → ReLU → 32 → ReLU → 10, 95.4% test accuracy. **Ten test images**, image *i* a digit *i*.
**Three tools answer every query:**

| tool | what it is | can say |
|---|---|---|
| `lirpa_check` | auto_LiRPA's IBP / CROWN / α-CROWN bounds: sound, **incomplete** | verified · unknown |
| `milp_check` | the network as a mixed-integer linear program, solved exactly by HiGHS: sound and **complete** | verified · falsified (with a counterexample) · timeout |
| `pgd_attack` | projected gradient descent: a search | falsified · no counterexample found |

| File | Part | What it is |
|---|---|---|
| `hw5lib.py` | all | the network, the images, the VNN-LIB parser and meaning check, the three tools. **Do not edit it**; the checker refuses a changed copy |
| `part1_query.py` | 1 | write `make_vnnlib`: local robustness as a VNN-LIB property |
| `part2_frontier.py` | 2 | write `binary_search`: the ε frontier of CROWN, the MILP and PGD |
| `part3_compare.py` | 3 | the two verifiers on a grid; set `FINDING` |
| `part4_bounds.py` | 4 | IBP vs CROWN vs α-CROWN: precision against cost (nothing to edit) |
| `part5/` | 5 | three properties in English; the LLM's VNN-LIB and your corrected VNN-LIB |
| `check_hw5.py` | all | runs every part: ok / placeholder / wrong / error |
| `python/00_hw5_starter_checks.py` | — | CI: the starter's state; the meaning check catches four typical mistakes; CROWN never contradicts the MILP |
| `net/`, `data/` | — | the weights (`.npz`, no pickle), the ten images, and Part 5's intended output regions as bits on a fixed sample (so the checker can say "matches" without printing them) |

```bash
git clone --depth 1 https://github.com/ttj/cs3892-examples.git
cd cs3892-examples/homework/hw5-nn-verification
pip install -r requirements.txt
pip install --no-deps --ignore-requires-python -r requirements-lirpa.txt
python3 check_hw5.py              # what is done, what is not
python3 part1_query.py            # and so on, part by part
python3 check_hw5.py --strict     # the acceptance test: exits 0 only when every part is OK
```

**Every tool version is pinned.** torch 2.11.0 is the CPU build (on Linux and Windows from PyTorch's
own index; on macOS PyPI's build is CPU-only). auto_LiRPA 0.8.0 is pinned to its release commit,
`e393035`, because its maintained releases are on GitHub only. Its metadata says Python 3.11 only,
and the course checks it on 3.10 and 3.12, hence `--ignore-requires-python`. Use a virtual
environment (`python3 -m venv .venv && . .venv/bin/activate`) so the pins don't disturb anything else.
`check_hw5.py` says so if your versions differ.

**Credits.** MNIST: Yann LeCun, Corinna Cortes and Christopher J.C. Burges,
<http://yann.lecun.com/exdb/mnist/>, licensed [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/).
The ten images in `data/` are 2×2-average-pooled copies of MNIST test images 2000–2055, and are
shared under the same licence. auto_LiRPA: the α,β-CROWN team, BSD-3-Clause.
HiGHS: MIT licence.
