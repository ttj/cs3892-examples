/-
  HW4 Part 3 — a property that is true but not inductive (30 points).

  `bucket10` (Defs.lean) is a rate limiter with 10 tokens. The property is
  `P b := b.used ≤ 10`: at most 10 actions per window. It holds in every
  reachable state -- and it is not inductive.

  To unfold the system in a hypothesis `h`:
      simp only [bucket10_eq, bucket_init] at h      -- an initial state
      simp only [bucket10_eq, bucket_step] at h      -- a step, then `cases h`
-/
import HW4.Defs
namespace HW4.Part3
open HW4

-- (a, 6) P is not inductive: find a state that satisfies P and a step out of it
-- that breaks P. (Is that state reachable? Answer in your report.)
theorem P_not_inductive : ¬ InductiveInvariant bucket10 P := by
  sorry

-- (b, 6) The obvious strengthening, "used ≤ 10 and left ≤ 10", is not inductive either.
theorem Q_not_inductive : ¬ InductiveInvariant bucket10 Q := by
  sorry

-- (c) YOUR strengthened invariant. Replace `sorry` with a property of `b` that is
-- inductive and implies P. This definition is the whole assignment.
def Inv (b : Bucket) : Prop := sorry

-- (c, 4) It holds initially.
theorem inv_init : ∀ b, bucket10.init b → Inv b := by
  sorry

-- (c, 8) Every step preserves it -- from ANY state satisfying Inv.
theorem inv_step : ∀ b c, Inv b → bucket10.step b c → Inv c := by
  sorry

-- (d, 6) So P holds in every reachable state. (`inductive_invariant_holds` is in Defs.lean.)
theorem used_le_10 : ∀ b, Reachable bucket10 b → b.used ≤ 10 := by
  sorry

end HW4.Part3
