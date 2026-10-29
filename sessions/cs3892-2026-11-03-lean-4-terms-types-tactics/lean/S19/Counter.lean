/-
  Session 19 -- Lean is a programming language, and a theorem is about a program.

  The running counter (labs/running-example.md; sessions 9, 16, 18): x starts at 0;
  below 10 it counts up, otherwise it resets to 0.

      x < 10 / x := x + 1        x >= 10 / x := 0

  `step` is one move, `run x n` is the state after n moves from x. Then three theorems:
  one by computation, one for every x (the step condition from Thursday's loop
  invariant), and one by induction for every number of steps -- no bound, no unwinding.

  The regions between `-- SLIDE:` and `-- END` are printed on the slides verbatim
  (make_s19.py reads them from this file); python/01_lean_is_a_language.py runs this file
  and asserts every output the slides show.
-/
namespace S19

-- SLIDE: counter-def
/-- One move: count up to 10, then reset to 0. -/
def step (x : Nat) : Nat :=
  if x < 10 then x + 1 else 0

/-- Where the counter is after `n` moves from `x`. -/
def run (x : Nat) : Nat → Nat
  | 0     => x
  | n + 1 => step (run x n)

#eval step 3                       -- one move
#eval (List.range 13).map (run 0)  -- 0 to 12 moves
#check step
#check step 3 = 4                  -- a statement
-- END

-- SLIDE: counter-theorems
theorem step_3 : step 3 = 4 := rfl   -- by computing

theorem step_le (x : Nat) (h : x ≤ 10) :
    step x ≤ 10 := by
  unfold step               -- expose the if
  by_cases hx : x < 10
  · simp [hx]               -- leaves x ≤ 9
    omega
  · simp [hx]               -- the if is 0: done

theorem run_le (n : Nat) : run 0 n ≤ 10 := by
  induction n with
  | zero => decide          -- run 0 0 = 0
  | succ n ih => exact step_le (run 0 n) ih
-- END

end S19
