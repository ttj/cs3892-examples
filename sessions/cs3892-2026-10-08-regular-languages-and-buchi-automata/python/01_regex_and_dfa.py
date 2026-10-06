# FIGURE: figures/dfa_ends_d.svg   (the automata, drawn -- scripts/draw_models.py)
"""Session 13 -- regular expressions and finite automata, on the agent's logs.

Write down, at each step of session 11's agent, whether it deleted something:
d (a delete happened) or n (it did not). A finite log is then a WORD over the
alphabet {d, n}, and a property of logs is a LANGUAGE: a set of words.

    1. A regular expression and a DFA for "the log ends with a delete" agree
       on every word up to length 12 -- checked exhaustively, all 8191 of them.
    2. A DFA ACCEPTS a word when its run ENDS in an accepting state.
    3. Product = intersection. Complement = swap the accepting states.
       Emptiness = can an accepting state be reached? -- a graph search.
    4. Equivalence of two DFAs is emptiness of their symmetric difference,
       and the search hands back a word they disagree on.

Expected: the assertions at the bottom hold.
"""
import itertools
import re
from collections import deque

SIGMA = "dn"


class DFA:
    def __init__(self, start, accept, delta):
        self.start, self.accept, self.delta = start, set(accept), dict(delta)
        self.states = {self.start} | {q for q, _ in self.delta} | set(self.delta.values())

    def run(self, word):
        """The run: the sequence of states, one more than the letters read."""
        qs = [self.start]
        for a in word:
            qs.append(self.delta[(qs[-1], a)])
        return qs

    def accepts(self, word):
        return self.run(word)[-1] in self.accept


def words(maxlen):
    for k in range(maxlen + 1):
        for w in itertools.product(SIGMA, repeat=k):
            yield "".join(w)


def product(A, B, accept=lambda a, b: a and b):
    """Run A and B in lockstep. `accept` combines their verdicts (and = intersection)."""
    start = (A.start, B.start)
    delta, todo, seen = {}, deque([start]), {start}
    while todo:
        p, q = s = todo.popleft()
        for a in SIGMA:
            t = (A.delta[(p, a)], B.delta[(q, a)])
            delta[(s, a)] = t
            if t not in seen:
                seen.add(t); todo.append(t)
    acc = {s for s in seen if accept(s[0] in A.accept, s[1] in B.accept)}
    return DFA(start, acc, delta)


def complement(A):
    """For a COMPLETE deterministic automaton: swap accepting and non-accepting."""
    return DFA(A.start, A.states - A.accept, A.delta)


def shortest_accepted(A):
    """Emptiness check: breadth-first search for an accepting state. Returns the
    shortest accepted word, or None when the language is empty."""
    prev, todo = {A.start: None}, deque([A.start])
    while todo:
        q = todo.popleft()
        if q in A.accept:
            w = ""
            while prev[q] is not None:
                q, a = prev[q]
                w = a + w
            return w
        for a in SIGMA:
            t = A.delta[(q, a)]
            if t not in prev:
                prev[t] = (q, a); todo.append(t)
    return None


# "The log ends with a delete" -- q1 means: the last letter read was d.
END_D = DFA("q0", {"q1"}, {("q0", "n"): "q0", ("q0", "d"): "q1",
                           ("q1", "d"): "q1", ("q1", "n"): "q0"})
# "An even number of deletes" -- a parity bit.
EVEN_D = DFA("e", {"e"}, {("e", "n"): "e", ("e", "d"): "o",
                          ("o", "n"): "o", ("o", "d"): "e"})

# --- 1. Two runs, step by step (slide: "A DFA accepts if its run ends in F") --
for w in ("ndnd", "ndn"):
    print(f"run on {w!r:7}: {' -> '.join(END_D.run(w))}   "
          f"{'ACCEPT' if END_D.accepts(w) else 'reject'}")
assert END_D.accepts("ndnd") and not END_D.accepts("ndn")

# --- 2. Regular expressions, and the DFA, on every word up to length 12 --------
REGEX = {
    "[dn]*d":  "ends with a delete",
    "n*":      "never deletes (including the empty log)",
    "n*dn*":   "deletes exactly once",
    "(n*d)*":  "empty, or ends with a delete",
}
W = list(words(12))
print(f"\n{len(W)} words of length <= 12")
for rx, meaning in REGEX.items():
    k = sum(1 for w in W if re.fullmatch(rx, w))
    print(f"  {rx:8} {meaning:42} matches {k:5}")
assert all(END_D.accepts(w) == bool(re.fullmatch(r"[dn]*d", w)) for w in W)
print("the DFA END_D and the regex [dn]*d agree on all of them")

# --- 3. Product, complement, emptiness ------------------------------------------
P = product(END_D, EVEN_D)
assert all(P.accepts(w) == (END_D.accepts(w) and EVEN_D.accepts(w)) for w in W)
print(f"\nproduct END_D x EVEN_D: {len(P.states)} states, accepting {sorted(P.accept)}")
print(f"shortest word in the intersection: {shortest_accepted(P)!r}")
assert len(P.states) == 4 and shortest_accepted(P) == "dd"

C = complement(END_D)
assert all(C.accepts(w) != END_D.accepts(w) for w in W)
print(f"complement of END_D accepts the empty log: {C.accepts('')}, and 'dn': {C.accepts('dn')}")

NEVER = DFA("s", {"s"}, {("s", "n"): "s", ("s", "d"): "x", ("x", "n"): "x", ("x", "d"): "x"})
both = product(END_D, NEVER)            # ends with a delete AND never deletes
assert shortest_accepted(both) is None
print("ends-with-d AND never-deletes: the language is EMPTY (no accepting state is reachable)")

# --- 4. Equivalence = emptiness of the symmetric difference ---------------------
# (n*d)* looks like "ends with d" -- but it also matches the empty word.
STAR = DFA("s0", {"s0", "s1"}, {("s0", "n"): "s2", ("s0", "d"): "s1",
                                ("s1", "n"): "s2", ("s1", "d"): "s1",
                                ("s2", "n"): "s2", ("s2", "d"): "s1"})
assert all(STAR.accepts(w) == bool(re.fullmatch(r"(n*d)*", w)) for w in W)
diff = product(END_D, STAR, accept=lambda a, b: a != b)
witness = shortest_accepted(diff)
print(f"\nEND_D vs a DFA for (n*d)*: they differ on {witness!r} -- the empty word")
assert witness == ""

# A 3-state DFA for the same language as END_D (q2 is a redundant copy of q0).
END_D3 = DFA("q0", {"q1"}, {("q0", "n"): "q2", ("q0", "d"): "q1", ("q1", "d"): "q1",
                            ("q1", "n"): "q2", ("q2", "n"): "q0", ("q2", "d"): "q1"})
assert shortest_accepted(product(END_D, END_D3, accept=lambda a, b: a != b)) is None
print("END_D vs a 3-state DFA for the same language: symmetric difference EMPTY -> equal")

print("\nok -- regex, DFA, product, complement, emptiness, equivalence")
