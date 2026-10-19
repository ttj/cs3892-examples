# FIGURE: figures/add2.svg   (session 9's add-2 counter, drawn -- scripts/draw_models.py)
"""Session 16 -- IC3 finds the strengthening for you: Z3's Spacer on the add-2 counter.

04_k_induction.py showed that over the integers, k-induction fails for EVERY k on
add-2 with P: x != 5. The counterexamples to induction run ..., 1, 3, 5 forever. In
session 9 you fixed it by hand, with "x is even".

IC3 (Bradley, VMCAI 2011) builds the strengthening itself. Each time a state that
satisfies the current frame can step to a bad state, IC3 asks whether that state can be
reached. If it can, that is a real counterexample. If not, IC3 learns a clause that
excludes the state and pushes the clause forward. It stops when a frame is inductive.

Spacer (Komuravelli, Gurfinkel & Chaki, CAV 2014) is the IC3/PDR-style engine built into
Z3. It takes the system as constrained Horn clauses, with Inv an unknown predicate:

    Inv(x)  <-  x = 0                      the initial state
    Inv(y)  <-  Inv(x)  and  y = x + 2     one step
    Bad     <-  Inv(x)  and  x = 5         the property fails

Is Bad derivable? "unsat" means no, so the system is safe. The answer comes with an
interpretation of Inv, and that interpretation is an inductive invariant that implies P.

The exact invariant can differ between Z3 versions. So this file checks what makes it
an answer: the initial state is in it, it is closed under a step, and it excludes x = 5.
It does not check which formula it is.

nuXmv's IC3 (`go_msat; check_invar_ic3`) proves the same property on 05_add2_finite.smv,
and on the integer version too. nuXmv is not run in CI (its licence), so Spacer is the
check here.

Expected: the assertions at the bottom hold.
"""
from z3 import (And, BoolSort, BoolVal, Fixedpoint, Function, Implies, Int, IntSort, IntVal, Not, Solver,
                is_quantifier, simplify, substitute, substitute_vars, unsat)


def ic3(step, init, bad):
    """Ask Spacer whether a bad state is reachable. Returns (verdict, Inv as a formula in x)."""
    fp = Fixedpoint()
    fp.set(engine="spacer")
    Inv = Function("Inv", IntSort(), BoolSort())
    Bad = Function("Bad", BoolSort())
    fp.register_relation(Inv, Bad)
    x, y = Int("x"), Int("y")
    fp.declare_var(x, y)
    fp.rule(Inv(x), init(x))
    fp.rule(Inv(y), [Inv(x), step(x, y)])
    fp.rule(Bad(), [Inv(x), bad(x)])
    verdict = fp.query(Bad())
    if verdict != unsat:
        return verdict, None
    answer = fp.get_answer()
    parts = answer.children() if not is_quantifier(answer) else [answer]
    q = next(p for p in parts if is_quantifier(p))            # ForAll A. Inv(A) == phi(A)
    return verdict, substitute_vars(q.body().arg(1), x)


def valid(f):
    s = Solver()
    s.add(Not(f))
    return s.check() == unsat


x, y = Int("x"), Int("y")
init = lambda v: v == 0
P = lambda v: v != 5

print("add-2 over the integers, P: x != 5   (k-induction fails here for every k)")
verdict, inv = ic3(lambda a, b: b == a + 2, init, lambda v: Not(P(v)))
print("   Spacer:", "SAFE -- x = 5 is unreachable" if verdict == unsat else verdict)
print("   the inductive invariant it built:", simplify(inv))


def is_answer(inv, step):
    """The three facts that make Inv a proof of P, each checked by Z3."""
    return {
        "contains the initial state     x = 0  ->  Inv(x)": valid(Implies(init(x), inv)),
        "closed under a step            Inv(x) and step(x, y)  ->  Inv(y)":
            valid(Implies(And(inv, step(x, y)), substitute(inv, (x, y)))),
        "implies the property           Inv(x)  ->  x != 5": valid(Implies(inv, P(x))),
    }


check = is_answer(inv, lambda a, b: b == a + 2)
for what, ok in check.items():
    print("   %-62s %s" % (what, "yes" if ok else "NO"))
odd_ok = [v for v in range(7, 20, 2) if simplify(substitute(inv, (x, IntVal(v)))).eq(BoolVal(True))]
if odd_ok:
    print("   It admits odd values such as x = %d: not session 9's 'x is even', and it need not be." % odd_ok[0])

assert verdict == unsat and all(check.values())

print("\nadd-2 on 0..15 with wrap-around (05_add2_finite.smv), P: x != 5")
wrap = lambda a, b: b == (a + 2) % 16
verdict16, inv16 = ic3(wrap, init, lambda v: Not(P(v)))
print("   Spacer:", "SAFE" if verdict16 == unsat else verdict16, "-- its invariant has",
      len(inv16.children()) if inv16 is not None else 0, "clauses")
assert verdict16 == unsat and all(is_answer(inv16, wrap).values())
