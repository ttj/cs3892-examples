# Session 7 — SAT solving and proof by refutation

**Thursday, September 17, 2026.** [Open the notebook in Colab](https://colab.research.google.com/github/ttj/cs3892-examples/blob/main/notebooks/cs3892-2026-09-17-sat-solving-and-refutation.ipynb)

Three examples about what the solver is doing underneath.

| # | Shows | Slide | Verdict |
|---|---|---|---|
| 01 | `refutation` — the contrapositive law, proved by asking whether it can be false | 24 | `unsat` |
| 02 | `unsat_core` — which rules are the contradiction, not just that there is one | 30 | `unsat` |
| 03 | `bitblast` — one line about an 8-bit number becomes 90 CNF clauses | 28 | `sat`, `x = 127` |

## The one idea

**You never ask a solver whether something is true.** You ask whether it can be
false, and `unsat` is the proof. `01` is the law proved by hand on the board on
September 10, done the machine's way; every tool in Units 3–10 works like this.

`02` is the part people underestimate. A checker that says *inconsistent* is
annoying; one that says *these four rules are the inconsistency* is usable. That
is what an UNSAT core is, and it is why the Bedrock-style policy checkers from
session 4 can tell you what to fix.

`03` shows where the boolean problem actually comes from. Nobody writes SAT by
hand — you write `x + 1 > x` over an 8-bit value, and bit-blasting plus Tseitin
turns it into clauses over the individual bits.

Run them all:

```bash
bash scripts/check_examples.sh sessions/cs3892-2026-09-17-sat-solving-and-refutation
```
