"""Session 19 -- the tactics that close a goal, and one that gives up.

`rfl` closes a goal whose two sides compute to the same value; `decide` evaluates a decidable
claim; `omega` decides linear arithmetic over Nat and Int; `simp` rewrites with the lemmas
tagged @[simp]. OmegaStops.lean asks omega for x <= x * x: true, but x * x is not linear, so
omega fails -- and says what it could not rule out. A failing tactic is an error, and the file
does not compile.

Expected: the assertions at the bottom hold.
"""
from lean_cli import lean, show

show("S19/Tactics.lean", "closers")
rc, out = lean("S19/Tactics.lean")
assert rc == 0 and out == "", out
print("Lean says: nothing -- every example is proved\n")

show("S19/OmegaStops.lean", "omega-stops")
rc, out = lean("S19/OmegaStops.lean")
print("Lean says:\n  " + out.replace("\n", "\n  ") + "\n")
assert rc == 1, out
assert "error: omega could not prove the goal" in out and "b := ↑x * ↑x" in out, out
print("omega: linear arithmetic only; x * x is an opaque term to it")
