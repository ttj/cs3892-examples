# Session 5 — Sets, logic, and solvers

**Thursday, September 10, 2026.** [Open the notebook in Colab](https://colab.research.google.com/github/ttj/cs3892-examples/blob/main/notebooks/cs3892-2026-09-10-sets-and-propositional-logic.ipynb)

The five demos from the back half of the lecture, plus the identity the whole
course rests on. Each one exists twice: as SMT-LIB, which is what the standard
looks like, and as Python, which is what you will actually write.

| # | Shows | Slide | Verdict |
|---|---|---|---|
| 01 | `policy_booleans` — a policy and a claim, in pure propositional logic | 27 | `unsat` |
| 02 | `policy_integers` — one atom becomes arithmetic; Z3 knows 11 < 12 | 29 | `unsat` |
| 03 | `policy_integers_sat` — change 11 to 12; `sat`, **with a model** | 29 | `sat` |
| 04 | `half_int` — \(2x = 1\) has no integer solution | 30 | `unsat` |
| 05 | `half_real` — the same formula over the reals | 30 | `sat`, `x = 1/2` |
| 06 | `bitvector_overflow` — \(x+1 > x\) is false on a machine | 31 | `sat`, `x = 127` |
| 07 | `uninterpreted_function` — congruence, with no definition of `f` | 32 | `unsat` |
| 08 | `validity_by_refutation` — \(\varphi\) valid ⟺ \(\neg\varphi\) unsat | 23 | `unsat` |

Pairs 04/05 and 02/03 are the point of the session: **the formula does not
change, the theory does, and the answer reverses.**

```bash
bash scripts/check_examples.sh sessions/cs3892-2026-09-10-sets-and-propositional-logic
```
