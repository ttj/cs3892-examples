/-
  Session 19 -- a goal omega cannot close. THIS FILE IS MEANT TO FAIL: x * x is not linear,
  so omega reports an error. It is not part of the S19 library (S19.lean does not import it);
  python/03_tactics.py runs it on its own and asserts the error.
-/
namespace S19

-- SLIDE: omega-stops
example (x : Nat) : x ≤ x * x := by omega  -- not linear
-- END

end S19
