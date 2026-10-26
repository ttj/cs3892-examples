/-
  HW4 Part 1 — a tactic ladder (15 points).

  Replace every `sorry` with a proof. Each rung practises one idea; the handout's
  "Tactics you need" table lists the tactics. Do not change any statement:
  `check_hw4.py` compares each one with the original.

  The definitions used here (`triple`, `Light`, `Light.next`) are in Defs.lean.
-/
import HW4.Defs
namespace HW4.Part1

-- Rung 1 (2) — a closed computation: Lean can evaluate both sides.
theorem rung1_compute : triple 4 = 12 := by
  sorry

-- Rung 2 (2) — linear arithmetic over the natural numbers.
theorem rung2_arith (a b : Nat) (h1 : a + 2 ≤ b) (h2 : b < 7) : a < 5 := by
  sorry

-- Rung 3 (2) — proving a conjunction: one goal per side.
theorem rung3_and_intro (x : Nat) (h : x = 4) : x + 1 = 5 ∧ 2 * x = 8 := by
  sorry

-- Rung 4 (2) — using an existential (and the conjunction inside it).
theorem rung4_exists_elim (x : Nat) (h : ∃ k, x = 2 * k ∧ k > 3) : x ≥ 8 := by
  sorry

-- Rung 5 (2) — implication. Curry–Howard: a proof of P → R is a function from
-- proofs of P to proofs of R.
theorem rung5_imp (P Q R : Prop) (hpq : P → Q) (hqr : Q → R) : P → R := by
  sorry

-- Rung 6 (2) — induction on n, for a function defined by recursion on n.
theorem rung6_induction (n : Nat) : triple n = 3 * n := by
  sorry

-- Rung 7 (3) — case analysis on a type with finitely many values.
theorem rung7_cases (l : Light) : l.next.next.next = l := by
  sorry

end HW4.Part1
