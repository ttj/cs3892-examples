# FIGURE: figures/vend_lts.svg   (session 14's two vending machines as one LTS -- scripts/draw_models.py)
"""Session 21 -- session 14's two vending machines in Cslib, told apart by one HML formula.

LATE takes the coin and then lets you choose; EARLY commits to a drink as it takes the coin.
Session 14 showed they have the same traces and are not bisimilar. Here they are one Cslib LTS
(`vend`), and the Hennessy-Milner formula <coin>not<tea>true -- "some coin leads to a state where
tea is impossible" -- holds at idleE (the coin into paidC) and fails at idleL (its only coin goes
to paid, which serves tea). Cslib's Hennessy-Milner theorem says states with the same formulas
are bisimilar and vice versa, so one separating formula PROVES that idleL and idleE are not
bisimilar. Lean checks that proof against Cslib's theorem.

Expected: the assertions at the bottom hold.
"""
from lean_cli import messages, goals, show, show_goals

F = "S21/Vending.lean"
show(F, "vend-lts")
show(F, "hml")
show(F, "not-bisim")
rc, ms = messages(F)
print("Lean says:\n  " + "\n  ".join(t for _, t in ms) + "\n")
assert rc == 0 and [s for s, _ in ms] == ["information"], ms
assert ms[0][1] == "'S21.not_bisimilar' depends on axioms: [propext, Classical.choice, Quot.sound]"
print("Lean's goal at each step of late_not_sat:")
show_goals(F, "hml")
g = dict(goals(F, "hml"))
assert g["exact hno ⟨.idleL, .tea, trivial⟩"].startswith("case coin")      # one coin only
assert "Satisfies vend St.paid" in g["exact hno ⟨.idleL, .tea, trivial⟩"]
print("idleE satisfies <coin>not<tea>true, idleL does not: by Hennessy-Milner, not bisimilar")
