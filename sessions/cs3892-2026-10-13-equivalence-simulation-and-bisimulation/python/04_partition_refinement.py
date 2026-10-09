# FIGURE: figures/ends_d3.svg   (the automata, drawn -- scripts/draw_models.py)
"""Session 14 -- computing bisimilarity: partition refinement.

Start by putting states with the same label in one BLOCK. A block is wrong if
two of its states disagree about which blocks they can move to; split it.
Repeat until nothing splits. The blocks left are the bisimulation classes --
the coarsest partition that is stable -- and merging each block into one state
gives the QUOTIENT, the smallest system bisimilar to the original.

This is the algorithm that minimized DFAs in session 13
(02_nfa_subset_construction.py, `minimal_size`): for a deterministic automaton,
bisimilar states are exactly the states that accept the same language.

    1. END_D3, a 3-state DFA for "ends with d", collapses to the 2-state END_D.
    2. The two vending machines: refinement pulls their initial states apart,
       which is the proof that they are NOT bisimilar.

Expected: the assertions at the bottom hold.
"""


def refine(states, label, moves, show=None):
    """states: iterable; label[s]: what is observed in s;
    moves[s]: set of (action, target) -- the action is "" for an unlabelled step.
    Returns the list of partitions, one per round, the last one stable."""
    block = {s: label[s] for s in states}                       # round 0: by label
    rounds = [block]
    while True:
        sig = {s: (block[s], frozenset((a, block[t]) for a, t in moves[s])) for s in states}
        names = {v: i for i, v in enumerate(sorted(set(sig.values()), key=repr))}
        new = {s: names[sig[s]] for s in states}
        if len(set(new.values())) == len(set(block.values())):  # nothing split: stable
            return rounds
        block = new
        rounds.append(block)


def blocks(part):
    out = {}
    for s, b in part.items():
        out.setdefault(b, []).append(s)
    return sorted(sorted(v) for v in out.values())


def show(title, rounds):
    print(title)
    for i, part in enumerate(rounds):
        print(f"  round {i}: " + "  ".join("{" + ", ".join(b) + "}" for b in blocks(part)))
    print(f"  stable after {len(rounds) - 1} split round(s): {len(blocks(rounds[-1]))} classes")


# --- 1. END_D3: q2 is a redundant copy of q0 -----------------------------------
D3 = {"q0": {("n", "q2"), ("d", "q1")}, "q1": {("d", "q1"), ("n", "q2")}, "q2": {("n", "q0"), ("d", "q1")}}
acc = {"q0": "reject", "q1": "ACCEPT", "q2": "reject"}
r1 = refine(D3, acc, D3)
show("END_D3 (3 states, accepts the words ending in d)", r1)
classes = blocks(r1[-1])
assert classes == [["q0", "q2"], ["q1"]]

# The quotient: one state per class; a move between classes if any member has it.
cls = {s: "".join(c) for c in classes for s in c}
quotient = sorted({(cls[s], a, cls[t]) for s in D3 for a, t in D3[s]})
print("  quotient:", ", ".join(f"{s} --{a}--> {t}" for s, a, t in quotient))
assert quotient == [("q0q2", "d", "q1"), ("q0q2", "n", "q0q2"), ("q1", "d", "q1"), ("q1", "n", "q0q2")]
print("  ...which is END_D: 3 states were 2 all along\n")

# --- 2. The vending machines, side by side in one system ------------------------
V = {"L.idle": {("", "L.paid")}, "L.paid": {("", "L.coffee"), ("", "L.tea")},
     "L.coffee": {("", "L.idle")}, "L.tea": {("", "L.idle")},
     "E.idle": {("", "E.paid_c"), ("", "E.paid_t")}, "E.paid_c": {("", "E.coffee")},
     "E.paid_t": {("", "E.tea")}, "E.coffee": {("", "E.idle")}, "E.tea": {("", "E.idle")}}
seen = {s: s.split(".")[1].split("_")[0] for s in V}             # paid_c and paid_t both show "paid"
r2 = refine(V, seen, V)
show("LATE (L.) and EARLY (E.) together", r2)
final = r2[-1]
assert final["L.idle"] != final["E.idle"]                       # the initial states end in different classes
assert len(blocks(r2[0])) == 4 and len(blocks(r2[1])) == 6      # round 1 splits the three `paid` states
part1 = blocks(r2[1])
assert ["E.paid_c"] in part1 and ["E.paid_t"] in part1 and ["L.paid"] in part1
print("  L.idle and E.idle end in different classes -> LATE and EARLY are NOT bisimilar")

print("\nok -- partition refinement: the coarsest stable partition is bisimilarity")
