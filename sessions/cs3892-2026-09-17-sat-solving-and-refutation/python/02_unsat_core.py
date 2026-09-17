"""Slide 30 -- when the answer is unsat, ask WHICH assumptions caused it.

A solver that says `unsat` and stops is much less useful than one that says
which of your assumptions could not hold together. Z3 returns an UNSAT CORE:
a subset of the tracked assumptions that is already contradictory.

Here five rules are asserted. Four of them are jointly impossible -- two policy
rules plus the two facts about Alex -- and the fifth is a tautology that has
nothing to do with the contradiction. The core names the four and leaves the
innocent one out.

This is the difference between "your policy is inconsistent" and "these three
rules are the inconsistency" -- the second is the one you can act on, and it is
what an automated-reasoning policy checker has to produce to be worth running.

Expected: unsat, with a core of four that excludes `unrelated`.
"""

from z3 import Bool, Implies, Not, Solver, unsat

senior = Bool("senior")          # the employee is senior staff
contractor = Bool("contractor")  # ... and is engaged as a contractor
approved = Bool("approved")      # ... and is approved for extended leave
onsite = Bool("onsite")          # ... and works onsite

s = Solver()
s.set(unsat_core=True)

# Tracked assumptions: each gets a name so the core can point at it.
s.assert_and_track(Implies(senior, approved),          "seniors_are_approved")
s.assert_and_track(Implies(contractor, Not(approved)), "contractors_never")
s.assert_and_track(senior,                             "alex_is_senior")
s.assert_and_track(contractor,                         "alex_is_a_contractor")
s.assert_and_track(Implies(onsite, onsite),            "unrelated")

print(s.check())
assert s.check() == unsat, "expected unsat"

core = sorted(str(c) for c in s.unsat_core())
print("unsat core:", core)
assert "unrelated" not in core, "the core should not name the innocent rule"
print(f"\n{len(core)} of the 5 rules are jointly impossible, and `unrelated` is")
print("not among them. The solver did not just say no --")
print("it said which rules to go and look at.")
