"""HW1 part 1 -- logic warm-up. STARTER: one worked, five for you.

The routine below is the whole part. For each English statement you write the
formula, then ask TWO different questions about it:

    satisfiable?  is there ANY interpretation making it true?
    valid?        do ALL interpretations make it true?

A solver answers only the first. You get the second from the identity this
course runs on:  phi is valid  <=>  (not phi) is unsatisfiable.

Decide each one by hand FIRST, then run this. Where you and Z3 disagreed, say
so in your report and say who was right -- that disagreement is the whole
point of the exercise.
"""

from z3 import Bool, Implies, Not, Or, And, Solver, sat, unsat


def classify(phi, label):
    """Report satisfiable / valid / unsatisfiable for one formula."""
    s = Solver(); s.add(phi)
    is_sat = s.check() == sat
    model = s.model() if is_sat else None

    n = Solver(); n.add(Not(phi))
    is_valid = n.check() == unsat
    counter = n.model() if not is_valid else None

    verdict = ("VALID (and so satisfiable)" if is_valid
               else "satisfiable, not valid" if is_sat
               else "UNSATISFIABLE")
    print(f"{label}\n   {verdict}")
    if is_sat and not is_valid:
        print(f"   a model:          {model}")
        print(f"   a counterexample: {counter}")
    return verdict


# --- worked example ---------------------------------------------------------
# "If it is raining then the ground is wet. It is raining. Therefore the ground
#  is wet."  -- an entailment, so we check the IMPLICATION for validity.
r, w = Bool("raining"), Bool("wet")
modus_ponens = Implies(And(Implies(r, w), r), w)
v = classify(modus_ponens, "worked: modus ponens")
assert v.startswith("VALID"), "modus ponens should be valid"

# The near-miss that catches people: affirming the consequent.
affirming = Implies(And(Implies(r, w), w), r)
v = classify(affirming, "worked: affirming the consequent (the classic error)")
assert v == "satisfiable, not valid"
print("   ^ the counterexample IS the explanation: wet ground, no rain.\n")


# --- yours ------------------------------------------------------------------
# Replace each `None` with a formula over Bools (or Ints, if the statement
# needs arithmetic) and delete the `continue`. Write your by-hand answer in the
# label so the report writes itself.
STATEMENTS = [
    ("1. <your English statement here>  [by hand: ?]", None),
    ("2. <your English statement here>  [by hand: ?]", None),
    ("3. <your English statement here>  [by hand: ?]", None),
    ("4. <your English statement here>  [by hand: ?]", None),
    ("5. <your English statement here>  [by hand: ?]", None),
]

todo = 0
for label, phi in STATEMENTS:
    if phi is None:
        todo += 1
        continue
    classify(phi, label)

if todo:
    print(f"TODO: {todo} of 5 statements still to encode.")
