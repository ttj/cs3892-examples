# cs3892-2026-09-24-inductive-invariants-and-smv

Worked examples for the lecture of the same name — Session 9, Thursday 24 September 2026.

| File | Shows | Verdict |
|---|---|---|
| `smt2/01_bmc_k3.smt2` | the BMC query at `k = 3`, written out with nothing hidden | `unsat` |
| `python/01_bmc_worked.py` | the same query printed at each `k`, then pushed out to 50 | `unsat` every time |
| `smt2/02_induction.smt2` | **consecution** — the query with no `k` in it | `unsat` |
| `python/02_inductive_check.py` | all three obligations for the canonical counter | all `unsat` — inductive |
| `smt2/03_not_inductive.smt2` | consecution failing, and the CTI | `sat`, `x = 3` |
| `python/03_not_inductive.py` | invariant but **not** inductive — the distinction | CTI `3 → 5` |
| `python/04_strengthen.py` | strengthening `x ≠ 5` to `x is even` fixes it | all `unsat` |
| `smv/counter.smv` | the same machine in the SMV language, with three `SPEC`s | — |

**The arc is 01 → 02 → 03 → 04.** Fifty bounds and fifty `unsat` is still not a
proof (01). Two queries that mention no bound at all is one (02). Then the thing
that makes it hard: a property can be a true invariant and still fail
consecution (03), because induction is asked about *unreachable* states too —
and the fix is a **stronger** invariant, not a better solver (04).

`smv/counter.smv` runs in the browser with no install: **<https://bit.ly/fmaiv_smvis>**

Run them all:

```bash
bash scripts/check_examples.sh sessions/cs3892-2026-09-24-inductive-invariants-and-smv
```
