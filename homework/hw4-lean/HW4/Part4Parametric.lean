/-
  HW4 Part 4 — every capacity at once (18 points here + 2 for the written question).

  `bucket N` has N tokens. Part 3 proved the bound for N = 10; a model checker
  can check N = 10, then N = 11, ... but never all N. Prove it for all N.
-/
import HW4.Defs
namespace HW4.Part4
open HW4

-- (a, 10) The bound holds for every capacity N.
theorem used_le_N (N : Nat) : ∀ b, Reachable (bucket N) b → b.used ≤ N := by
  sorry

-- (b, 6) Helper: after k actions from a full bucket, the state is ⟨k, N - k⟩.
-- Prove it by induction on k.
theorem reach_k (N : Nat) : ∀ k, k ≤ N → Reachable (bucket N) ⟨k, N - k⟩ := by
  sorry

-- (c, 2) The bound is tight: some reachable state has used = N.
theorem bound_tight (N : Nat) : ∃ b, Reachable (bucket N) b ∧ b.used = N := by
  sorry

end HW4.Part4
