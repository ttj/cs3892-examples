/-
  Session 26 -- the lemma an LLM was asked to prove (llm/run.md), and a proof Lean accepts.

  Core Lean 4.33.0, no Mathlib. `grind` closes the inductive step: it normalises the arithmetic,
  including the products n * (n + 1) that omega treats as opaque atoms.
-/
namespace S26

-- SLIDE: sum
def sumTo : Nat → Nat
  | 0 => 0
  | n + 1 => (n + 1) + sumTo n

theorem two_sumTo (n : Nat) : 2 * sumTo n = n * (n + 1) := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [sumTo]
    grind

#print axioms two_sumTo
-- END

end S26
