"""HW1 part 4 -- how do you know the encoding is right?

Part 4 asks an LLM for the SMT-LIB encoding of part 3 and then asks you the
only interesting question: how did you know whether it was correct.

"I read it and it looked fine" is not an answer. An encoding that is `unsat`
for the wrong reason is indistinguishable from a correct one by inspection --
`unsat` is exactly what a contradictory, over-constrained, or empty encoding
returns. Below are three checks that actually distinguish them. Run this, then
run the same three against whatever the model hands you.
"""

from z3 import Int, Or, Solver, sat, unsat


def machine(k, target, steps=(1, 2), x0=0, sabotage=False):
    xs = [Int(f"x{i}") for i in range(k + 1)]
    s = Solver()
    s.add(xs[0] == x0)
    for i in range(k):
        s.add(Or([xs[i + 1] == xs[i] + a for a in steps]))
        if sabotage:
            # A plausible-looking typo: the step is also forced to be zero.
            s.add(xs[i + 1] == xs[i])
    s.add(Or([x == target for x in xs]))
    return s


print("CHECK 1 -- does a target you KNOW is reachable come back sat?")
print("   An encoding that says unsat to everything is not a proof, it is a bug.")
for name, sab in (("honest", False), ("sabotaged", True)):
    r = machine(4, 7, sabotage=sab).check()
    print(f"   {name:>10}: reach 7 in 4 steps -> {r}")
assert machine(4, 7).check() == sat
assert machine(4, 7, sabotage=True).check() == unsat
print("   The sabotaged one 'proves' unreachability. It is simply broken.\n")

print("CHECK 2 -- is the model an actual trace you can read?")
s = machine(4, 7)
assert s.check() == sat
m = s.model()
xs = [m[Int(f"x{i}")].as_long() for i in range(5)]
print(f"   trace: {xs}")
steps_taken = [b - a for a, b in zip(xs, xs[1:])]
print(f"   steps: {steps_taken}")
assert all(d in (1, 2) for d in steps_taken), "a step outside the machine's rules"
assert 7 in xs
print("   Every step is legal and the target really appears. A model you cannot\n"
      "   read back as a trace is a sign the encoding is not about your system.\n")

print("CHECK 3 -- does the threshold sit where the arithmetic says it should?")
below = machine(3, 7).check()
at = machine(4, 7).check()
print(f"   k=3 -> {below}   k=4 -> {at}")
assert below == unsat and at == sat
print("   Three steps add at most 6, so unsat below 4 is forced by arithmetic,\n"
      "   not by the solver. An encoding whose threshold is off by one is wrong\n"
      "   in a way that no amount of staring at it reveals.\n")

print("Run all three against the LLM's encoding. Whichever one fails IS your\n"
      "answer to 'how did you know'.")
