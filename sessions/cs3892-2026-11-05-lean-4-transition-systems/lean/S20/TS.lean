/-
  Session 20 -- a transition system in Lean, and why an inductive invariant holds.

  These are the definitions HW4's `Defs.lean` gives you, with the same names: `TS`,
  `Reachable`, `InductiveInvariant`, `Invariant` and `inductive_invariant_holds`. `Reachable`
  is an inductive predicate -- the least set that contains the initial states and is closed
  under steps -- so a fact about every reachable state is proved by induction on how the state
  was reached. That induction is the whole proof of `inductive_invariant_holds`.
-/
namespace S20

-- SLIDE: ts-defs
/-- Which states are initial, and which pairs of states are steps. -/
structure TS (State : Type) where
  init : State → Prop
  step : State → State → Prop

/-- Reachable: an initial state, or one step from a reachable state. -/
inductive Reachable {State : Type} (ts : TS State) : State → Prop
  | init {s} : ts.init s → Reachable ts s
  | step {s t} : Reachable ts s → ts.step s t → Reachable ts t

/-- True initially, and kept by every step -- from ANY state, reachable or not. -/
def InductiveInvariant {State : Type} (ts : TS State) (P : State → Prop) : Prop :=
  (∀ s, ts.init s → P s) ∧ (∀ s t, P s → ts.step s t → P t)

/-- True in every reachable state. -/
def Invariant {State : Type} (ts : TS State) (P : State → Prop) : Prop :=
  ∀ s, Reachable ts s → P s
-- END

-- SLIDE: holds-proof
theorem inductive_invariant_holds {State : Type} (ts : TS State)
    (P : State → Prop) (h : InductiveInvariant ts P) :
    Invariant ts P := by
  intro s hs
  induction hs with
  | init hi => exact h.1 _ hi
  | step _ hst ih => exact h.2 _ _ ih hst
-- END

end S20
