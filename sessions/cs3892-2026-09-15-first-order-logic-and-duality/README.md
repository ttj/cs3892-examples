# Session 6 — First-order logic and the duality

**Tuesday, September 15, 2026.** [Open the notebook in Colab](https://colab.research.google.com/github/ttj/cs3892-examples/blob/main/notebooks/cs3892-2026-09-15-first-order-logic-and-duality.ipynb)

Six examples about quantifiers. Each exists twice: as SMT-LIB, which is what
the standard looks like, and as Python, which is what you will actually write.

| # | Shows | Slide | Verdict |
|---|---|---|---|
| 01 | `forall_policy` — one rule binds a user declared after it | 21 | `unsat` |
| 02 | `forall_policy_gap` — 18 becomes 6, and the model is the hole in your spec | 21 | `sat` |
| 03 | `order_strong_implies_weak` — ∃∀ really does imply ∀∃ | 18 | `unsat` |
| 04 | `order_weak_not_strong` — ∀∃ does **not** imply ∃∀ | 18 | `sat` |
| 05 | `only_a_may_b` — "only A may B" is `B ⇒ A`, and the reversal is a different spec | 20 | `sat` |
| 06 | `negation_of_forall` — ¬∀x P(x) ≡ ∃x ¬P(x), machine-checked | 19 | `unsat` |
| 07 | `coloring_sat` — five regions in a ring, three colours; the solver finds one | 32 | `sat` |
| 08 | `coloring_unsat` — four mutually adjacent regions, three colours | 32 | `unsat` |

## The three things worth taking from these

**A quantifier is not a loop.** `01` proves something about every integer. Z3
never enumerates them — it instantiates the quantifier with the single term it
needs, derives a contradiction, and stops.

**`sat` is information, not failure.** In `02` you asked for a proof and got a
model instead. The model is the answer: the policy says nothing about service
under twelve months, so the case you were worried about is genuinely allowed.
Read the model before you change the code.

**`unsat` is a proof of impossibility.** `08` does not report "I looked and did
not find a colouring" — it reports that none exists. In the language of the
lecture, `⟦legal colouring⟧ = ∅`, which is why `unsat` is the answer you want
when you are trying to show something *cannot* happen.

**Order and direction are the specification.** `03`/`04` differ only in the
order of two quantifiers and `05` only in the direction of one arrow, and in
each pair one member is the requirement you meant and the other is not. A
solver will prove either one for you without comment.

Run them all:

```bash
bash scripts/check_examples.sh sessions/cs3892-2026-09-15-first-order-logic-and-duality
```
