"""Session 18 -- two abstract domains: what they can say, and what a join throws away.

An abstract value stands for a SET of concrete values. The sign domain has five:
bottom (no value), -, 0, +, top (any value). The interval domain has [lo, hi]. Every
operation must be SOUND: the abstract result contains every concrete result. It may
contain more -- that is the over-approximation, and it is where false alarms come from.

At a join (the point after an if/else) the domain must describe both branches with one
abstract value. Signs: + joined with - is top. Intervals: [1, 1] joined with [5, 5] is
[1, 5], which also contains 2, 3 and 4, values no run produces.

Expected: the assertions at the bottom hold.
"""
from absint import Analysis, Intervals, Signs, show

S, I = Signs(), Intervals()
vals = [S.NEG, S.ZERO, S.POS, S.TOP]
for op in ("*", "+"):
    print("signs, %s:" % op)
    print("        " + "".join("%-6s" % v for v in vals))
    for a in vals:
        print("   %-4s " % a + "".join("%-6s" % S.binop(op, a, b) for b in vals))
    print()
assert S.binop("*", S.NEG, S.NEG) == S.POS and S.binop("*", S.NEG, S.POS) == S.NEG
assert S.binop("+", S.POS, S.NEG) == S.TOP          # + plus - can be anything: precision lost
assert S.binop("+", S.POS, S.POS) == S.POS

print("intervals: [2, 3] + [-1, 4] =", show(I.binop("+", (2, 3), (-1, 4))),
      "   [2, 3] * [-1, 4] =", show(I.binop("*", (2, 3), (-1, 4))))
assert I.binop("+", (2, 3), (-1, 4)) == (1, 7) and I.binop("*", (2, 3), (-1, 4)) == (-3, 12)

# if (*) x := 1 else x := 5 -- then y := x - 3
prog = ("seq", ("if", ("nondet",), ("assign", "x", ("const", 1)), ("assign", "x", ("const", 5))),
        ("assign", "y", ("-", ("var", "x"), ("const", 3))))
concrete = sorted({x - 3 for x in (1, 5)})
for D in (S, I):
    env = Analysis(D).run(prog, {})
    print("\n%-9s after  if (*) x := 1 else x := 5;  y := x - 3:   x = %s   y = %s"
          % (D.name, show(env["x"]), show(env["y"])))
print("concrete   y is one of {%s}: the interval also admits -1, 0 and 1" % ", ".join(map(str, concrete)))
env_s, env_i = Analysis(S).run(prog, {}), Analysis(I).run(prog, {})
assert env_s["x"] == S.POS and env_s["y"] == S.TOP          # signs lost the sign of y
assert env_i["x"] == (1, 5) and env_i["y"] == (-2, 2)       # intervals: [-2, 2] -- sound, and includes 0
assert all(env_i["y"][0] <= v <= env_i["y"][1] for v in concrete)
