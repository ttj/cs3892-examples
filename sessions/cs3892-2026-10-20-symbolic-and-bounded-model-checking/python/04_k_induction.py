# FIGURE: figures/add2.svg   (the state machine, drawn -- scripts/draw_models.py)
"""Session 16 -- k-induction: from bounded checks to a proof for every length.

k-induction makes two queries, neither of which mentions an unbounded run:

  BASE (k)   no counterexample of length < k            -- that is BMC
  STEP (k)   P(s_0) and ... and P(s_{k-1}), joined by T, implies P(s_k)
             for ANY states s_0 .. s_k -- reachable or not

If both are unsat, P holds on runs of every length. With k = 1, STEP is
session 9's consecution. A bigger k lets the step assume more history.

The machine is session 9's add-2 counter:  x := 0;  x := x + 2.   P: x != 5.
P is true (every reachable x is even) and, as session 9 showed, not inductive:
3 satisfies P and steps to 5. Here we see that no k rescues it over the
integers -- the step query is satisfiable at every k, by the run that climbs
through odd numbers: 5 - 2k, ..., 1, 3, 5. Strengthening P to "x is even"
(session 9's fix) proves it with k = 1.

Then the same machine on a FINITE range, x in 0..15 with wrap-around, which is
what smv/05_add2_finite.smv gives NuSMV: the longest run through odd numbers
that avoids 5 has 7 steps (7, 9, ..., 15, 1, 3), so k-induction succeeds at
k = 8. (Finite is not enough in general: a LOOP of unreachable P-states would
defeat every k. Requiring the states s_0 .. s_k to be distinct -- Een and
Sorensson, 2003 -- is what makes k-induction complete on finite systems.)

Expected: the assertions at the bottom hold.
"""

from z3 import And, Int, Not, Or, Solver, sat, unsat


def base(I, T, P, k, dom=lambda x: True):
    xs = [Int("b_%d" % i) for i in range(k)]
    s = Solver()
    if k == 0:
        return True
    s.add(I(xs[0]), *[dom(x) for x in xs], *[T(xs[i], xs[i + 1]) for i in range(k - 1)])
    s.add(Or(*[Not(P(x)) for x in xs]))
    return s.check() == unsat


def step(T, P, k, dom=lambda x: True):
    xs = [Int("s_%d" % i) for i in range(k + 1)]
    s = Solver()
    s.add(*[dom(x) for x in xs])
    s.add(*[T(xs[i], xs[i + 1]) for i in range(k)])
    s.add(*[P(x) for x in xs[:k]], Not(P(xs[k])))
    if s.check() == sat:
        m = s.model()
        return [m.eval(x).as_long() for x in xs]
    return None


I = lambda x: x == 0
T = lambda x, y: y == x + 2
P = lambda x: x != 5

print("add-2 over the integers, P: x != 5")
witnesses = {}
for k in range(1, 7):
    w = step(T, P, k)
    witnesses[k] = w
    print("   k = %d   base %s   step %s" % (k, "holds" if base(I, T, P, k) else "FAILS",
          "holds -> PROVED" if w is None else "fails, e.g. " + " -> ".join(map(str, w))))
assert all(witnesses[k] is not None and witnesses[k][-2:] == [3, 5] for k in witnesses)

even = lambda x: x % 2 == 0
print("\nstrengthened to 'x is even'   step at k = 1:",
      "holds -> PROVED (and even implies x != 5)" if step(T, even, 1) is None else "fails")
assert step(T, even, 1) is None and base(I, T, even, 1)

dom = lambda x: And(x >= 0, x <= 15)
Tw = lambda x, y: y == (x + 2) % 16
print("\nadd-2 on 0..15 with wrap-around, P: x != 5")
first = None
for k in range(1, 10):
    w = step(Tw, P, k, dom)
    print("   k = %d   step %s" % (k, "holds -> PROVED" if w is None else "fails, e.g. " + " -> ".join(map(str, w))))
    if w is None and first is None:
        first = k
        break
assert first == 8 and base(I, Tw, P, 8, dom)
print("\nOver the integers no k works, and the cure is a stronger invariant. Here, on a finite")
print("range, k = 8 works: the longest run through odd numbers that avoids 5 has 7 steps.")
