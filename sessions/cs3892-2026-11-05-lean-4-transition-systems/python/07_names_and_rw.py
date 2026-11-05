"""Session 20 -- where `h` comes from, and which way `rw [h]` rewrites.

`h` is a name somebody chose for a hypothesis, not a keyword. A name enters the context when
the theorem's statement binds it, when `intro` binds it, when taking a hypothesis apart binds
its pieces (`obtain`), or never: an unnamed hypothesis shows as `a✝`. `rw [h]` with
`h : y = x + 7` replaces y by x + 7; `rw [← h]` replaces x + 7 by y. In Lean (unlike the
Natural Number Game) `rw` then tries `rfl`, so the NNG's level 2 is one line here.

Expected: the assertions at the bottom hold.
"""
from lean_cli import lean, goals, show, show_goals

F = "S20/Names.lean"
show(F, "names")
show(F, "rw-direction")
rc, out = lean(F)
assert rc == 0 and out == "", out
print("Lean's goal before each step:")
show_goals(F, "names")
g = goals(F, "names")
assert g[0] == ("rw [h]", "x y : Nat\nh : y = x + 7\n⊢ 2 * y = 2 * (x + 7)")      # the statement named it
assert g[1][1].endswith("⊢ y = x + 7 → 2 * y = 2 * (x + 7)")                   # before intro: no name yet
assert g[2] == ("rw [hy]", "x y : Nat\nhy : y = x + 7\n⊢ 2 * y = 2 * (x + 7)")  # intro named it hy
assert g[4] == ("exact ⟨k + 1, by omega⟩", "n k : Nat\nhk : n = 2 * k\n⊢ ∃ m, n + 2 = 2 * m")
assert g[6] == ("subst y", "x y : Nat\na✝ : y = x + 7\n⊢ 2 * y = 2 * (x + 7)")  # nobody named it
assert g[-1][1] == "no goals"
r = dict(goals(F, "rw-direction"))
assert r["rw [h]"].endswith("⊢ y + 1 = x + 8") and r["rw [← h]"].endswith("⊢ 2 * (x + 7) = 2 * y")
print("names come from the statement, intro, obtain -- or nowhere (a✝); rw [h] goes left to right")
