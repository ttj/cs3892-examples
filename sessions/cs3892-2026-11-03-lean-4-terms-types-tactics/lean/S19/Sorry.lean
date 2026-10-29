/-
  Session 19 -- `sorry` compiles, and proves nothing. So does an `axiom` you declare.

  THIS FILE IS MEANT TO WARN. It is not part of the S19 library (S19.lean does not import it);
  python/04_sorry_and_axioms.py runs it on its own and asserts every message below.
  `#print axioms` lists what a theorem finally rests on: a `sorry` anywhere underneath shows
  up as `sorryAx`, however deep it is buried. The last theorem is the opposite trap: honestly
  proved, and vacuous -- its hypothesis can never hold (Thursday's vacuity slide, in Lean).
-/
namespace S19

-- SLIDE: sorry
theorem bogus : 2 + 2 = 5 := by
  sorry                  -- Lean warns, and accepts

theorem built_on_bogus : 1 = 0 := by
  have h := bogus        -- h : 2 + 2 = 5
  omega                  -- false fact: anything

#print axioms built_on_bogus
-- END

-- SLIDE: axiom
axiom all_zero : ∀ n : Nat, n = 0    -- unchecked
theorem one_is_zero : 1 = 0 := all_zero 1
theorem two_two : 2 + 2 = 4 := by decide
#print axioms one_is_zero
#print axioms two_two
-- END

-- SLIDE: vacuous
-- No Nat is below 0, so this says nothing.
theorem vacuous (x : Nat) (h : x < 0) :
    x = 42 := by
  omega
#print axioms vacuous
-- END

end S19
