/-
  Session 21 -- session 14's two vending machines in Cslib: one HML formula tells them apart, so
  (by the Hennessy-Milner theorem, which Cslib proves) they are not bisimilar.

  Both machines take a coin and serve coffee or tea, and they have the same traces. LATE takes the
  coin and then lets you choose; EARLY commits to a drink as it takes the coin. The formula
  "some coin leads to a state where tea is impossible" holds for EARLY (the coin into paidC) and
  fails for LATE (after its only coin, tea is still possible).
-/
import Cslib.Logics.HML.Basic

namespace S21
open Cslib Cslib.Logic.HML

-- SLIDE: vend-lts
/-- Both machines' states in one LTS: LATE is idleL, paid; EARLY is idleE, paidC, paidT. -/
inductive St where
  | idleL | paid | idleE | paidC | paidT
deriving DecidableEq

inductive Act where
  | coin | coffee | tea

inductive Tr : St → Act → St → Prop
  | coin    : Tr .idleL .coin .paid
  | coffee  : Tr .paid .coffee .idleL
  | tea     : Tr .paid .tea .idleL
  | coinC   : Tr .idleE .coin .paidC
  | coinT   : Tr .idleE .coin .paidT
  | coffeeE : Tr .paidC .coffee .idleE
  | teaE    : Tr .paidT .tea .idleE

def vend : LTS St Act := ⟨Tr⟩
-- END

-- SLIDE: hml
/-- ⟨coin⟩¬⟨tea⟩⊤: some coin leads to a state where tea is impossible. -/
def φ : Proposition Act := .diamond .coin (.not (.diamond .tea .true))

theorem early_sat : Satisfies vend .idleE φ :=
  ⟨.paidC, .coinC, fun ⟨_, h, _⟩ => by cases h⟩   -- paidC: no tea

theorem late_not_sat : ¬ Satisfies vend .idleL φ := by
  rintro ⟨s, h, hno⟩
  cases h                                          -- the only coin goes to paid
  exact hno ⟨.idleL, .tea, trivial⟩                -- and paid serves tea
-- END

/-- Five states, so every set of states is finite: what the Hennessy-Milner theorem needs. -/
instance : Fintype St :=
  Fintype.ofList [.idleL, .paid, .idleE, .paidC, .paidT] (fun s => by cases s <;> simp)

-- SLIDE: not-bisim
/-- So idleL and idleE are not bisimilar: Hennessy-Milner (Cslib) turns a separating formula
    into a proof. `vend` is finite-state, so it is image-finite, as the theorem requires. -/
theorem not_bisimilar : ¬ (LTS.HomBisimilarity vend .idleL .idleE) := by
  intro h
  rw [← theoryEq_eq_bisimilarity] at h
  exact late_not_sat (theoryEq_satisfies (φ := φ) (show TheoryEq vend .idleE .idleL from h.symm) early_sat)

#print axioms not_bisimilar
-- END

end S21
