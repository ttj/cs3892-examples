# FIGURE: figures/add2_mod16.svg   (session 9's add-2 counter, wrapping at 16 -- scripts/draw_models.py)
"""Session 17 -- what IC3's frames are, on a system small enough to print them.

The system is session 16's finite add-2 counter: x in 0..15, I: x = 0, T: x' = (x + 2) mod 16.
The property is P: x != 5. It is true (x stays even), but not inductive: 3 steps to 5.

A FRAME Fr_i is a set of states that contains every state reachable in at most i steps:
an over-approximation of "reachable within i". IC3 keeps a sequence of them:

    Fr_0 = I,    Fr_i ⊆ Fr_{i+1},    T(Fr_i) ⊆ Fr_{i+1},    Fr_1 .. Fr_k ⊆ P

(Fr_k is the newest frame; Fr_{k+1} starts as "everything" and must be cleaned of bad
states in the next round.)

It starts with a frame that excludes nothing, and shrinks frames by learning "x != s" for a
state s that it shows cannot be reached within i steps. It shows that by first excluding
s's predecessor one frame down, recursively. If that recursion reaches Fr_0 = I, it has
found a real counterexample. When two neighbouring frames are equal, Fr_i = Fr_{i+1},
that frame is closed under T: an inductive invariant that implies P.

This is IC3 with each "cube" a single state and no generalization. The real algorithm
learns clauses over many states at once (nuXmv, and Z3's Spacer in session 16's
08_ic3_spacer.py), but the frames mean the same thing.

Expected: the assertions at the bottom hold.
"""
STATES = range(16)
I = {0}
BAD = {5}                                   # the states where P fails


def post(x):
    return (x + 2) % 16


def pre(x):                                 # each state has exactly one predecessor here
    return (x - 2) % 16


def show(fr):
    out = sorted(set(STATES) - fr)
    return "everything" if not out else "all but {" + ", ".join(map(str, out)) + "}"


frames = [set(I), set(STATES)]              # Fr_0 = I, Fr_1 = everything
learned = []


def check(frames):
    assert frames[0] == I
    for i in range(len(frames) - 1):
        assert frames[i] <= frames[i + 1]                       # Fr_i ⊆ Fr_{i+1}
        assert {post(x) for x in frames[i]} <= frames[i + 1]    # T(Fr_i) ⊆ Fr_{i+1}


def block(s, i):
    """Exclude s from Fr_1..Fr_i, first excluding its predecessor from Fr_{i-1} if needed."""
    if s in frames[0]:
        return False                        # reached I: a real counterexample
    while pre(s) in frames[i - 1]:
        if not block(pre(s), i - 1):
            return False
    for j in range(1, i + 1):
        frames[j].discard(s)
    learned.append((i, s))
    return True


k, rounds, result = 1, [], None
while result is None:
    while frames[k] & BAD:                  # blocking: no bad state may stay in Fr_k
        assert block(min(frames[k] & BAD), k), "counterexample"
    assert all(not (frames[j] & BAD) for j in range(1, k + 1))   # Fr_1 .. Fr_k ⊆ P
    frames.append(set(STATES))              # a new frame on top, and push learned facts up
    for i in range(1, k + 1):
        for s in sorted(set(STATES) - frames[i]):
            if pre(s) not in frames[i]:     # s has no predecessor in Fr_i: x != s holds in Fr_{i+1}
                frames[i + 1].discard(s)
    check(frames)
    rounds.append([show(f) for f in frames[1:]])
    for i in range(1, k + 1):
        if frames[i] == frames[i + 1]:      # the first closed frame ends the search
            result = (i, frames[i])
            break
    k += 1

print("finite add-2, P: x != 5.  Fr_0 = {0} throughout.")
for r, fs in enumerate(rounds, 1):
    print(f"  round {r}: " + "   ".join(f"Fr_{i} = {f}" for i, f in enumerate(fs, 1)))
i, inv = result
print(f"\nFr_{i} = Fr_{i + 1} = {sorted(inv)}  -> an inductive invariant (x is even), and it implies P")
print(f"{len(learned)} facts learned; the first four, in order: "
      + ", ".join(f"x != {s} up to Fr_{j}" for j, s in learned[:4]) + ", ...")

# the result is what the slide says it is
assert inv == set(range(0, 16, 2))
assert I <= inv and {post(x) for x in inv} <= inv and not (inv & BAD)
assert learned[0] == (1, 5) and learned[1] == (1, 3)     # first: 5 is bad; then 3, its predecessor
print(f"rounds: {len(rounds)}, closed at frame {i}")
assert (len(rounds), i) == (8, 1), (len(rounds), i)
