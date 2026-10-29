"""Session 19 -- Curry-Howard: a proposition is a type, and a proof is a program of that type.

`and_swap` proves A ∧ B → B ∧ A with a function that takes a pair of proofs apart and puts it
back together the other way round. `swap` is the same function on a pair of data. `#check`
shows that each is a value of the type its statement names.

Then `and_swap'`: the same theorem, proved with tactics. Each tactic changes the goal, and this
script prints Lean's goal before every line -- the panel the Lean editor shows as you type.

Expected: the assertions at the bottom hold.
"""
from lean_cli import lean, goals, show, show_goals

F = "S19/CurryHoward.lean"
show(F, "ch-terms")
show(F, "ch-false")
rc, out = lean(F)
print("Lean says:\n  " + out.replace("\n", "\n  ") + "\n")
assert rc == 0 and "warning" not in out and "error" not in out, out
assert out.split("\n") == ["S19.and_swap (A B : Prop) : A ∧ B → B ∧ A",
                           "S19.swap (α β : Type) : α × β → β × α",
                           '("one", 1)'], out

show(F, "tactic-steps")
print("Lean's goal at each step:")
show_goals(F, "tactic-steps")
steps = goals(F, "tactic-steps")
assert [s for s, _ in steps] == ["intro h", "obtain ⟨ha, hb⟩ := h", "constructor",
                                 "· exact hb", "· exact ha", ""]
st = [g for _, g in steps]
assert st[0] == "A B : Prop\n⊢ A ∧ B → B ∧ A"
assert st[1] == "A B : Prop\nh : A ∧ B\n⊢ B ∧ A"
assert st[2] == "A B : Prop\nha : A\nhb : B\n⊢ B ∧ A"
assert st[3].startswith("case left") and "⊢ B\n\ncase right" in st[3] and st[3].endswith("⊢ A")
assert st[4] == "case right\nA B : Prop\nha : A\nhb : B\n⊢ A"
assert st[5] == "no goals"
print("and_swap (a term) and and_swap' (tactics) prove the same proposition")
