/-
  Session 20 -- the running counter with a power switch, and a cap N in place of 10.

  The state is a structure (`on`, `x`), and a step is an inductive relation with one
  constructor per guarded transition, so a proof about "every step" is a `cases` on the step:
  one goal per transition, with the state's fields filled in. `x_le_N` proves the bound for
  EVERY cap N in one proof, which a model checker cannot do: it checks one N at a time.

  Going the other way, `reach_k` builds reachable states forward, one `Reachable.step` at a
  time, and `bound_tight` uses it as the witness that the bound N is actually reached.
-/
import S20.TS

namespace S20

-- SLIDE: switch-def
structure Ctr where
  on : Bool
  x  : Int

/-- One constructor per transition: its guard, and the state after. -/
inductive CtrStep (N : Nat) : Ctr → Ctr → Prop
  | tick {x : Int} : x < N → CtrStep N ⟨true, x⟩ ⟨true, x + 1⟩
  | wrap {x : Int} : x ≥ N → CtrStep N ⟨true, x⟩ ⟨true, 0⟩
  | off  {b : Bool} {x : Int} : CtrStep N ⟨b, x⟩ ⟨false, 0⟩
  | on   {x : Int} : CtrStep N ⟨false, x⟩ ⟨true, x⟩

def counter (N : Nat) : TS Ctr where
  init s := s = ⟨false, 0⟩
  step := CtrStep N
-- END

-- SLIDE: switch-proof
theorem x_le_N (N : Nat) :
    Invariant (counter N) (fun s => s.x ≤ N) := by
  apply inductive_invariant_holds
  constructor
  · intro s (hs : s = ⟨false, 0⟩)
    subst hs
    show (0 : Int) ≤ N
    omega
  · intro s t (hs : s.x ≤ N) (hst : CtrStep N s t)
    cases hst with
    | tick h => show _ + 1 ≤ (N : Int); omega
    | wrap h => show (0 : Int) ≤ N; omega
    | off => show (0 : Int) ≤ N; omega
    | on => exact hs
-- END

-- SLIDE: forward
/-- Switch on, then tick k times: ⟨true, k⟩ is reachable for every k ≤ N. -/
theorem reach_k (N : Nat) :
    ∀ k : Nat, k ≤ N → Reachable (counter N) ⟨true, k⟩ := by
  intro k
  induction k with
  | zero => intro _; exact .step (.init rfl) .on
  | succ k ih =>
    intro hk
    have hr : Reachable (counter N) ⟨true, k⟩ := ih (by omega)
    exact .step hr (.tick (by omega))

/-- The bound is reached, so it cannot be improved. -/
theorem bound_tight (N : Nat) :
    ∃ s, Reachable (counter N) s ∧ s.x = N :=
  ⟨⟨true, N⟩, reach_k N N (Nat.le_refl N), rfl⟩
-- END

end S20
