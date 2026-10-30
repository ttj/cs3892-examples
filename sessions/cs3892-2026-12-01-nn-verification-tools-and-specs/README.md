# cs3892-2026-12-01-nn-verification-tools-and-specs

Session 25: neural-network verification II. Two verifiers on the same queries, what a verifier's
"timeout" means, and an LLM writing VNN-LIB, on session 24's toy network (2 → 2 → 2 ReLU; imported
from that session's `nnv.py`, not copied).

| File | Shows | Result |
|---|---|---|
| `python/toy.py`, `python/queries.py` | session 24's network and bounds; 25 queries (5 points × 5 radii, none on the boundary) | — |
| `python/milp.py` | an exact verifier: the big-M MILP encoding of each ReLU, solved by HiGHS | equals the exact minimum on every query |
| `python/01_two_verifiers.py` | CROWN (incomplete) vs the MILP (complete): the agreement table | 14 both verified · 7 CROWN unknown, MILP verified · 4 CROWN unknown, MILP falsified · **0** unsound |
| `python/02_buggy_verifier.py` | CROWN with the chord's intercept dropped, cross-checked by the MILP | verifies 4 false properties; its bound exceeds the true minimum on 16 of 25 |
| `python/03_timeout.py` | one query under three budgets | MILP 0 s: timeout · BaB 2 boxes: unknown · given time: verified |
| `python/04_llm_vnnlib.py`, `llm/` | three English properties → VNN-LIB by Claude Haiku 4.5 (no tools, empty directory, one attempt, saved verbatim); parsed with HW5's parser and compared with references | all three files right; the Q3 explanation contradicts itself about the boundary |

Tools: HW5's pinned set (numpy, highspy, and torch + auto_LiRPA through session 24's `nnv.py`).
No model is called when the scripts run: `04` checks the saved reply.

Run them all:

```bash
bash scripts/check_examples.sh sessions/cs3892-2026-12-01-nn-verification-tools-and-specs
```
