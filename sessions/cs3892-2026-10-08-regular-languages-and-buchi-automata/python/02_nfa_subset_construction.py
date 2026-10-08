# FIGURE: figures/nfa_second_last.svg   (the automata, drawn -- scripts/draw_models.py)
"""Session 13 -- nondeterminism on finite words, and why it costs nothing in power.

First the session's own language, "ends with a delete", as an NFA that guesses
which d is the last letter: its subset construction is END_D itself. Then a
case where determinism costs something:

"The second-to-last step was a delete": (d|n)* d (d|n).

An NFA for it has 3 states. It GUESSES which d is the second-to-last letter;
it accepts a word if SOME run ends in an accepting state. A wrong guess just dies.

The subset construction (Rabin and Scott, 1959) turns any NFA into a DFA whose
states are SETS of NFA states. Here that DFA has 4 states, and for "the k-th
letter from the end is d" the NFA has k + 1 states while the DFA has 2^k -- and
minimizing it shows the 2^k is not slack in the construction: every one of
those states is needed.

Expected: the assertions at the bottom hold.
"""
import itertools
import re
from collections import deque

SIGMA = "dn"


def kth_from_last(k):
    """NFA p0 -> p1 -> ... -> pk: p0 loops, guesses a d, then counts k-1 more letters."""
    delta = {(0, "d"): {0, 1}, (0, "n"): {0}}
    for i in range(1, k):
        delta[(i, "d")] = delta[(i, "n")] = {i + 1}
    return 0, {k}, delta


def nfa_accepts(nfa, word):
    start, acc, delta = nfa
    cur = {start}                          # every state some run could be in
    for a in word:
        cur = set().union(*(delta.get((q, a), set()) for q in cur))
    return bool(cur & acc)


def subset_construction(nfa):
    start, acc, delta = nfa
    s0 = frozenset({start})
    dfa, todo = {}, deque([s0])
    while todo:
        S = todo.popleft()
        if S in dfa:
            continue
        dfa[S] = {a: frozenset(set().union(*(delta.get((q, a), set()) for q in S))) for a in SIGMA}
        todo.extend(dfa[S].values())
    accepting = {S for S in dfa if S & acc}
    return s0, accepting, dfa


def dfa_accepts(dfa, word):
    S, acc, delta = dfa
    for a in word:
        S = delta[S][a]
    return S in acc


def minimal_size(dfa):
    """Moore's partition refinement: the number of states of the minimal DFA."""
    _, acc, delta = dfa
    block = {S: S in acc for S in delta}
    while True:
        sig = {S: (block[S],) + tuple(block[delta[S][a]] for a in SIGMA) for S in delta}
        ids = {v: i for i, v in enumerate(sorted(set(sig.values()), key=repr))}
        new = {S: ids[sig[S]] for S in delta}
        if len(set(new.values())) == len(set(block.values())):
            return len(set(new.values()))
        block = new


def name(S):
    return "{" + ",".join(f"p{q}" for q in sorted(S)) + "}"


W = ["".join(w) for k in range(13) for w in itertools.product(SIGMA, repeat=k)]

# --- The k = 1 case: the NFA for "ends with d" becomes END_D ------------------
# p0 loops on d and n; on a d it may also jump to p1, guessing "this d is the
# last letter". Tracking the SET of states some run could be in gives two sets,
# {p0} and {p0,p1}, and with their moves they are exactly END_D's q0 and q1.
N1 = kth_from_last(1)
D1 = subset_construction(N1)
assert all(nfa_accepts(N1, w) == bool(re.fullmatch(r"[dn]*d", w)) for w in W)
S0, S01 = frozenset({0}), frozenset({0, 1})
assert D1[2] == {S0: {"d": S01, "n": S0}, S01: {"d": S01, "n": S0}} and D1[1] == {S01}
cur, trace = {0}, ["{p0}"]
for a in "ndnd":
    cur = set().union(*(N1[2].get((q, a), set()) for q in cur)); trace.append(name(cur))
print("NFA for (d|n)* d on 'ndnd', the states some run could be in:", " -> ".join(trace))
print("  its subset construction has 2 states, {p0} and {p0,p1}: it is END_D\n")

# --- The k = 2 case: the slide ----------------------------------------------
N2 = kth_from_last(2)
D2 = subset_construction(N2)
assert all(nfa_accepts(N2, w) == bool(re.fullmatch(r"[dn]*d[dn]", w)) for w in W)
assert all(dfa_accepts(D2, w) == nfa_accepts(N2, w) for w in W)
print("NFA for (d|n)* d (d|n): 3 states; the subset construction gives a DFA with",
      len(D2[2]), "states:")
for S, out in D2[2].items():
    mark = "  accepting" if S in D2[1] else ""
    print(f"  {name(S):12} --d--> {name(out['d']):12} --n--> {name(out['n']):12}{mark}")
print("  NFA, DFA and regex agree on all", len(W), "words of length <= 12")

# --- The blowup: k + 1 NFA states, 2^k DFA states, and all of them needed ----
print("\n  k   NFA states   DFA states (subset)   minimal DFA")
for k in range(1, 9):
    D = subset_construction(kth_from_last(k))
    m = minimal_size(D)
    print(f"  {k}   {k + 1:10}   {len(D[2]):19}   {m:11}")
    assert len(D[2]) == 2 ** k and m == 2 ** k

print("\nok -- NFAs and DFAs accept the same languages; the price is up to 2^n states")
