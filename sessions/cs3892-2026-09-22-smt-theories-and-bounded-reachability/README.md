# cs3892-2026-09-22-smt-theories-and-bounded-reachability

Worked examples for the lecture of the same name — Session 8, Tuesday 22 September 2026.

| File | Shows | Verdict |
|---|---|---|
| `smt2/01_theory_conflict.smt2` | the boolean skeleton is sat, the formula is not — the gap DPLL(T) closes | `unsat` |
| `python/01_theory_conflict.py` | the same gap, both halves side by side | `sat` / `unsat` |
| `python/02_bmc_unroll.py` | bounded reachability: unroll `k`, assert the property breaks, read the trace | threshold `k = 4` |
| `smt2/02_bmc_unroll_k4.smt2` | the same unrolling written out by hand, so the shape is visible | `sat` |
| `smt2/03_bmc_unroll_k3.smt2` | one step short — `unsat` that is **not** a proof of safety | `unsat` |
| `python/03_scaling.py` | 100,000 variables in a fraction of a second; 11 pigeons is worse | `sat` / `unsat` |
| `python/04_abstract_core.py` | an UNSAT core with no domain meaning attached | core = `A1 A2 A3` |
| `python/05_modes_efsm.py` | the two-mode extended state machine — a relation over **two** variables | `x = 11` unreachable |

**`02_bmc_unroll.py` is the method for HW1 Part 3, on a different machine.** The
thermostat here starts at 20 and each step adds +3 or −1; Part 3's counter starts
at 0 and adds 1 unconditionally. Copy the method, not the number — finding the
threshold and *arguing* for it is what Part 3 is asking.

Run them all:

```bash
bash scripts/check_examples.sh sessions/cs3892-2026-09-22-smt-theories-and-bounded-reachability
```
