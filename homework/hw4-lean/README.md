# HW4 — Interactive theorem proving in Lean 4: starters

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ttj/cs3892-examples/blob/main/notebooks/hw4-lean.ipynb)

Starters for the HW4 handout. **Out Tue Nov 3 · due Thu Nov 12, 11:59 p.m.** The handout, with
the questions and the points, is
[`assignments/hw4.md`](https://github.com/ttj/cs3892-fmstai-fall2026/blob/main/assignments/hw4.md)
in the class repository.

**Lean v4.33.0, core library only.** No Mathlib, so it builds in seconds, and Parts 1–2 also run in
the [Lean web editor](https://live.lean-lang.org/). Do not use FMAIV's day 3 project for this: it
pins Lean v4.29.0 and has different exercises.

| File | Part | What it is |
|---|---|---|
| `HW4/Defs.lean` | all | every given definition: transition systems, sets as predicates, the token bucket. **Do not edit it**; the checker refuses a changed copy |
| `HW4/Part1Ladder.lean` | 1 | seven rungs, one tactic idea each |
| `HW4/Part2Sets.lean` | 2 | five set identities, one of them classical |
| `HW4/Part3Bucket.lean` | 3 | a true property that is not inductive; your strengthened `Inv` |
| `HW4/Part4Parametric.lean` | 4 | the same bound for every capacity `N`, and that it is tight |
| `ai_log.md` | 5 | the AI proof-partner log |
| `check_hw4.py` | all | builds each part and reports every theorem as proved / uses sorry / disallowed axiom / statement changed |
| `python/00_starter_checks.py` | — | CI: the starter builds, every theorem is still a `sorry`, and the checker catches `native_decide`, a home-made `axiom`, and an edited `Defs.lean` |

```bash
git clone --depth 1 https://github.com/ttj/cs3892-examples.git
cd cs3892-examples/homework/hw4-lean
python3 check_hw4.py            # installs elan + Lean v4.33.0 on first run if you have none
lake build HW4.Part1Ladder      # or build one part while you work on it
python3 check_hw4.py --strict   # the acceptance test: exits 0 only when every theorem is proved
```

**Proved** means: the part builds, the statement is unchanged, and `#print axioms` lists nothing
beyond `propext`, `Classical.choice` and `Quot.sound`. A `sorry` (`sorryAx`), `native_decide`,
or an `axiom` you declare yourself all fail the theorem.
