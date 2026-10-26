/-
  HW4 Part 2 — discrete maths, machine-checked (20 points; 4 each).

  Sets are predicates (Defs.lean). `Set.ext` turns `A = B` into "same members";
  the `mem_union` / `mem_inter` / `mem_diff` / `mem_compl` lemmas unfold what a
  membership means, and `subset_def` unfolds `⊆`.

  One of these needs classical logic: `by_cases h : x ∈ A` splits on whether a
  proposition holds. Which one, and why can the others do without it?
-/
import HW4.Defs
namespace HW4.Part2
open HW4.Set
variable {α : Type}

-- Two sets that contain each other are equal.
theorem subset_antisymm (A B : Set α) (h1 : A ⊆ B) (h2 : B ⊆ A) : A = B := by
  sorry

-- De Morgan, for an intersection.
theorem demorgan_inter (A B : Set α) : (A ∩ B)ᶜ = Aᶜ ∪ Bᶜ := by
  sorry

-- Union distributes over intersection.
theorem union_distrib_inter (A B C : Set α) : A ∪ (B ∩ C) = (A ∪ B) ∩ (A ∪ C) := by
  sorry

-- Removing a union is removing each part.
theorem diff_union (A B C : Set α) : A \ (B ∪ C) = (A \ B) ∩ (A \ C) := by
  sorry

-- Being inside an intersection is being inside both.
theorem subset_inter_iff (A B C : Set α) : C ⊆ A ∩ B ↔ C ⊆ A ∧ C ⊆ B := by
  sorry

end HW4.Part2
