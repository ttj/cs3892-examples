"""Session 19 -- sets as predicates; a constructive proof and a classical one.

A set of α's is its membership test, α → Prop, so x ∈ A ∪ B is literally x ∈ A ∨ x ∈ B.
`compl_union` proves De Morgan for union, (A ∪ B)ᶜ = Aᶜ ∩ Bᶜ, without ever asking whether
x ∈ A is true or false: it is constructive, and `#print axioms` shows no Classical.choice.
`not_not` (¬¬p → p) has no such proof: it splits on `by_cases hp : p`, which is classical,
and Classical.choice appears. (HW4 Part 2 proves the ∩ version, which needs by_cases too.)

Expected: the assertions at the bottom hold.
"""
from lean_cli import lean, goals, show, show_goals

F = "S19/Sets.lean"
show(F, "compl-union")
print("Lean's goal at each step:")
show_goals(F, "compl-union")
g = dict(goals(F, "compl-union"))
assert g["constructor"].endswith("⊢ ¬(x ∈ A ∨ x ∈ B) ↔ ¬x ∈ A ∧ ¬x ∈ B")
assert "h : ¬(x ∈ A ∨ x ∈ B)" in g["exact ⟨fun ha => h (Or.inl ha), fun hb => h (Or.inr hb)⟩"]
assert g["cases h with"].endswith("h : x ∈ A ∨ x ∈ B\n⊢ False")

show(F, "classical")
rc, out = lean(F)
print("Lean says:\n  " + out.replace("\n", "\n  ") + "\n")
assert rc == 0, out
assert out.split("\n") == [
    "'S19.Set.compl_union' depends on axioms: [propext, Quot.sound]",
    "'S19.not_not' depends on axioms: [propext, Classical.choice, Quot.sound]"], out
print("constructive: no Classical.choice; by_cases: Classical.choice")
