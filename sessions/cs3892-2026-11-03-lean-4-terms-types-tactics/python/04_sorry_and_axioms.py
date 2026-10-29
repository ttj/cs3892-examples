"""Session 19 -- `sorry` compiles, and proves nothing.

`bogus` claims 2 + 2 = 5 and is "proved" by sorry: Lean warns, and accepts the file.
`built_on_bogus` uses it to prove 1 = 0 (from a false fact, anything follows). Nothing about
`built_on_bogus` itself says sorry -- but `#print axioms` lists what a theorem finally rests on,
and sorry shows up there as sorryAx. An axiom you declare yourself is the same kind of promise,
and shows up by its own name. An honest proof lists nothing, or only Lean's standard three
(propext, Classical.choice, Quot.sound): that is exactly what HW4's checker asks.
And `vacuous` passes that check while saying nothing: its hypothesis, x < 0 over Nat, never
holds. Lean checks the proof; whether the statement is the one you meant is yours to check.

Expected: the assertions at the bottom hold.
"""
from lean_cli import lean, goals, show

F = "S19/Sorry.lean"
show(F, "sorry")
show(F, "axiom")
show(F, "vacuous")
rc, out = lean(F)
print("Lean says:\n  " + out.replace("\n", "\n  ") + "\n")
assert rc == 0, out                                          # it compiles
assert out.split("\n") == [
    "S19/Sorry.lean:13:8: warning: declaration uses `sorry`",
    "'S19.built_on_bogus' depends on axioms: [propext, sorryAx, Quot.sound]",
    "'S19.one_is_zero' depends on axioms: [all_zero]",
    "'S19.two_two' does not depend on any axioms",
    "'S19.vacuous' depends on axioms: [propext, Quot.sound]"], out
assert dict(goals(F, "sorry"))["omega"].endswith("h : 2 + 2 = 5\n⊢ 1 = 0")
assert dict(goals(F, "vacuous"))["omega"].endswith("h : x < 0\n⊢ x = 42")
print("a file that compiles is not a file that proves: read #print axioms -- and the statement")
