"""HW3 Part 3 -- run the sign and interval domains over four programs.

absint.py is the course's small abstract interpreter (the one from session 18). Programs
are written as small ASTs:

    ("assign", "x", e)     ("if", c, then, else)     ("while", c, body)     ("seq", ...)
    e: ("const", n) ("var", "x") ("+", e, e) ("-", e, e) ("*", e, e)
    c: ("<", e, e) (">=", e, e) ("!=", e, e) ("nondet",)       ("nondet",) is C's  *  (either way)

For each program this prints the abstract value of every variable at the end, in each
domain, and -- for the loop -- with and without widening. Compare those with what the
program actually computes. That comparison is the exercise; the numbers are just the tool's
output.

P5 is yours: a program on which the INTERVAL domain raises a false alarm because of a join.
Write it in the same AST form below (and in C, in c/part3_p5.c, for goto-analyzer and CBMC).

Runs as is (P5 starts empty), so you can iterate.
"""
from absint import Analysis, Intervals, Signs, show

TOP_SIGN, TOP_INT = Signs.TOP, (float("-inf"), float("inf"))
V, K = (lambda x: ("var", x)), (lambda n: ("const", n))

PROGRAMS = {
    "P1  x := -4; y := 3; z := x * y; w := z + y":
        (("seq", ("assign", "x", K(-4)), ("assign", "y", K(3)),
          ("assign", "z", ("*", V("x"), V("y"))), ("assign", "w", ("+", V("z"), V("y")))), {}),
    "P2  total := 0; i := 0; while (i < 10) { total := total + 2; i := i + 1 }":
        (("seq", ("assign", "total", K(0)), ("assign", "i", K(0)),
          ("while", ("<", V("i"), K(10)),
           ("seq", ("assign", "total", ("+", V("total"), K(2))), ("assign", "i", ("+", V("i"), K(1)))))), {}),
    "P3  if (*) { x := 2; y := 8 } else { x := 6; y := 4 };  s := x + y":
        (("seq", ("if", ("nondet",),
                  ("seq", ("assign", "x", K(2)), ("assign", "y", K(8))),
                  ("seq", ("assign", "x", K(6)), ("assign", "y", K(4)))),
          ("assign", "s", ("+", V("x"), V("y")))), {}),
    "P4  x is any integer (an input);  if (x < 0) y := 0 - x else y := x":
        (("if", ("<", V("x"), K(0)), ("assign", "y", ("-", K(0), V("x"))), ("assign", "y", V("x"))),
         {"x": "input"}),
    # "P5  ...": (YOUR PROGRAM HERE, {}),
}


def fmt(e):
    """An expression or condition, written as code."""
    if e[0] == "const":
        return str(e[1])
    if e[0] == "var":
        return e[1]
    return "%s %s %s" % (fmt(e[1]), e[0], fmt(e[2]))


def run(prog, inputs, domain, widen_after=None):
    env0 = {v: (TOP_SIGN if domain.name == "signs" else TOP_INT) for v in inputs}
    a = Analysis(domain, widen_after=widen_after)
    env = a.run(prog, env0)
    return env, a


if __name__ == "__main__":
    for title, (prog, inputs) in PROGRAMS.items():
        print(title)
        for D, wa in ((Signs(), None), (Intervals(), None), (Intervals(), 1)):
            env, a = run(prog, inputs, D, wa)
            label = D.name + (" + widening" if wa is not None else "")
            vals = "   ".join("%s = %s" % (v, show(env[v])) for v in sorted(env))
            rounds = "   (loop head: %d rounds)" % a.iterations if hasattr(a, "iterations") else ""
            print("   %-22s %s%s" % (label, vals, rounds))
            if a.alarms:
                cond, val = a.alarms[0]
                print("   %-22s ALARM: assert(%s) may fail -- %s is %s" % ("", fmt(cond), fmt(cond[1]), val))
        print()
