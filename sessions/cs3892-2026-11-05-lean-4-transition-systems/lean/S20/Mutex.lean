/-
  Mutex — auto-generated from `mutex.smv`
  =========================================

  This file was produced by `scripts/smv2lean (ttj/leansmv)` from the SMV
  source `mutex.smv`. It contains:

    • Lean encodings of the SMV variable types (enums become
      `inductive`s, booleans become `Bool`, ranges become `Nat`).
    • A `State` structure holding all variables of the model.
    • A `TS` value (`<name>TS`) capturing the SMV
      `init` and `next` clauses. Nondeterministic SMV inputs
      become existentially-quantified variables in `next`.
    • For each `INVARSPEC` in the SMV, a COMMENTED Lean `theorem`
      stub (so this file stays sorry-free). Uncomment one and prove
      it; completed proofs live in `S20.MutexProofs`.

  Do NOT hand-edit this file: it will be overwritten by the next
  run of `smv2lean.py`. Add proofs in the corresponding
  `*Proofs.lean` file instead.
-/
import S20.TS

namespace S20

inductive AVal where
  | idle
  | trying
  | critical
  deriving DecidableEq, Repr

open AVal

inductive BVal where
  | idle
  | trying
  | critical
  deriving DecidableEq, Repr

open BVal

structure MutexState where
  a : AVal
  b : BVal
  move : Nat
  deriving DecidableEq, Repr

def MutexTS : TS MutexState where
  init s := s.a = .idle ∧ s.b = .idle
  step s s' :=
    ∃ move' : Nat,
    s'.move = move' ∧
    (if ((s.move = 1) ∧ (s.a = .idle)) then s'.a = .trying
    else if (((s.move = 1) ∧ (s.a = .trying)) ∧ (s.b ≠ .critical)) then s'.a = .critical
    else if ((s.move = 1) ∧ (s.a = .critical)) then s'.a = .idle
    else s'.a = s.a)
    ∧
    (if ((s.move = 2) ∧ (s.b = .idle)) then s'.b = .trying
    else if (((s.move = 2) ∧ (s.b = .trying)) ∧ (s.a ≠ .critical)) then s'.b = .critical
    else if ((s.move = 2) ∧ (s.b = .critical)) then s'.b = .idle
    else s'.b = s.b)

-- INVARSPEC 1 (from mutex.smv): !((crit_a & crit_b))
--   Exercise: uncomment and prove (or, if false, prove its negation);
--   completed proofs go in S20.MutexProofs.
-- theorem MutexTS_inv1 :
--     Invariant MutexTS (fun s => (¬((s.a = .critical) ∧ (s.b = .critical)))) := by
--   sorry

end S20
