# HW1 — Logic, SAT/SMT, and bounded reachability

Starters for [the HW1 handout](https://github.com/ttj/cs3892-fmstai-fall2026/blob/main/assignments/hw1.md).
**Out Thu Sep 10 · due Thu Sep 24, 11:59 p.m.**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ttj/cs3892-examples/blob/main/notebooks/hw1-logic-sat-smt.ipynb)

These are **starters, not solutions.** Everything complete here is worked on a
*different* instance from the one the homework asks about; the files with TODOs
are the ones that are yours.

| Part | File | State |
|---|---|---|
| 1 | `python/p1_warmup_starter.py` | modus ponens and affirming-the-consequent worked; **five statements are yours** |
| 2 | `python/p2_pigeonhole.py` | complete, parameterised |
| 2 | `python/p2_nqueens.py` | complete, parameterised |
| 2 | `python/p2_timing.py` | complete — produces the table part 2 asks for; **widen the ranges** |
| 2 | `smt2/p2_pigeonhole_5_into_4.smt2` | the same thing written by hand, `unsat` |
| 3 | `python/p3_reachability_demo.py` | **worked on a toy**: +1/+2, target 7, threshold k = 4 |
| 3 | `python/p3_reachability_starter.py` | **three TODOs** — the machine from the handout |
| 3 | `smt2/p3_reach7_k3.smt2` · `p3_reach7_k4.smt2` | the unrolling by hand, either side of the threshold |
| 4 | `python/p4_how_do_you_know.py` | three checks that catch a wrong encoding, worked against a deliberately sabotaged one |

## Run them

Colab needs nothing. Locally:

```bash
pip install z3-solver
cd homework/hw1-logic-sat-smt/python && python3 p3_reachability_demo.py
bash scripts/check_examples.sh homework/hw1-logic-sat-smt   # from the repo root
```

## The one that matters

`p4_how_do_you_know.py`. Part 4 is not "did the LLM get it right" — it is
**how you knew**. An encoding that returns `unsat` for the wrong reason looks
exactly like a correct one, and that file shows three checks that tell them
apart. Run all three against whatever the model gives you.
