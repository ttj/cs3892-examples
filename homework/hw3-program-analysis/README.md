# HW3 — Program analysis: bounded model checking, loop invariants, abstract interpretation

Starters for the HW3 handout. **Out Mon Oct 26 · due Tue Nov 3, 11:59 p.m.**

**The handout:** [PDF](https://github.com/ttj/cs3892-fmstai-fall2026/blob/main/assignments/hw3.pdf) ·
[web page](https://github.com/ttj/cs3892-fmstai-fall2026/blob/main/assignments/hw3.md). It is also in Brightspace
([Content](https://brightspace.vanderbilt.edu/d2l/le/content/646125/Home) → Week 10), which is where you submit.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ttj/cs3892-examples/blob/main/notebooks/hw3-program-analysis.ipynb) — every starter, ready to run, with nothing to install.

These are **starters, not solutions.** Every script runs as it is and exits normally, with a
placeholder where your work goes. No file states an answer the homework asks for.

| File | What it is | Part |
|---|---|---|
| `c/counter.c`, `c/counter_check.c` | the course's two-mode counter in C and its CBMC harness (from [FMAIV](https://github.com/ttj/fmaiv) day 4) | 1 |
| `c/array_max.c` | the array maximum (from FMAIV) whose loop you prove | 2a |
| `python/hw3_part2_vcs.py` | `array_max`'s three loop-invariant conditions as Z3 queries. **Your invariants go in `CANDIDATES`** | 2a |
| `c/converge.c`, `python/hw3_part2_converge.py` | two indices walking towards each other, with a CBMC loop contract. **Your invariant is the argument** | 2b |
| `python/absint.py` | the course's small abstract interpreter (signs, intervals, join, widening), as in session 18 | 3 |
| `python/hw3_part3_programs.py` | programs P1–P4, run in both domains. **Your P5 goes in `PROGRAMS`** | 3 |
| `c/part3_p5.c` | **your P5 in C**, for `goto-analyzer` and CBMC (the placeholder is not a false alarm) | 3 |
| `c/triangle.c` | the function you generate tests for, with a deliberate bug behind `-DMUTANT` | 4 |
| `python/hw3_part4_coverage.py`, `tests/example.txt` | runs a test file: results against the specification, `gcov` branch coverage, and does it catch the mutant? | 4 |
| `c/part5_functions.c`, `c/contracts.h` | three functions to give contracts. **Contracts go in `contracts.h`**; the placeholders say nothing | 5 |
| `python/hw3_part5_check.py` | checks each contract against the function, against a mutant, and whether its precondition can be met | 5 |
| `python/cbmc_cli.py` | finds CBMC, or fetches the official 6.11.0 release (checked by SHA-256, no root needed) | all |

## Run them

**Colab:** open the notebook above and run it top to bottom. It installs Z3 and CBMC itself.

**Any Linux shell, or the [FMAIV Codespace](https://github.com/ttj/fmaiv)** (which ships CBMC 6.9):

```bash
git clone --depth 1 https://github.com/ttj/cs3892-examples.git
cd cs3892-examples/homework/hw3-program-analysis/python
pip install z3-solver
python3 cbmc_cli.py                       # prints the CBMC it found or fetched
python3 hw3_part2_vcs.py
```

`cbmc_cli.py` puts CBMC in `~/.cache/cs3892/cbmc-6.11.0/`. To type `cbmc` yourself, add that folder
to your `PATH`. On macOS: `brew install cbmc`. On Windows: the `.msi` from the
[CBMC releases page](https://github.com/diffblue/cbmc/releases), or use Colab.

**CBMC 6 turns unwinding assertions on by default.** `--unwinding-assertions` is accepted and changes
nothing. `--no-unwinding-assertions` turns them off. Older tutorials pass the first flag explicitly.
