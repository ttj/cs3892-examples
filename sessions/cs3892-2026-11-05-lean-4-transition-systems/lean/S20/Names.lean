/-
  Session 20 -- where the names in a proof come from, and which way `rw` rewrites.

  `h` is not a keyword. It is a name someone chose for a hypothesis (a fact you may use), by
  convention `h` for "hypothesis", `hx` for a fact about x, `ih` for an induction hypothesis.
  A name enters the context in one of a few ways: the theorem's statement binds it, `intro`
  binds it, taking a hypothesis apart binds its pieces (`obtain`, `cases ... with`, `next`),
  or `have` proves a fact on the spot and binds it. A hypothesis nobody names shows up as
  `a✝` and cannot be referred to.

  `rw [h]` with `h : a = b` replaces every `a` in the goal by `b`; `rw [← h]` goes the other
  way. In real Lean, `rw` then tries `rfl`, so a goal it makes into `t = t` is closed. (The
  Natural Number Game's `rw` does not, which is why it asked for `rfl` after `rw [h]`.)
-/
namespace S20

-- SLIDE: names
-- (1) The statement names it: NNG's level 2, in Lean 4.33.
theorem nng2 (x y : Nat) (h : y = x + 7) : 2 * y = 2 * (x + 7) := by
  rw [h]

-- (2) `intro` names it: the same claim as an implication.
theorem nng2' (x y : Nat) : y = x + 7 → 2 * y = 2 * (x + 7) := by
  intro hy
  rw [hy]

-- (3) Taking a hypothesis apart names the pieces.
theorem even_add2 (n : Nat) (h : ∃ k, n = 2 * k) : ∃ m, n + 2 = 2 * m := by
  obtain ⟨k, hk⟩ := h
  exact ⟨k + 1, by omega⟩

-- (4) Nobody names it: Lean shows a✝, and you cannot use it by name.
theorem nng2'' (x y : Nat) : y = x + 7 → 2 * y = 2 * (x + 7) := by
  intro
  subst y
  rfl
-- END

-- SLIDE: rw-direction
-- `rw [h]` rewrites left to right: y becomes x + 7.
theorem rw_fwd (x y : Nat) (h : y = x + 7) : y + 1 = x + 8 := by
  rw [h]

-- `rw [← h]` rewrites right to left: x + 7 becomes y.
theorem rw_back (x y : Nat) (h : y = x + 7) : 2 * (x + 7) = 2 * y := by
  rw [← h]
-- END

end S20
