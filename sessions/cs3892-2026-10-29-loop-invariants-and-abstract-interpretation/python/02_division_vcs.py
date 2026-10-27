# FIGURE: figures/division.svg   (the division loop as a transition system, drawn -- scripts/draw_models.py)
"""Session 18 -- a loop invariant, and the three conditions it must meet.

    {Pre}   q := 0; r := x;  while (r >= y) { r := r - y; q := q + 1 }   {Post}
    Pre:  x >= 0  and  y > 0
    Post: x = q*y + r  and  0 <= r < y          (q and r are quotient and remainder)

An invariant Inv proves {Pre} loop {Post} when three implications are valid:
    1. established:  Pre, and the code before the loop, give Inv
    2. preserved:    Inv and the loop condition, then one iteration, give Inv again
    3. sufficient:   Inv and NOT the loop condition give Post
Each is a formula, so Z3 checks it: valid means "Not(formula)" is unsatisfiable.

The obvious invariant, r >= 0, passes 1 and 2 and fails 3. It is true, and too weak:
it says nothing linking q and r to x. x = q*y + r and r >= 0 passes all three.
Termination is a separate obligation: r decreases and stays >= 0 (a "variant").

Expected: the assertions at the bottom hold.
"""
from z3 import And, Implies, Ints, Not, Solver, sat, substitute

x, y, q, r = Ints("x y q r")
pre = And(x >= 0, y > 0)
post = And(x == q * y + r, 0 <= r, r < y)
guard = r >= y


def after_init(f):                       # q := 0; r := x
    return substitute(f, (q, x * 0), (r, x))


def after_body(f):                       # r := r - y; q := q + 1   (wp: substitute right to left)
    return substitute(substitute(f, (q, q + 1)), (r, r - y))


def check(name, f):
    s = Solver()
    s.add(Not(f))
    if s.check() == sat:
        m = s.model()
        return name, "FAILS", ", ".join("%s=%s" % (v, m.eval(v, model_completion=True)) for v in (x, y, q, r))
    return name, "holds", ""


def conditions(inv):
    return [check("1 established", Implies(pre, after_init(inv))),
            check("2 preserved  ", Implies(And(pre, inv, guard), after_body(inv))),
            check("3 sufficient ", Implies(And(pre, inv, Not(guard)), post))]


results = {}
for label, inv in (("r >= 0", r >= 0), ("x = q*y + r and r >= 0", And(x == q * y + r, r >= 0))):
    print("Inv:", label)
    results[label] = conditions(inv)
    for name, verdict, cex in results[label]:
        print("   %s  %-5s  %s" % (name, verdict, ("counterexample: " + cex) if cex else ""))
    print()

assert [v for _, v, _ in results["r >= 0"]] == ["holds", "holds", "FAILS"]
assert [v for _, v, _ in results["x = q*y + r and r >= 0"]] == ["holds", "holds", "holds"]

variant = check("variant: r decreases and stays >= 0",
                Implies(And(pre, x == q * y + r, r >= 0, guard), And(r - y < r, r - y >= 0)))
print("   %s: %s" % (variant[0], variant[1]))
assert variant[1] == "holds"
