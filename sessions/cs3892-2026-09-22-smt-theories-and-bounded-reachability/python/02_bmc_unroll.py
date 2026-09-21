"""Session 8, demo 2 -- bounded reachability: a system becomes one formula.

THE MOVE. A transition system has runs; a solver decides one fixed formula.
You reconcile those by giving each step its own copy of the state variable
and writing the transition relation down k times:

    x0 = init
    T(x0, x1)  and  T(x1, x2)  and  ...  and  T(x[k-1], xk)
    Or(  bad(x0), bad(x1), ..., bad(xk)  )          <-- the negated property

`sat` means REACHABLE and the model IS the counterexample trace.
`unsat` means not reachable WITHIN k STEPS -- and says nothing past k.

The machine here is a thermostat, NOT the counter from HW1 Part 3. Work that
one yourself; the method is the transferable part, and finding the threshold k
is what Part 3 is actually asking.

    state      t : Int, the temperature
    initial    t = 20
    transition the heater adds 3 or the room loses 1  (nondeterministic)
    bad        t >= 30
"""

from z3 import Int, Or, Solver, sat

INIT = 20
DELTAS = [3, -1]     # what one step may add -- the nondeterminism
BAD = 30             # the property is t < 30; its negation is t >= 30


def bmc(k):
    """Unroll k steps and ask whether a bad state appears on the way."""
    t = [Int(f"t{i}") for i in range(k + 1)]
    s = Solver()
    s.add(t[0] == INIT)
    for i in range(k):
        s.add(Or([t[i + 1] == t[i] + d for d in DELTAS]))
    s.add(Or([ti >= BAD for ti in t]))
    return s, t


def threshold(kmax=20):
    """The least k at which the answer flips from unsat to sat."""
    for k in range(kmax + 1):
        s, _ = bmc(k)
        if s.check() == sat:
            return k
    return None


if __name__ == "__main__":
    for k in range(5):
        s, t = bmc(k)
        r = s.check()
        trace = ""
        if r == sat:
            m = s.model()
            trace = "   trace: " + " -> ".join(str(m[ti]) for ti in t)
        print(f"  k={k}: {r}{trace}")

    k = threshold()
    print(f"\n  smallest k = {k}")
    assert k == 4, f"expected the threshold at 4, got {k}"
    print("  Four steps, because the fastest route up is +3 each time:")
    print("  20 -> 23 -> 26 -> 29 -> 32, and 32 is the first value >= 30.")
    print("  Three steps can reach at most 29. That is a fact about the")
    print("  machine's arithmetic, not about Z3.")
    print()
    print("  NOTE what k=3 does NOT tell you. `unsat` at k=3 means 'no")
    print("  counterexample within 3 steps'. It is not a proof of safety.")
