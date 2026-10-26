"""HW3 Part 2a -- the three loop-invariant conditions for array_max, checked by Z3.

c/array_max.c (from FMAIV), with n >= 1:

    m = a[0];  w = 0;  i = 1;                  w is a GHOST variable: the index m came from.
    while (i < n) {                            It is not in the C code; you may use it in
        if (a[i] > m) { m = a[i]; w = i; }     your invariant, or not.
        i = i + 1;
    }

    Post:  every a[k] with 0 <= k < n is <= m,  and  m equals some a[k] with 0 <= k < n.

An invariant Inv proves the loop when three implications are valid (session 18, slide 9):
    1 established: Pre, then the code before the loop, gives Inv
    2 preserved:   Inv and i < n, then one iteration, give Inv
    3 sufficient:  Inv and not (i < n) give Post
check(inv) prints, for each condition, whether Z3 finds it valid -- and if not, a
counterexample: values of the variables (and of the array) that make the condition false.

YOUR TASK: put your candidate invariants in CANDIDATES below. The one entry there now is a
placeholder to show the output, not a hint.

Runs as is (it exits 0 whatever your candidates do), so you can iterate.
"""
from z3 import (And, Array, Exists, ForAll, Implies, IntSort, Ints, IntVal, Not, Solver,
                If, sat, substitute, unknown)

a = Array("a", IntSort(), IntSort())
n, i, m, w, k = Ints("n i m w k")

pre = n >= 1
guard = i < n
post = And(ForAll(k, Implies(And(0 <= k, k < n), a[k] <= m)),
           Exists(k, And(0 <= k, k < n, a[k] == m)))


def after_init(f):                       # m = a[0]; w = 0; i = 1
    return substitute(f, (i, IntVal(1)), (m, a[0]), (w, IntVal(0)))


def after_body(f):                       # if (a[i] > m) { m = a[i]; w = i; }  i = i + 1;
    f = substitute(f, (i, i + 1))
    return If(a[i] > m, substitute(f, (m, a[i]), (w, i)), f)


def condition(f):
    s = Solver()
    s.set("timeout", 30000)
    s.add(Not(f))
    r = s.check()
    if r == sat:
        mod = s.model()
        vals = ", ".join("%s=%s" % (v, mod.eval(v, model_completion=True)) for v in (n, i, m, w))
        arr = ", ".join("a[%d]=%s" % (j, mod.eval(a[j], model_completion=True)) for j in range(4))
        return "FAILS   e.g. " + vals + "; " + arr
    return "holds" if r != unknown else "unknown (Z3 timed out)"


def check(name, inv):
    print("Inv:", name)
    print("   1 established ", condition(Implies(pre, after_init(inv))))
    print("   2 preserved   ", condition(Implies(And(pre, inv, guard), after_body(inv))))
    print("   3 sufficient  ", condition(Implies(And(pre, inv, Not(guard)), post)))
    print()


CANDIDATES = {
    "placeholder: 1 <= i (replace me)": 1 <= i,
}

if __name__ == "__main__":
    for name, inv in CANDIDATES.items():
        check(name, inv)
