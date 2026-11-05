# cs3892-2026-11-05-lean-4-transition-systems

Session 20 (after D8). A transition system in Lean is a structure with an `init` and a `step`;
`Reachable` is an inductive predicate, so a fact about every reachable state is proved by
induction on how the state was reached. That is why an inductive invariant holds. Then session 9's
add-2 machine, where `x ≠ 5` is true but not inductive, and the stronger invariant that proves it;
the running counter with a power switch, proved for every cap `N`; and how to build a reachable
state, to show the bound is tight. Then where hypothesis names like `h` come from, and two SMV
models translated into Lean by `scripts/smv2lean` (from ttj/leansmv) and proved there by case
splits: the course's two-mode counter, and session 11's mutex.

`TS`, `Reachable`, `InductiveInvariant`, `Invariant` and `inductive_invariant_holds` are the
definitions HW4's `Defs.lean` gives you, with the same names. **Lean v4.33.0, core library only.**
The Colab notebook installs it with HW4's checker. To see goals as you type, open `lean/` in VS
Code with the Lean 4 extension.

| File | Shows | Result |
|---|---|---|
| `python/lean_cli.py` | finds Lean, or installs it through `homework/hw4-lean/check_hw4.py`; builds the library once and runs each file through `lake env lean` (the files import one another); reads Lean's goal before every tactic line (`trace_state`) | `Lean (version 4.33.0, …)` |
| `lean/S20/TS.lean`, `python/01_reachable_and_induction.py` | the definitions; `inductive_invariant_holds` by induction on `Reachable`, with its goal in each case | `case init` · `case step` with `ih : P s✝` |
| `lean/S20/Switch.lean`, `python/02_switch_every_step.py` | the counter with a power switch: a structure state, a step relation with one constructor per guarded transition; `x_le_N` by `cases` on the step | `x ≤ N` for every cap `N` · four goals, one per transition |
| `lean/S20/Add2.lean`, `python/03_true_but_not_inductive.py` | add-2 and `P x := x ≠ 5`; `P_not_inductive` from the CTI 3 → 5 | `¬InductiveInvariant add2 P`, proved |
| `lean/S20/Add2.lean`, `python/04_strengthen.py` | `Even` is inductive; `P_holds` from it | `x ≠ 5` in every reachable state |
| `lean/S20/Switch.lean`, `python/05_build_reachable_states.py` | `reach_k`: a `Reachable` proof built forward, by induction on `k`; `bound_tight`: an `∃` witness | `⟨true, k⟩` reachable for every `k ≤ N` · the bound is reached |
| `lean/S20.lean`, `python/06_whole_library.py` | `lake build`, then `#print axioms` for every theorem | no `sorry`, no warning · nothing beyond `propext`, `Quot.sound`, except `Classical.choice` in the false-INVARSPEC proof |
| `lean/S20/Names.lean`, `python/07_names_and_rw.py` | where a hypothesis name comes from (the statement, `intro`, `obtain`, or nobody: `a✝`); `rw [h]` and `rw [← h]` | Lean's goal before each step |
| `smv/counter.smv`, `smv/mutex.smv`, `python/08_smv_to_lean.py` | `scripts/smv2lean/to_course.py` regenerates `lean/S20/Counter.lean` and `Mutex.lean` from the SMV and checks they match | the committed files are the translator's output, and build |
| `lean/S20/CounterProofs.lean`, `python/09_counter_case_split.py` | the counter's three INVARSPECs: `split at hx` (one goal per case line), `cases mode <;> cases press` (one per combination), and the false one refuted with NuSMV's trace | `x ≤ 10` · `mode = off → x = 0` · `¬ (x < 10)` |
| `lean/S20/MutexProofs.lean`, `python/10_mutex_case_split.py` | mutual exclusion: `cases a <;> cases b`, nine goals, eight left after `simp` | `¬(a = critical ∧ b = critical)` in every reachable state |

HW4's own systems (the token bucket and its invariant) are not proved here.

![The counter with a power switch (02, 05).](figures/switch.svg)

![Session 9's add-2 machine (03, 04).](figures/add2.svg)

![The two-mode counter, as in smv/counter.smv (08, 09).](figures/modes_efsm.svg)

![Session 11's mutex, process a; b is its mirror image (08, 10).](figures/mutex.svg)

Run them all:

```bash
pip install lark      # for scripts/smv2lean (08)
bash scripts/check_examples.sh sessions/cs3892-2026-11-05-lean-4-transition-systems
```

NuSMV gives the same verdicts on the two SMV files: `x <= count_max` and `(mode = off -> x = 0)`
true, `x < count_max` false (a trace to x = 10); `!(crit_a & crit_b)` true.
