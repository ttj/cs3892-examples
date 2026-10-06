# FIGURE: figures/nba_fg_n.svg   (the automata, drawn -- scripts/draw_models.py)
"""Session 13 -- the same automata, read on INFINITE words.

A reactive system never stops, so its runs are infinite words. A Buchi
automaton reads one and ACCEPTS if some run of it visits an accepting state
INFINITELY OFTEN. Nothing else about the automaton changes.

Infinite words are tested here as LASSOS  u v v v ...  (written u(v)^w): the
shape of every LTL counterexample NuSMV prints. Two omega-regular languages
that differ always differ on some lasso, so lassos are the right test words.

    1. END_D, the DFA for "ends with d", read as a Buchi automaton accepts
       exactly the words with infinitely many d:  G F d.
    2. F G n -- "eventually, no more deletes" -- needs a GUESS: an NBA.
    3. "d at every even position" -- omega-regular, but no LTL formula says it.
    4. No complete deterministic Buchi automaton with at most 3 states accepts
       F G n: every one of them disagrees with F G n on some short lasso, so
       none of them can recognize it. (A partial one can be completed with a
       rejecting sink, so the bound covers those too, at one state more. For
       every size, no deterministic Buchi automaton recognizes F G n at all:
       Landweber, 1969.) For contrast, the same search finds automata that
       agree with G F d on every test lasso -- END_D is one.

Expected: the assertions at the bottom hold.
"""
import itertools

SIGMA = "dn"


def lassos(max_u, max_v):
    for i in range(max_u + 1):
        for u in itertools.product(SIGMA, repeat=i):
            for j in range(1, max_v + 1):
                for v in itertools.product(SIGMA, repeat=j):
                    yield "".join(u), "".join(v)


def letter(u, v, i):
    return u[i] if i < len(u) else v[(i - len(u)) % len(v)]


def nba_accepts(nba, u, v):
    """Some run visits an accepting state infinitely often <=> in the product of
    the automaton with the lasso's positions, an accepting node lies on a cycle."""
    start, acc, delta = nba
    npos = len(u) + len(v)
    nxt = lambda i: i + 1 if i + 1 < npos else len(u)          # the loop goes back to v
    succ = lambda node: [(r, nxt(node[1])) for r in delta.get((node[0], letter(u, v, node[1])), ())]
    reach, todo = {(start, 0)}, [(start, 0)]
    while todo:
        for m in succ(todo.pop()):
            if m not in reach:
                reach.add(m); todo.append(m)
    for a in (n for n in reach if n[0] in acc):
        seen, todo = set(), succ(a)
        while todo:
            m = todo.pop()
            if m == a:
                return True
            if m not in seen:
                seen.add(m); todo.extend(succ(m))
    return False


def dba_accepts(start, acc, delta, u, v):
    """Deterministic: one run. Walk u, then whole copies of v until the state at
    the start of v repeats; the states seen on that cycle are the ones visited
    infinitely often."""
    q = start
    for a in u:
        q = delta[(q, a)]
    seen, order = {}, []
    while q not in seen:
        seen[q] = len(order); order.append(q)
        for a in v:
            q = delta[(q, a)]
    inf = set()
    for p in order[seen[q]:]:
        for a in v:
            inf.add(p); p = delta[(p, a)]
    return bool(inf & acc)


# The semantics, evaluated directly on a lasso.
GF_d = lambda u, v: "d" in v                                    # infinitely many d
FG_n = lambda u, v: "d" not in v                                # finitely many d
EVEN = lambda u, v: all(letter(u, v, i) == "d"                  # d at positions 0, 2, 4, ...
                        for i in range(0, len(u) + 2 * len(v), 2))

# 1. END_D -- the same four edges as the finite-word DFA "ends with d".
END_D = ("q0", {"q1"}, {("q0", "n"): {"q0"}, ("q0", "d"): {"q1"},
                        ("q1", "d"): {"q1"}, ("q1", "n"): {"q0"}})
# 2. F G n -- q0 reads anything; on an n it may GUESS that the deletes are over.
FG_NBA = ("q0", {"q1"}, {("q0", "d"): {"q0"}, ("q0", "n"): {"q0", "q1"},
                         ("q1", "n"): {"q1"}})                  # q1 on d: no move, the guess dies
# 3. d at every even position -- deterministic, with a dead end on a bad letter.
EVEN_DBA = ("e", {"e"}, {("e", "d"): {"o"}, ("o", "d"): {"e"}, ("o", "n"): {"e"}})

L = list(lassos(3, 3))
print(f"{len(L)} lasso words u(v)^w with |u| <= 3, 1 <= |v| <= 3")
for name, nba, sem in (("END_D as Buchi = G F d", END_D, GF_d),
                       ("NBA for F G n", FG_NBA, FG_n),
                       ("d at every even position", EVEN_DBA, EVEN)):
    assert all(nba_accepts(nba, u, v) == sem(u, v) for u, v in L), name
    print(f"  {name:26} agrees with its meaning on all {len(L)}")

for u, v in (("", "nd"), ("d", "n"), ("dd", "n"), ("", "dn")):
    w = u + "(" + v + ")^w"
    print(f"  {w:9}  G F d {GF_d(u, v)!s:5}  F G n {FG_n(u, v)!s:5}  even-d {EVEN(u, v)}")

# 4. Search every COMPLETE deterministic Buchi automaton with k <= 3 states.
#    Disagreeing on one lasso is a proof that an automaton does not recognize
#    the language; agreeing on all of them is only evidence.
L4 = list(lassos(4, 4))
print(f"\nevery complete deterministic Buchi automaton over {{d, n}} with k states, "
      f"tested on {len(L4)} lassos:")
for k in (1, 2, 3):
    states = range(k)
    keys = [(q, a) for q in states for a in SIGMA]
    total = fg = gf = 0
    for targets in itertools.product(states, repeat=len(keys)):
        delta = dict(zip(keys, targets))
        for r in range(k + 1):
            for acc in itertools.combinations(states, r):
                acc = set(acc)
                total += 1
                if all(dba_accepts(0, acc, delta, u, v) == FG_n(u, v) for u, v in L4):
                    fg += 1
                if all(dba_accepts(0, acc, delta, u, v) == GF_d(u, v) for u, v in L4):
                    gf += 1
    print(f"  k = {k}: {total:5} automata   agree with F G n: {fg}   agree with G F d: {gf}")
    assert fg == 0
    assert (gf > 0) == (k >= 2)

print("\nok -- Buchi acceptance; F G n needs nondeterminism; G F d does not")
