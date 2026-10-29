/-
  Session 19 -- sets as predicates, a constructive proof, and where classical logic enters.

  A set of α's is its membership test, α → Prop (HW4's Defs.lean does the same, so HW4 needs
  nothing beyond core Lean). `compl_union` is De Morgan for ∪: (A ∪ B)ᶜ = Aᶜ ∩ Bᶜ. Its proof
  never asks whether x ∈ A is true or false, so it is constructive. `not_not` (¬¬p → p) cannot
  be proved that way: it needs `by_cases`, which uses the axiom of choice. `#print axioms`
  shows the difference. (HW4 Part 2 proves the ∩ version and four other identities; none of
  them is proved here.)
-/
namespace S19

def Set (α : Type) : Type := α → Prop

namespace Set
variable {α : Type}

instance : Membership α (Set α) := ⟨fun A x => A x⟩

def union (A B : Set α) : Set α := fun x => x ∈ A ∨ x ∈ B
def inter (A B : Set α) : Set α := fun x => x ∈ A ∧ x ∈ B
def compl (A : Set α) : Set α := fun x => ¬ x ∈ A

instance : Union (Set α) := ⟨union⟩
instance : Inter (Set α) := ⟨inter⟩
postfix:max "ᶜ" => compl

@[simp] theorem mem_union (x : α) (A B : Set α) : (x ∈ A ∪ B) = (x ∈ A ∨ x ∈ B) := rfl
@[simp] theorem mem_inter (x : α) (A B : Set α) : (x ∈ A ∩ B) = (x ∈ A ∧ x ∈ B) := rfl
@[simp] theorem mem_compl (x : α) (A : Set α) : (x ∈ Aᶜ) = (¬ x ∈ A) := rfl

/-- Two sets are equal when they have the same members. -/
theorem ext {A B : Set α} (h : ∀ x, x ∈ A ↔ x ∈ B) : A = B :=
  funext fun x => propext (h x)

-- SLIDE: compl-union
theorem compl_union (A B : Set α) :
    (A ∪ B)ᶜ = Aᶜ ∩ Bᶜ := by
  apply ext
  intro x
  simp only [mem_compl, mem_union, mem_inter]
  constructor
  · intro h                  -- h : ¬(x ∈ A ∨ x ∈ B)
    exact ⟨fun ha => h (Or.inl ha), fun hb => h (Or.inr hb)⟩
  · intro ⟨hna, hnb⟩ h       -- h : x ∈ A ∨ x ∈ B
    cases h with
    | inl ha => exact hna ha
    | inr hb => exact hnb hb
-- END

end Set

-- SLIDE: classical
theorem not_not (p : Prop) (h : ¬¬p) : p := by
  by_cases hp : p        -- p holds, or it does not
  · exact hp
  · exact absurd hp h    -- ¬p contradicts ¬¬p

#print axioms Set.compl_union
#print axioms not_not
-- END

end S19
