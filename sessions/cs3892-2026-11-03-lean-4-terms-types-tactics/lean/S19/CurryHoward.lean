/-
  Session 19 -- Curry-Howard: a proposition is a type, and a proof is a program of that type.

  `and_swap` proves A ∧ B → B ∧ A. `swap` swaps the two halves of a pair of data. They are the
  same program: a proof of an "and" is a pair, and a proof of an implication is a function.
  Then the same theorem again, in tactics: `and_swap'` builds that function one step at a time,
  and python/02_curry_howard.py prints Lean's goal after every step.
-/
namespace S19

-- SLIDE: ch-terms
-- A proof of A ∧ B is a pair; of A → B, a function.
theorem and_swap (A B : Prop) : A ∧ B → B ∧ A :=
  fun ⟨ha, hb⟩ => ⟨hb, ha⟩

-- The same program on data: a pair of values.
def swap (α β : Type) : α × β → β × α :=
  fun ⟨a, b⟩ => ⟨b, a⟩

#check and_swap
#check swap
#eval swap Nat String (1, "one")
-- END

-- SLIDE: ch-false
-- False has no proof; given one, conclude anything.
theorem from_false (A : Prop) (h : False) : A :=
  h.elim
-- END

-- SLIDE: tactic-steps
theorem and_swap' (A B : Prop) :
    A ∧ B → B ∧ A := by
  intro h
  obtain ⟨ha, hb⟩ := h
  constructor
  · exact hb
  · exact ha
-- END

end S19
