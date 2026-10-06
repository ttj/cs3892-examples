# FIGURE: figures/agent.svg   (the state machine, drawn -- scripts/draw_models.py)
"""Session 12 -- LTL model checking the automata way, small enough to read.

The recipe the model checker follows for an LTL property phi:

    1. build a Buchi automaton A for NOT phi -- it accepts exactly the bad runs
    2. form the product of the system M with A -- runs of M that A accepts
    3. search the product for a reachable ACCEPTING CYCLE
         found     -> a lasso: a run of M violating phi (the counterexample)
         not found -> L(M) and L(A) do not meet, so M satisfies phi

A Buchi automaton accepts an infinite word if some run of it visits an
accepting state INFINITELY OFTEN. In a finite product that means: reach an
accepting state that lies on a cycle.

The system is the agent of 01_ctl_on_the_agent.smv (and session 11), written
out as an explicit graph. The two automata are drawn on the slides.

Expected: the assertions at the bottom hold, and agree with NuSMV (the notebook
runs both).
"""
from collections import deque


def agent(shortcut=False):
    """States (step, approved). The buggy agent can go plan -> act directly."""
    succ = {}
    for step in ("plan", "ask", "act", "abort", "done"):
        for appr in (False, True):
            nxt = {"plan": [("ask", False), ("abort", False)] + ([("act", False)] if shortcut else []),
                   "ask": [("act", True), ("abort", False)],
                   "act": [("done", False)],
                   "abort": [("done", False)],
                   "done": [("plan", False)]}[step]
            succ[(step, appr)] = nxt
    return ("plan", False), succ


def label(s):
    step, appr = s
    return {"del": step == "act", "approved": appr}


# Buchi automata for the NEGATIONS, as (initial, accepting, delta).
# delta(q, L) -> the set of states the automaton may move to on reading L.
NOT_GF_DEL = ("q0", {"q1"},                    # not G F del  ==  F G !del
              lambda q, L: ({"q0", "q1"} if not L["del"] else {"q0"}) if q == "q0"
              else ({"q1"} if not L["del"] else set()))   # q1: !del forever; guessing WHEN is nondeterminism
NOT_SAFE = ("q0", {"q1"},                      # not G (del -> approved)  ==  F (del & !approved)
            lambda q, L: ({"q0", "q1"} if (L["del"] and not L["approved"]) else {"q0"}) if q == "q0"
            else {"q1"})                       # q1: a bad delete has happened; anything after


def product(system, automaton):
    s0, succ = system
    qi, acc, delta = automaton
    init = [(s0, q) for q in delta(qi, label(s0))]
    edges, seen, todo = {}, set(init), deque(init)
    while todo:
        s, q = node = todo.popleft()
        edges[node] = [(t, r) for t in succ[s] for r in delta(q, label(t))]
        for n in edges[node]:
            if n not in seen:
                seen.add(n); todo.append(n)
    return init, edges, acc


def path(edges, starts, goal_test):
    """BFS from `starts` to the first node satisfying goal_test; returns the path."""
    prev = {}
    todo = deque()
    for st in starts:
        if st not in prev:
            prev[st] = None; todo.append(st)
    while todo:
        n = todo.popleft()
        if goal_test(n):
            out = [n]
            while prev[out[-1]] is not None:
                out.append(prev[out[-1]])
            return out[::-1]
        for m in edges[n]:
            if m not in prev:
                prev[m] = n; todo.append(m)
    return None


def accepting_lasso(system, automaton):
    """Return (prefix, cycle) through an accepting product state, or None if empty."""
    init, edges, acc = product(system, automaton)
    for a in [n for n in edges if n[1] in acc]:
        back = path(edges, edges[a], lambda n: n == a)  # can a reach itself again?
        if back:
            pre = path(edges, init, lambda n: n == a)
            return pre, [a] + back, len(edges)
    return None, None, len(edges)


def show(name, res):
    pre, cyc, size = res
    if pre is None:
        print(f"{name}: product has {size} states, NO accepting cycle -> the property HOLDS")
        return
    fmt = lambda ns: " -> ".join(f"{s[0]}{'*' if s[1] else ''}/{q}" for s, q in ns)
    print(f"{name}: product has {size} states, accepting cycle FOUND -> the property FAILS")
    print(f"   prefix: {fmt(pre)}")
    print(f"   cycle:  {fmt(cyc)}   (* = approved)")


fixed, buggy = agent(), agent(shortcut=True)

r1 = accepting_lasso(fixed, NOT_GF_DEL)
show("fixed agent,  G F del", r1)
r2 = accepting_lasso(fixed, NOT_SAFE)
show("fixed agent,  G (del -> approved)", r2)
r3 = accepting_lasso(buggy, NOT_SAFE)
show("buggy agent,  G (del -> approved)", r3)

# G F del fails on the fixed agent: the lasso loops through plan/abort/done, never act.
assert r1[0] is not None and all(s[0] != "act" for s, _ in r1[1])
# The safety property holds on the fixed agent: no accepting cycle at all.
assert r2[0] is None
# ...and fails on the buggy one, through an unapproved delete in the prefix.
assert r3[0] is not None and any(s == ("act", False) for s, _ in r3[0])
print("\nok -- the same verdicts NuSMV gives (the notebook checks both)")
