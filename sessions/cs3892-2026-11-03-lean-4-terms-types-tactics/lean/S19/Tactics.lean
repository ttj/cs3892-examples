/-
  Session 19 -- what the closing tactics do, and where one stops.

  rfl and decide close a goal by computing; omega decides linear arithmetic over Nat and Int;
  simp rewrites with lemmas tagged @[simp]. OmegaStops.lean holds a goal omega cannot do,
  because x * x is not linear: python/03_tactics.py asserts the error Lean gives.
-/
namespace S19

-- SLIDE: closers
example : 2 ^ 10 = 1024 := rfl        -- compute
example : 7 * 6 ≠ 41 := by decide     -- evaluate
example (x : Nat) (h : x < 10) :
    x + 1 ≤ 10 := by omega            -- linear
example (xs : List Nat) :
    (xs ++ []).length = xs.length := by simp
-- END

end S19
