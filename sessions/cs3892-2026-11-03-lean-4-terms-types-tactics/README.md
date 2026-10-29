# cs3892-2026-11-03-lean-4-terms-types-tactics

Session 19. Lean 4 is a programming language whose type checker also checks proofs. A
proposition is a type, and a proof is a program of that type (Curry–Howard). Tactics build that
program one step at a time, and Lean shows the goal after every step. `sorry` compiles and proves
nothing; `#print axioms` says what a theorem rests on.

**Lean v4.33.0, core library only** (the version HW4 pins). The Colab notebook installs it with
HW4's checker (elan + Lean, about 575 MB, once). To see goals as you type, open `lean/` in VS Code
with the Lean 4 extension.

| File | Shows | Result |
|---|---|---|
| `python/lean_cli.py` | finds Lean, or installs it through `homework/hw4-lean/check_hw4.py` (pinned by SHA-256); runs a Lean file; reads Lean's goal before every tactic line (`trace_state`) | `Lean (version 4.33.0, …)` |
| `lean/S19/Counter.lean`, `python/01_lean_is_a_language.py` | the running counter as a Lean function: `#eval`, `#check`, then `step_3` (rfl), `step_le` (for every x), `run_le` (by induction, for every number of moves) | `[0, 1, …, 10, 0, 1]` · `run 0 n ≤ 10` for all n, proved |
| `lean/S19/CurryHoward.lean`, `python/02_curry_howard.py` | `and_swap` as a term (a function on pairs), `swap` on data, `from_false`, and `and_swap'` in tactics with its goal at every step | `A ∧ B → B ∧ A` · six goals, the last "no goals" |
| `lean/S19/Tactics.lean`, `lean/S19/OmegaStops.lean`, `python/03_tactics.py` | `rfl`, `decide`, `omega`, `simp` closing goals; omega on a non-linear goal | all proved · `x ≤ x * x`: error, `omega could not prove the goal` |
| `lean/S19/Sorry.lean`, `python/04_sorry_and_axioms.py` | `sorry`, a home-made `axiom`, and a vacuous theorem (its hypothesis `x < 0` never holds for a `Nat`), each read with `#print axioms` | ``declaration uses `sorry` `` · `[propext, sorryAx, Quot.sound]` · `[all_zero]` · `does not depend on any axioms` · `vacuous`: `[propext, Quot.sound]`, proved and saying nothing |
| `lean/S19/Sets.lean`, `python/05_sets_as_predicates.py` | sets as predicates; De Morgan for ∪, constructively; `¬¬p → p` with `by_cases` | `compl_union`: `[propext, Quot.sound]` · `not_not`: adds `Classical.choice` |
| `lean/S19.lean`, `python/06_whole_library.py` | `lake build` of the whole project | builds, no `sorry`, no warning |

`Sorry.lean` is meant to warn and `OmegaStops.lean` is meant to fail; `S19.lean` leaves both out,
so `lake build` stays clean. HW4's own examples (`triple`, the traffic light, the token bucket and
its five set identities) are not proved here.

![The running counter (01).](figures/counter.svg)

Run them all:

```bash
bash scripts/check_examples.sh sessions/cs3892-2026-11-03-lean-4-terms-types-tactics
```
