/-
  Counter — auto-generated from `counter.smv`
  ===========================================

  This file was produced by `scripts/smv2lean (ttj/leansmv)` from the SMV
  source `counter.smv`. It contains:

    • Lean encodings of the SMV variable types (enums become
      `inductive`s, booleans become `Bool`, ranges become `Nat`).
    • A `State` structure holding all variables of the model.
    • A `TS` value (`<name>TS`) capturing the SMV
      `init` and `next` clauses. Nondeterministic SMV inputs
      become existentially-quantified variables in `next`.
    • For each `INVARSPEC` in the SMV, a COMMENTED Lean `theorem`
      stub (so this file stays sorry-free). Uncomment one and prove
      it; completed proofs live in `S20.CounterProofs`.

  Do NOT hand-edit this file: it will be overwritten by the next
  run of `smv2lean.py`. Add proofs in the corresponding
  `*Proofs.lean` file instead.
-/
import S20.TS

namespace S20

inductive ModeVal where
  | off
  | on
  deriving DecidableEq, Repr

open ModeVal

structure CounterState where
  mode : ModeVal
  press : Bool
  x : Nat
  deriving DecidableEq, Repr

def CounterTS : TS CounterState where
  init s := s.mode = .off ∧ s.x = 0
  step s s' :=
    ∃ press' : Bool,
    s'.press = press' ∧
    (if ((s.mode = .off) ∧ (s.press = false)) then s'.mode = .off
    else if ((s.mode = .off) ∧ (s.press = true)) then s'.mode = .on
    else if (((s.mode = .on) ∧ (s.press = false)) ∧ (s.x < 10)) then s'.mode = .on
    else if ((s.mode = .on) ∧ ((s.press = true) ∨ (s.x ≥ 10))) then s'.mode = .off
    else s'.mode = s.mode)
    ∧
    (if (((s.mode = .on) ∧ (s.press = false)) ∧ (s.x < 10)) then s'.x = (s.x + 1)
    else if ((s.mode = .on) ∧ ((s.press = true) ∨ (s.x ≥ 10))) then s'.x = 0
    else s'.x = s.x)

-- INVARSPEC 1 (from counter.smv): (x <= count_max)
--   Exercise: uncomment and prove (or, if false, prove its negation);
--   completed proofs go in S20.CounterProofs.
-- theorem CounterTS_inv1 :
--     Invariant CounterTS (fun s => (s.x ≤ 10)) := by
--   sorry

-- INVARSPEC 2 (from counter.smv): ((mode = off) -> (x = 0))
--   Exercise: uncomment and prove (or, if false, prove its negation);
--   completed proofs go in S20.CounterProofs.
-- theorem CounterTS_inv2 :
--     Invariant CounterTS (fun s => ((s.mode = .off) → (s.x = 0))) := by
--   sorry

-- INVARSPEC 3 (from counter.smv): (x < count_max)
--   Exercise: uncomment and prove (or, if false, prove its negation);
--   completed proofs go in S20.CounterProofs.
-- theorem CounterTS_inv3 :
--     Invariant CounterTS (fun s => (s.x < 10)) := by
--   sorry

end S20
