# FIGURE: figures/vacuous.svg   (c/vacuous.c, the harness, drawn -- scripts/draw_models.py)
"""Session 18 -- vacuous specifications: "verified", and saying nothing.

D7's middle column, in code. Three ways a specification can pass while constraining
nothing -- each is a pattern found in machine-written specifications -- and the check
that exposes each one:

  1. An assumption nobody can meet. c/vacuous.c assumes n > 10 and n < 5, then asserts
     0. CBMC: VERIFICATION SUCCESSFUL -- about no runs at all. cbmc --cover assume shows
     the code after the assume is unreachable.
  2. A precondition nobody can meet: "requires n > 10 && n < 5". Check: is the
     precondition satisfiable?
  3. A postcondition true of every result. For clamp(v, lo, hi):
         ensures result >= lo || result <= hi
     follows from "requires lo <= hi" alone, so every function, correct or not,
     satisfies it. Check: does the precondition imply it without looking at the code?
     The useful contract says lo <= result <= hi, and result = v when v is in range.

Expected: the assertions at the bottom hold.
"""
from pathlib import Path

from z3 import And, Implies, Ints, Not, Or, Solver, sat, unsat

from cbmc_cli import run

C = Path(__file__).resolve().parent.parent / "c"

out = run("cbmc", C / "vacuous.c")
cov = run("cbmc", C / "vacuous.c", "--cover", "assume")
print("1. $ cbmc vacuous.c")
print("      " + next(l for l in out.splitlines() if "VERIFICATION" in l).strip())
print("   $ cbmc vacuous.c --cover assume")
print("      ... " + next(l for l in cov.splitlines() if "after assume" in l).split("function main ")[1].strip())
assert "VERIFICATION SUCCESSFUL" in out
assert "after assume(n > 10 && n < 5): FAILED" in cov       # nothing gets past the assume

n, v, lo, hi, result = Ints("n v lo hi result")
s = Solver()
s.add(And(n > 10, n < 5))
print("\n2. requires n > 10 && n < 5:   satisfiable?", s.check())
assert s.check() == unsat


def valid(f):
    t = Solver()
    t.add(Not(f))
    return t.check() == unsat


weak = Or(result >= lo, result <= hi)
print("\n3. clamp: requires lo <= hi")
print("   ensures result >= lo || result <= hi     true for EVERY result?",
      valid(Implies(lo <= hi, weak)))
useful = And(lo <= result, result <= hi, Implies(And(lo <= v, v <= hi), result == v))
print("   ensures lo <= result <= hi, and result = v when v is in range:   true for every result?",
      valid(Implies(lo <= hi, useful)))
assert valid(Implies(lo <= hi, weak))                 # vacuous: needs no code at all
assert not valid(Implies(lo <= hi, useful))           # this one actually constrains the code
