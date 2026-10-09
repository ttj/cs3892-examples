# FIGURE: figures/vending_late.svg   (the state machines, drawn -- scripts/draw_models.py)
"""Session 14 -- three ways for two transition systems to be "the same".

A system here is a transition system with labelled states, T = (S, S0, ->, L):
what an observer sees of a run is its TRACE, the sequence of labels.

    trace equivalence    the two have the same set of traces
    simulation  A <= B   B can match every move of A, forever
    bisimulation A ~ B   each can match every move of the other, forever,
                         with ONE relation that works in both directions

    bisimilar  =>  simulate each other  =>  trace equivalent
    and neither arrow can be turned round. Two pairs of machines show it:

    1. LATE vs EARLY -- the vending machines of 01 and 02. Same traces;
       LATE simulates EARLY but not the other way; not bisimilar.
    2. FAIR vs JAMS  -- a machine that may jam after the coin. They SIMULATE
       EACH OTHER, and still are not bisimilar.

Expected: the assertions at the bottom hold. (NuSMV agrees on pair 1: the
notebook checks that LTL cannot tell LATE from EARLY and CTL can.)
"""
from collections import deque


class TS:
    def __init__(self, name, init, edges, label=None):
        self.name, self.init = name, set(init)
        self.succ = {}
        for s, t in edges:
            self.succ.setdefault(s, []).append(t)
            self.succ.setdefault(t, [])
        self.label = {s: (label or {}).get(s, s) for s in self.succ}   # default: its own name
        assert all(self.succ[s] for s in self.succ), "every state needs a successor"


# 1. The two vending machines. An observer sees `paid`, not which paid state.
LATE = TS("LATE", {"idle"}, [("idle", "paid"), ("paid", "coffee"), ("paid", "tea"),
                             ("coffee", "idle"), ("tea", "idle")])
EARLY = TS("EARLY", {"idle"}, [("idle", "paid_c"), ("idle", "paid_t"), ("paid_c", "coffee"),
                               ("paid_t", "tea"), ("coffee", "idle"), ("tea", "idle")],
           label={"paid_c": "paid", "paid_t": "paid"})

# 2. A machine that keeps you waiting (paid -> paid) and then serves, and one
#    that may also JAM: `stuck` looks like `paid` and can only wait.
FAIR = TS("FAIR", {"idle"}, [("idle", "paid"), ("paid", "paid"), ("paid", "coffee"), ("coffee", "idle")])
JAMS = TS("JAMS", {"idle"}, [("idle", "ok"), ("idle", "stuck"), ("ok", "ok"), ("ok", "coffee"),
                             ("stuck", "stuck"), ("coffee", "idle")],
          label={"ok": "paid", "stuck": "paid"})


def step(T, states, lab):
    """All states with label `lab` reachable in one move from `states`."""
    return frozenset(t for s in states for t in T.succ[s] if T.label[t] == lab)


def trace_difference(A, B):
    """Compare the trace sets by tracking, for each trace read so far, the SET of
    states each system could be in -- the subset construction of session 13.
    Returns None if the trace sets are equal, else a shortest trace only one has.
    (For finite systems where every state has a successor, equal finite traces
    means equal infinite traces.)"""
    labels = sorted(set(A.label.values()) | set(B.label.values()))
    first = {lab: (frozenset(s for s in A.init if A.label[s] == lab),
                   frozenset(s for s in B.init if B.label[s] == lab)) for lab in labels}
    todo = deque(([lab], sa, sb) for lab, (sa, sb) in first.items() if sa or sb)
    seen = set()
    while todo:
        trace, sa, sb = todo.popleft()
        if bool(sa) != bool(sb):
            return trace                                  # one system has this trace, the other does not
        if (sa, sb) in seen:
            continue
        seen.add((sa, sb))
        for lab in labels:
            ta, tb = step(A, sa, lab), step(B, sb, lab)
            if ta or tb:
                todo.append((trace + [lab], ta, tb))
    return None


def greatest_simulation(A, B):
    """The largest R such that (s, t) in R implies: same label, and every move
    s -> s' is matched by some t -> t' with (s', t') in R. Start from "same
    label" and delete pairs that fail, until nothing changes: a greatest fixpoint."""
    R = {(s, t) for s in A.succ for t in B.succ if A.label[s] == B.label[t]}
    changed = True
    while changed:
        changed = False
        for s, t in sorted(R):
            if not all(any((s2, t2) in R for t2 in B.succ[t]) for s2 in A.succ[s]):
                R.discard((s, t)); changed = True
    return R


def simulated_by(A, B):
    """A <= B: every initial state of A is simulated by some initial state of B."""
    R = greatest_simulation(A, B)
    return all(any((s, t) in R for t in B.init) for s in A.init)


def greatest_bisimulation(A, B):
    """As above, but a pair must survive in BOTH directions with the same R."""
    R = {(s, t) for s in A.succ for t in B.succ if A.label[s] == B.label[t]}
    changed = True
    while changed:
        changed = False
        for s, t in sorted(R):
            fwd = all(any((s2, t2) in R for t2 in B.succ[t]) for s2 in A.succ[s])
            back = all(any((s2, t2) in R for s2 in A.succ[s]) for t2 in B.succ[t])
            if not (fwd and back):
                R.discard((s, t)); changed = True
    return R


def bisimilar(A, B):
    R = greatest_bisimulation(A, B)
    return (all(any((s, t) in R for t in B.init) for s in A.init)
            and all(any((s, t) in R for s in A.init) for t in B.init))


def reachable(T):
    seen, todo = set(T.init), list(T.init)
    while todo:
        for t in T.succ[todo.pop()]:
            if t not in seen:
                seen.add(t); todo.append(t)
    return seen


def always_possible(T, at, nxt):
    """The CTL formula AG (at -> EX nxt), checked directly on the graph."""
    return all(any(T.label[t] == nxt for t in T.succ[s]) for s in reachable(T) if T.label[s] == at)


def report(A, B):
    diff = trace_difference(A, B)
    print(f"{A.name} vs {B.name}")
    print(f"  same traces:          {diff is None}" + ("" if diff is None else f"   (differ on {' '.join(diff)})"))
    print(f"  {A.name + ' <= ' + B.name + ':':22}{simulated_by(A, B)}")
    print(f"  {B.name + ' <= ' + A.name + ':':22}{simulated_by(B, A)}")
    print(f"  bisimilar:            {bisimilar(A, B)}")


report(EARLY, LATE)
R = greatest_simulation(EARLY, LATE)
print("  LATE simulates EARLY with  R =", ", ".join(f"({s},{t})" for s, t in sorted(R)))
print(f"  CTL  AG (paid -> EX coffee):   LATE {always_possible(LATE, 'paid', 'coffee')}, "
      f"EARLY {always_possible(EARLY, 'paid', 'coffee')}")

assert trace_difference(EARLY, LATE) is None            # trace equivalent
assert simulated_by(EARLY, LATE)                        # LATE can match EARLY...
assert not simulated_by(LATE, EARLY)                    # ...but EARLY cannot match LATE's `paid`
assert not bisimilar(EARLY, LATE)
assert always_possible(LATE, "paid", "coffee") and not always_possible(EARLY, "paid", "coffee")

print()
report(JAMS, FAIR)
print(f"  CTL  AG (paid -> EX coffee):   FAIR {always_possible(FAIR, 'paid', 'coffee')}, "
      f"JAMS {always_possible(JAMS, 'paid', 'coffee')}")

assert trace_difference(JAMS, FAIR) is None
assert simulated_by(JAMS, FAIR) and simulated_by(FAIR, JAMS)     # they simulate EACH OTHER
assert not bisimilar(JAMS, FAIR)                                  # ...and are still not bisimilar
assert ("stuck", "paid") in greatest_simulation(JAMS, FAIR)       # FAIR's paid can wait like stuck
assert ("stuck", "paid") not in greatest_bisimulation(JAMS, FAIR)  # but stuck cannot serve like paid
assert always_possible(FAIR, "paid", "coffee") and not always_possible(JAMS, "paid", "coffee")

# A system is bisimilar to itself, and the three notions are nested.
for T in (LATE, EARLY, FAIR, JAMS):
    assert bisimilar(T, T) and simulated_by(T, T) and trace_difference(T, T) is None

print("\nok -- bisimilar => simulate each other => same traces, and neither arrow reverses")
