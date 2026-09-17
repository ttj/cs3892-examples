"""Slides 23-24 -- the board example, with every rule application checked.

    F = (NOT x OR y) AND (NOT y OR z) AND (NOT x OR NOT z) AND (x OR y)

The trace worked on the board:

    decide x        [x]
    Unit  on (NOT x OR y)      -> y      [x, y]
    Unit  on (NOT y OR z)      -> z      [x, y, z]
    Conflict on (NOT x OR NOT z)         BOTTOM
    backtrack
    decide NOT x    [NOT x]
    Unit  on (x OR y)          -> y      [NOT x, y]
    Unit  on (NOT y OR z)      -> z      [NOT x, y, z]
    all clauses satisfied                SAT

This script does not just confirm the answer. It replays the trace one rule at
a time and checks that each application was LEGAL:

  * a Unit step must name a clause with exactly one unassigned literal and all
    the others false under the current trail;
  * a Conflict step must name a clause with every literal false;
  * the final trail must satisfy every clause.

One thing worth saying out loud in class, because a sharp student will ask:
`F AND x` is itself unsatisfiable, so the two propagations on that branch are
VACUOUSLY entailed. That does not make the trace wrong -- unit propagation is a
syntactic rule on clauses, and those two steps are how the solver DISCOVERS the
branch is dead. The semantic fact is only the last one: F AND x entails BOTTOM.

Expected: every step legal, one model, and it is unique.
"""

from itertools import product

from z3 import Bool, Not, Or, Solver, sat, unsat

# ---------------------------------------------------------------- the formula
# A literal is (name, sign); sign True means the variable appears positive.
CLAUSES = [
    [("x", False), ("y", True)],    # NOT x OR y
    [("y", False), ("z", True)],    # NOT y OR z
    [("x", False), ("z", False)],   # NOT x OR NOT z
    [("x", True), ("y", True)],     # x OR y
]
NAMES = ["x", "y", "z"]


def show(cl):
    return " OR ".join(("" if s else "NOT ") + v for v, s in cl)


def lit_value(lit, trail):
    """True / False / None for one literal under a trail {var: bool}."""
    var, sign = lit
    if var not in trail:
        return None
    return trail[var] if sign else (not trail[var])


# ------------------------------------------------- replay, checking each step
def check_unit(clause, trail, expect_var, expect_val):
    """The Unit rule: all literals false but one, and that one is unassigned."""
    vals = [lit_value(l, trail) for l in clause]
    unassigned = [l for l, v in zip(clause, vals) if v is None]
    assert all(v is False for v in vals if v is not None), \
        f"Unit on ({show(clause)}) is illegal: a literal is already true"
    assert len(unassigned) == 1, \
        f"Unit on ({show(clause)}) is illegal: {len(unassigned)} literals unassigned, need 1"
    var, sign = unassigned[0]
    assert var == expect_var and sign == expect_val, \
        f"Unit on ({show(clause)}) forces {var}={sign}, not {expect_var}={expect_val}"
    return {**trail, var: sign}


def check_conflict(clause, trail):
    vals = [lit_value(l, trail) for l in clause]
    assert all(v is False for v in vals), \
        f"({show(clause)}) is not falsified by this trail: {vals}"


def satisfied(trail):
    return all(any(lit_value(l, trail) is True for l in cl) for cl in CLAUSES)


print(f"F = {' AND '.join('(' + show(c) + ')' for c in CLAUSES)}\n")

# --- branch one: decide x = true ------------------------------------------
t = {"x": True}
print("  Decide    x            trail [x]")
t = check_unit(CLAUSES[0], t, "y", True)
print(f"  Unit      ({show(CLAUSES[0])})  -> y       trail [x, y]")
t = check_unit(CLAUSES[1], t, "z", True)
print(f"  Unit      ({show(CLAUSES[1])})  -> z       trail [x, y, z]")
check_conflict(CLAUSES[2], t)
print(f"  Conflict  ({show(CLAUSES[2])})            BOTTOM\n")

# --- branch two: backtrack to x = false ------------------------------------
t2 = {"x": False}
print("  Backtrack NOT x        trail [NOT x]")
t2 = check_unit(CLAUSES[3], t2, "y", True)
print(f"  Unit      ({show(CLAUSES[3])})    -> y       trail [NOT x, y]")
t2 = check_unit(CLAUSES[1], t2, "z", True)
print(f"  Unit      ({show(CLAUSES[1])})  -> z       trail [NOT x, y, z]")
assert satisfied(t2), "the final trail does not satisfy every clause"
print("  all four clauses satisfied              SAT")
print(f"\n  model: x={t2['x']}, y={t2['y']}, z={t2['z']}")

# --- and the same facts, from the solver -----------------------------------
x, y, z = Bool("x"), Bool("y"), Bool("z")
Fz = [Or(Not(x), y), Or(Not(y), z), Or(Not(x), Not(z)), Or(x, y)]

s = Solver(); s.add(Fz); s.add(x)
assert s.check() == unsat, "the x-true branch should be unsatisfiable"
print("\n  z3: F AND x        -> unsat   (the branch really is dead)")

s = Solver(); s.add(Fz)
assert s.check() == sat
m = s.model()
got = (bool(m[x]), bool(m[y]), bool(m[z]))
assert got == (False, True, True), f"unexpected model {got}"
print("  z3: F              -> sat     x=False, y=True, z=True")

# Uniqueness, by brute force over all eight assignments.
def F_at(vx, vy, vz):
    return ((not vx or vy) and (not vy or vz) and (not vx or not vz) and (vx or vy))
models = [a for a in product([False, True], repeat=3) if F_at(*a)]
assert models == [(False, True, True)], f"expected one model, got {models}"
print(f"  brute force: {len(models)} model out of 8 — the trace found the only one")
