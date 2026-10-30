/-
  Session 20 -- session 9's add-2 machine in Lean: a property that is true and not inductive,
  and the stronger invariant that proves it.

  add-2 starts at 0 and adds 2 forever. `P x := x ≠ 5` holds in every reachable state (every
  reachable x is even), but it is not inductive: 3 satisfies P and steps to 5. 3 is a
  counterexample to induction (a CTI), not a bug, because no run reaches it. The cure is a
  STRONGER invariant, "x is even", which is inductive and implies P.
-/
import S20.TS

namespace S20

-- SLIDE: add2-def
/-- Start at 0; add 2, forever. -/
def add2 : TS Int where
  init x := x = 0
  step x y := y = x + 2

/-- The property: x is never 5. -/
def P (x : Int) : Prop := x ≠ 5
-- END

-- SLIDE: add2-cti
/-- 3 satisfies P, and its one step lands on 5. -/
theorem P_not_inductive : ¬ InductiveInvariant add2 P := by
  intro h
  have h5 : P 5 := h.2 3 5 (show (3 : Int) ≠ 5 by decide) rfl
  exact h5 rfl
-- END

-- SLIDE: add2-strengthen
/-- Stronger: x is even. -/
def Even (x : Int) : Prop := x % 2 = 0

theorem even_inductive : InductiveInvariant add2 Even := by
  constructor
  · intro x (hx : x = 0)
    show x % 2 = 0
    omega
  · intro x y (hx : x % 2 = 0) (hy : y = x + 2)
    show y % 2 = 0
    omega

theorem P_holds : Invariant add2 P := by
  intro x hx
  have he : Even x := inductive_invariant_holds _ _ even_inductive x hx
  unfold Even at he
  show x ≠ 5
  omega
-- END

end S20
