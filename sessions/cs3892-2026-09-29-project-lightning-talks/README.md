# cs3892-2026-09-29-project-lightning-talks

Session 10 is the project proposal talks. These files back the **backup slides**
(nuXmv in depth), used only if the talks finish early.

| File | Shows | Verdict | Tool |
|---|---|---|---|
| `smv/01_three_engines.smv` | one invariant, three engines: BDDs, BMC/k-induction, IC3 | `x <= 10` true · `x <= 9` false (BMC: "cannot prove" at k=9, false at k=10) | NuSMV / nuXmv |
| `smv/02_add2_integer.smv` | session 9's add-2 counter over the integers; IC3 finds the strengthening | `x != 5` true | **nuXmv only** |
| `smv/03_counter_ltl.smv` | first LTL: `G`, `G F`, `F G`, and a lasso counterexample | true · true · false | NuSMV / nuXmv |

All verdicts were run under NuSMV 2.6.0 and nuXmv 2.2.0. The notebook asserts the
NuSMV ones; `02` is nuXmv-only and its output is recorded in the file header.
