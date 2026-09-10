# CS 3892 / CS 5892 — runnable examples

**Formal Methods: Safe and Trustworthy AI · Vanderbilt · Fall 2026**

Every worked example from the lectures, runnable in a browser with nothing
installed. One folder per session, **named to match its slide deck**, so an
example is never orphaned from the lecture that used it.

## Sessions

| Session | Open in Colab | Files |
|---|---|---|
| **Thu Sep 10** · Sets, logic, and solvers | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ttj/cs3892-examples/blob/main/notebooks/cs3892-2026-09-10-sets-and-propositional-logic.ipynb) | [`sessions/cs3892-2026-09-10-sets-and-propositional-logic`](sessions/cs3892-2026-09-10-sets-and-propositional-logic) |

## How it is laid out

```
sessions/<slide-deck-name>/
  smt2/     SMT-LIB 2 — the standard language every SMT solver reads
  python/   the same examples through Z3's Python API
notebooks/<slide-deck-name>.ipynb   runs those files; does not copy them
scripts/                            check, lint, run
```

**The notebooks contain no copies of the code.** They execute the real files, so
a notebook cannot drift away from the repository — and CI executes the notebooks
end to end, so it cannot drift away from working either.

## Running it yourself

Colab needs nothing. Locally:

```bash
git clone https://github.com/ttj/cs3892-examples.git
cd cs3892-examples
pip install z3-solver
bash scripts/check_examples.sh          # every example, every verdict
```

```bash
bash scripts/check_examples.sh sessions/cs3892-2026-09-10-sets-and-propositional-logic   # one session
bash scripts/lint_examples.sh                              # wiring check
bash scripts/run_notebooks.sh                              # needs nbclient
```

## How an example proves itself

Each `.smt2` carries its expected verdict in its own header:

```
; EXPECT: unsat
```

and each `.py` asserts its own result. So a wrong answer is a **failure**, not a
number nobody notices. `scripts/run_smt2.py` runs SMT-LIB through the Z3 Python
bindings rather than a shell command, because the `z3-solver` pip wheel ships
**no `z3` CLI** — this way Colab, CI and your laptop all behave identically.

## Adding a session

```bash
bash scripts/new_session.sh 2026-09-17-sat-solving-and-refutation
```

Then write the examples, copy the previous notebook and repoint its `SESSION`
constant. `lint_examples.sh` will fail until every new file is referenced from a
notebook, which is the point.

---

Slides and course materials are elsewhere; this repository is only the code you
can run. It is public so the Colab links work without a login.
