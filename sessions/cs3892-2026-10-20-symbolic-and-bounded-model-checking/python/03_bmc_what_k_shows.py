# FIGURE: figures/counter.svg   (the state machine, drawn -- scripts/draw_models.py)
"""Session 16 -- bounded model checking: what a clean run at bound k shows.

BMC asks a SAT/SMT solver one question per bound k: is there a run of at most
k steps from an initial state that reaches a state violating P?

    I(x_0)  and  T(x_0, x_1)  and ... and  T(x_{k-1}, x_k)
            and  ( not P(x_0)  or ... or  not P(x_k) )

sat   -> the model is a counterexample of length <= k, and it is real.
unsat -> there is no counterexample of length <= k. NOTHING follows about
         runs longer than k.

Session 9 pushed "x <= 10" out to k = 50 and got unsat fifty times, which was
still not a proof. Here is the other half: a property that is FALSE, and a
clean answer at every bound below the length of the shortest counterexample.

Expected: the assertions at the bottom hold.
"""

from z3 import And, If, Int, Not, Or, Solver, sat


def I(x):
    return x == 0


def T(x, y):
    return y == If(x < 10, x + 1, 0)


def bmc(P, k):
    xs = [Int("x_%d" % i) for i in range(k + 1)]
    s = Solver()
    s.add(I(xs[0]))
    s.add(*[T(xs[i], xs[i + 1]) for i in range(k)])
    s.add(Or(*[Not(P(x)) for x in xs]))
    if s.check() == sat:
        m = s.model()
        return [m.eval(x).as_long() for x in xs]
    return None


print("P = x <= 9, which is FALSE (the counter reaches 10)")
answers = {}
for k in range(0, 12):
    trace = bmc(lambda x: x <= 9, k)
    answers[k] = trace
    print("   k = %2d   %s" % (k, "no counterexample of length <= %d" % k if trace is None
                               else "COUNTEREXAMPLE  " + " -> ".join(map(str, trace))))

assert all(answers[k] is None for k in range(10))      # clean at every bound below 10 ...
assert answers[10] == list(range(11))                 # ... and the property is false
print("\nAt k = 9 BMC said nothing was wrong, and the property was false all along.")
print("The shortest counterexample has 10 steps; no bound below 10 can see it.")
