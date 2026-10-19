# FIGURE: figures/counter.svg   (the state machine, drawn -- scripts/draw_models.py)
"""Session 16 -- reachability on SETS of states, the way NuSMV does it.

The running counter again:   x := 0;   x < 10 : x := x + 1;   otherwise x := 0.

Last Tuesday's slide 6 wrote the safety check as a fixpoint:

    Reach_0     = S_0                                   (the initial states)
    Reach_{k+1} = Reach_k  union  Post(Reach_k)          until nothing is added

and the property P holds in every reachable state iff  Reach and not P  is
empty. Here every one of those sets is a BDD (bdd.py), and Post is computed
on the whole set at once -- the IMAGE of Z under the transition relation T:

    Post(Z)(x')  =  exists x .  Z(x)  and  T(x, x')

then x' is renamed back to x. One BDD operation per step, however many states
Z holds. The fixpoint is detected the cheap way: Reach_{k+1} is the same node
as Reach_k (BDDs are canonical; see 01).

Expected: the assertions at the bottom hold.
"""

from bdd import BDD, at_most, number

N = 5                                     # x in 0..25 needs five bits
b = BDD(nvars=2 * N)
X = [2 * i for i in range(N)]             # x4 .. x0  at even levels
XP = [2 * i + 1 for i in range(N)]        # x4'.. x0' interleaved after them


def step(v):
    return v + 1 if v < 10 else 0


# The transition relation, built here by listing the 26 values. A model checker
# builds the same diagram from the SMV text without enumerating anything.
T = 0
for v in range(26):
    T = b.OR(T, b.AND(number(b, X, v), number(b, XP, step(v))))


def post(Z):
    image = b.exists(X, b.AND(Z, T))                     # a set of x' values
    return b.rename(image, {xp: x for xp, x in zip(XP, X)})


reach = number(b, X, 0)                                  # Reach_0 = { x = 0 }
print("   k  |Reach_k|  BDD nodes")
history = [reach]
while True:
    k = len(history) - 1
    print("  %2d     %3d       %3d" % (k, b.count(reach, X), b.size(reach)))
    nxt = b.OR(reach, post(reach))
    if nxt == reach:                                     # the same node: a fixpoint
        print("  %2d  the same node as Reach_%d: fixpoint" % (k + 1, k))
        break
    reach = nxt
    history.append(reach)

P10, P9 = at_most(b, X, 10), at_most(b, X, 9)
bad10 = b.AND(reach, b.NOT(P10))
bad9 = b.AND(reach, b.NOT(P9))
print("\n   AG (x <= 10):  Reach and not P is", "EMPTY -> holds" if bad10 == 0 else "not empty")
first = next(k for k, r in enumerate(history) if b.AND(r, b.NOT(P9)) != 0)
print("   AG (x <= 9):   Reach and not P is", "empty" if bad9 == 0 else
      "NOT empty -> fails; a bad state first appears in Reach_%d" % first)

assert len(history) == 11 and b.count(reach, X) == 11       # fixpoint after 10 steps
assert [b.size(r) for r in history] == [7, 6, 7, 5, 7, 6, 7, 4, 7, 6, 7]   # the slide's table
assert b.size(T) == 36
assert bad10 == 0 and bad9 != 0 and first == 10
assert reach == P10                                       # Reach IS the node for 'x <= 10'
print("\n   The reachable set IS the property 'x <= 10', as a diagram of",
      b.size(reach), "nodes; T has", b.size(T), "nodes for 26 states.")
