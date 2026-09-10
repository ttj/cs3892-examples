"""HW1 part 3 -- STARTER for the machine the homework actually asks about.

`p3_reachability_demo.py` shows the method on a toy. This is the shell for
yours. Fill in the three TODOs, then find the smallest k for which the answer
changes and be ready to say precisely WHY that k.

Read the handout for the machine's exact behaviour; do not guess it from the
demo, which deliberately uses different numbers.
"""

from z3 import Int, Or, Solver, sat

# TODO 1: the initial value of x.
X0 = None
# TODO 2: what a single step may do. The demo used [1, 2]; yours is in the handout.
STEPS = None
# TODO 3: the value you are asking about.
TARGET = None


def reachable(k):
    xs = [Int(f"x{i}") for i in range(k + 1)]
    s = Solver()
    s.add(xs[0] == X0)
    for i in range(k):
        s.add(Or([xs[i + 1] == xs[i] + a for a in STEPS]))
    s.add(Or([x == TARGET for x in xs]))
    return s, xs


def smallest_k(kmax=25):
    for k in range(kmax + 1):
        s, _ = reachable(k)
        if s.check() == sat:
            return k
    return None


if __name__ == "__main__":
    if None in (X0, STEPS, TARGET):
        print("TODO: set X0, STEPS and TARGET from the handout, then re-run.")
        print("      p3_reachability_demo.py shows the whole method worked through.")
        raise SystemExit(0)

    k = smallest_k()
    print(f"smallest k = {k}")
    if k is not None:
        s, xs = reachable(k)
        assert s.check() == sat
        m = s.model()
        print("trace:", " -> ".join(str(m[x]) for x in xs))
    print("\nNow answer the question the handout actually asks: WHY that k?")
