# FIGURE: figures/agent_abstraction.svg   (the state machines, drawn -- scripts/draw_models.py)
"""Session 14 -- why simulation matters: an abstraction simulates what it abstracts.

The agent of sessions 11-13 has five states. Suppose all we care about is
whether a delete is happening. Map every state to what we observe of it,

    h(act) = del          h(plan) = h(ask) = h(abort) = h(done) = quiet

and give the abstract system an edge  h(s) -> h(t)  whenever the agent has an
edge  s -> t.  Two abstract states instead of five -- and by construction the
abstraction SIMULATES the agent: whatever the agent does, the abstraction can
follow. So every run of the agent is, seen through h, a run of the abstraction.

    * A property of ALL runs that holds on the abstraction holds on the agent.
    * A counterexample on the abstraction may be SPURIOUS -- no run of the
      agent matches it -- and then the abstraction has to be refined.

Expected: the assertions at the bottom hold. The two properties are also LTL
specs in 06_agent_abstract.smv and 07_agent_concrete.smv; the notebook checks
that NuSMV agrees.
"""

AGENT = {"plan": ["ask", "abort"], "ask": ["act", "abort"], "act": ["done"],
         "abort": ["done"], "done": ["plan"]}
INIT = "plan"


def abstract(h):
    """The existential abstraction of AGENT under the map h."""
    succ = {}
    for s, ts in AGENT.items():
        for t in ts:
            succ.setdefault(h[s], set()).add(h[t])
    return h[INIT], succ


def simulates(h, a_succ):
    """Is R = {(s, h(s))} a simulation of the agent by the abstraction?
    Same observation by construction; every agent move must have an abstract match."""
    return all(h[t] in a_succ[h[s]] for s, ts in AGENT.items() for t in ts)


def has_path(succ, start_states, word, obs):
    """Is there a path whose observations spell `word`, from one of start_states?"""
    cur = {s for s in start_states if obs(s) == word[0]}
    for w in word[1:]:
        cur = {t for s in cur for t in succ[s] if obs(t) == w}
    return bool(cur)


def del_then_del_within(k, succ, obs):
    """A violation of "after a delete, no delete for the next k steps":
    a path  del, (k-1 or fewer quiet steps), del.  Returns one if it exists."""
    for gap in range(k):
        word = ["del"] + ["quiet"] * gap + ["del"]
        if has_path(succ, list(succ), word, obs):
            return word
    return None


see = lambda s: "del" if s == "act" else "quiet"        # what we observe of an agent state

# --- The coarse abstraction: two states -------------------------------------------
h1 = {s: see(s) for s in AGENT}
a0, A1 = abstract(h1)
print("abstraction 1:", {s: sorted(t) for s, t in sorted(A1.items())}, " initial:", a0)
assert A1 == {"quiet": {"quiet", "del"}, "del": {"quiet"}}
assert simulates(h1, A1)
print("  it simulates the agent: every agent move has an abstract match")

# Property 1 -- "never two deletes in a row" -- holds on the abstraction, so on the agent.
assert del_then_del_within(1, A1, lambda s: s) is None
assert del_then_del_within(1, AGENT, see) is None
print("  G (del -> X !del):          holds on the abstraction  =>  holds on the agent")

# Property 2 -- "no delete in the two steps after a delete" -- FAILS on the abstraction...
cex = del_then_del_within(2, A1, lambda s: s)
assert cex == ["del", "quiet", "del"]
# ...but the agent has no such run: act -> done -> plan -> ask -> act takes three steps.
assert not has_path(AGENT, list(AGENT), cex, see)
assert del_then_del_within(2, AGENT, see) is None
print(f"  G (del -> X !del & X X !del): fails on the abstraction with {' '.join(cex)}")
print("                              -- SPURIOUS: the agent has no such run. Refine.")

# --- Refinement: tell `done` apart from the states before the decision ---------------
h2 = {"plan": "before", "ask": "before", "abort": "before", "done": "after", "act": "del"}
see2 = lambda a: "del" if a == "del" else "quiet"
b0, A2 = abstract(h2)
print("\nabstraction 2:", {s: sorted(t) for s, t in sorted(A2.items())}, " initial:", b0)
assert simulates(h2, A2)
assert del_then_del_within(2, A2, see2) is None
print("  three states; it still simulates the agent, and now property 2 holds on it")
print("  =>  G (del -> X !del & X X !del) holds on the agent")

print("\nok -- prove it on the abstraction; a failure there may be spurious")
