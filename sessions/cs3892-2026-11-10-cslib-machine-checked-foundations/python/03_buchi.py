# FIGURE: figures/nba_fg_n.svg   (session 12's NBA for F G n -- scripts/draw_models.py)
"""Session 21 -- three theorems about Buchi automata from session 12, machine-checked in Cslib.

inter_language_eq: the product construction with a one-bit flag (generalized Buchi -> Buchi)
accepts exactly the intersection of the two languages -- the intersection step of the LTL
model-checking pipeline. not_da_buchi: some omega-regular language has NO deterministic Buchi
automaton, even an infinite-state one (Cslib's witness: "eventually only 0s", session 12's F G n).
compl: omega-regular languages are closed under complement (via Buchi's congruence).
Each rests on Lean's standard three axioms only.

Expected: the assertions at the bottom hold.
"""
from lean_cli import messages, show

F = "S21/Results.lean"
show(F, "buchi")
show(F, "axioms")
rc, ms = messages(F)
assert rc == 0, ms
out = [t for _, t in ms]
print("Lean says:\n  " + "\n  ".join(out).replace("\n", "\n  ") + "\n")
inter = [t for t in out if t.startswith("@Automata.NA.Buchi.inter_language_eq")][0]
dba = [t for t in out if t.startswith("ωLanguage.IsRegular.not_da_buchi")][0]
comp = [t for t in out if t.startswith("@ωLanguage.IsRegular.compl")][0]
assert inter.rstrip().endswith("⨅ i, Automata.ωAcceptor.language { toNA := na i, accept := acc i }")
assert dba.endswith("∃ Symbol p, p.IsRegular ∧ ¬∃ State da, Automata.ωAcceptor.language da = p")
assert comp.endswith("p.IsRegular → pᶜ.IsRegular")
axioms = [t for t in out if "depends on axioms" in t]
assert len(axioms) == 4 and all(t.endswith("[propext, Classical.choice, Quot.sound]") for t in axioms)
print("intersection, DBA < NBA, complement: all proved in Cslib, on the standard axioms")
