"""HW1 part 3 -- bounded reachability, WORKED on a different machine.

The technique, in four lines:

    unroll k steps            -> one variable per step
    constrain each transition -> x[i+1] is a legal successor of x[i]
    assert the target appears -> Or(x[i] == target)
    ask                        -> sat means REACHABLE, and the model is the trace

Here: x starts at 0 and each step adds 1 or 2. Target 7. The smallest k that
works is 4, because four steps can add at most 8 and at least 4.

Part 3 asks you the same question about a DIFFERENT machine. Do not copy the
number; copy the method, and pay attention to `smallest_k` -- finding the
threshold is the part that is actually being asked.
"""

from z3 import Int, Or, Solver, sat


def reachable(steps, target, k, x0=0):
    """Can x hit `target` within `k` steps, adding one of `steps` each time?"""
    xs = [Int(f"x{i}") for i in range(k + 1)]
    s = Solver()
    s.add(xs[0] == x0)
    for i in range(k):
        s.add(Or([xs[i + 1] == xs[i] + a for a in steps]))
    s.add(Or([x == target for x in xs]))
    return s, xs


def smallest_k(steps, target, kmax=20, x0=0):
    """The threshold: the least k for which the answer flips to sat."""
    for k in range(kmax + 1):
        s, _ = reachable(steps, target, k, x0)
        if s.check() == sat:
            return k
    return None


if __name__ == "__main__":
    for k in range(6):
        s, xs = reachable([1, 2], 7, k)
        r = s.check()
        trace = ""
        if r == sat:
            m = s.model()
            trace = "   trace: " + " -> ".join(str(m[x]) for x in xs)
        print(f"  k={k}: {r}{trace}")

    k = smallest_k([1, 2], 7)
    print(f"\n  smallest k = {k}")
    assert k == 4, f"expected the threshold at 4, got {k}"
    print("  Below it the answer is unsat because four steps of +1/+2 are needed\n"
          "  to cover 7. The threshold is a fact about the machine, not about Z3.")
