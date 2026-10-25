"""A small abstract interpreter, imported by 04-06: two abstract domains and a fixpoint.

Programs are tiny ASTs, not C, so that every step can be printed:

    ("assign", "x", e)       ("if", c, then, else)      ("while", c, body)
    ("seq", s1, s2, ...)     ("assert", c)

    expressions e:  ("const", n)  ("var", "x")  ("+", e, e)  ("-", e, e)  ("*", e, e)
    conditions  c:  ("<", e, e)  (">=", e, e)  ("!=", e, e)  ("nondet",)

A domain supplies: bottom, the abstraction of a constant, the arithmetic, join, and
(for intervals) widening and the refinement a branch condition allows. The interpreter
runs the program on abstract environments -- maps from variables to abstract values --
and at a loop head it iterates until the environment stops changing: the fixpoint of
session 16's reachability, computed over abstract values instead of sets of states.
"""
INF = float("inf")


# ------------------------------------------------------------------------------ signs
class Signs:
    """bottom < {neg, zero, pos} < top. Exact for *, coarse for + and -."""
    name = "signs"
    BOT, NEG, ZERO, POS, TOP = "bottom", "-", "0", "+", "top"

    def const(self, n):
        return self.NEG if n < 0 else self.ZERO if n == 0 else self.POS

    def join(self, a, b):
        if a == self.BOT:
            return b
        if b == self.BOT or a == b:
            return a
        return self.TOP

    def binop(self, op, a, b):
        if self.BOT in (a, b):
            return self.BOT
        if op == "*":
            if self.ZERO in (a, b):
                return self.ZERO
            if self.TOP in (a, b):
                return self.TOP
            return self.POS if a == b else self.NEG
        if op == "-":
            b = {self.NEG: self.POS, self.POS: self.NEG}.get(b, b)
        if a == self.ZERO:
            return b
        if b == self.ZERO:
            return a
        return a if a == b and a != self.TOP else self.TOP       # + plus - : could be anything

    widen = join

    def refine(self, cond, env):
        return env


# ------------------------------------------------------------------------------ intervals
class Intervals:
    """[lo, hi] with lo, hi possibly infinite; None is bottom (no value at all)."""
    name = "intervals"
    BOT = None

    def const(self, n):
        return (n, n)

    def join(self, a, b):
        if a is None:
            return b
        if b is None:
            return a
        return (min(a[0], b[0]), max(a[1], b[1]))

    def widen(self, old, new):
        """Any bound that moved jumps to infinity, so a chain of intervals must stop."""
        if old is None:
            return new
        if new is None:
            return old
        return (old[0] if new[0] >= old[0] else -INF, old[1] if new[1] <= old[1] else INF)

    def binop(self, op, a, b):
        if a is None or b is None:
            return None
        if op == "+":
            return (a[0] + b[0], a[1] + b[1])
        if op == "-":
            return (a[0] - b[1], a[1] - b[0])
        products = [x * y for x in a for y in b if not (x in (INF, -INF) and y == 0 or y in (INF, -INF) and x == 0)]
        return (min(products), max(products))

    def refine(self, cond, env):
        """Narrow a variable compared with a constant: x < c gives x <= c - 1, x >= c gives x >= c."""
        op, lhs, rhs = cond[0], cond[1:2], cond[2:3]
        if op not in ("<", ">=") or lhs[0][0] != "var" or rhs[0][0] != "const":
            return env
        x, c = lhs[0][1], rhs[0][1]
        lo, hi = env[x] if env.get(x) is not None else (INF, -INF)
        lo, hi = (lo, min(hi, c - 1)) if op == "<" else (max(lo, c), hi)
        new = dict(env)
        new[x] = (lo, hi) if lo <= hi else None
        return new if lo <= hi else None


NEGATE = {"<": ">=", ">=": "<", "!=": "==", "==": "!="}


def show(v):
    if isinstance(v, tuple):
        f = lambda b: "+inf" if b == INF else "-inf" if b == -INF else str(int(b))
        return "[%s, %s]" % (f(v[0]), f(v[1]))
    return "bottom" if v is None else str(v)


class Analysis:
    def __init__(self, domain, widen_after=None, trace=None, max_rounds=1000):
        self.D, self.widen_after, self.trace, self.max_rounds = domain, widen_after, trace, max_rounds
        self.converged = True
        self.alarms = []                      # (assertion, abstract value of the checked expression)

    def expr(self, e, env):
        if e[0] == "const":
            return self.D.const(e[1])
        if e[0] == "var":
            return env[e[1]]
        return self.D.binop(e[0], self.expr(e[1], env), self.expr(e[2], env))

    def join_env(self, a, b, op):
        if a is None:
            return b
        if b is None:
            return a
        return {k: op(a.get(k, self.D.BOT), b.get(k, self.D.BOT)) for k in set(a) | set(b)}

    def branch(self, cond, env, positive):
        if env is None or cond[0] == "nondet":
            return env
        c = cond if positive else (NEGATE[cond[0]],) + cond[1:]
        return self.D.refine(c, env)

    def run(self, s, env):
        if env is None:
            return None
        kind = s[0]
        if kind == "seq":
            for t in s[1:]:
                env = self.run(t, env)
            return env
        if kind == "assign":
            new = dict(env)
            new[s[1]] = self.expr(s[2], env)
            return new
        if kind == "if":
            return self.join_env(self.run(s[2], self.branch(s[1], env, True)),
                                 self.run(s[3], self.branch(s[1], env, False)), self.D.join)
        if kind == "while":
            head, k = env, 0
            while True:
                k += 1
                if self.trace is not None:
                    self.trace.append({v: show(x) for v, x in head.items()})
                body = self.run(s[2], self.branch(s[1], head, True))
                op = self.D.widen if self.widen_after is not None and k > self.widen_after else self.D.join
                nxt = self.join_env(head, self.join_env(env, body, self.D.join), op)
                if nxt == head:
                    break
                if k >= self.max_rounds:              # e.g. plain join on a loop with no bound
                    self.converged = False
                    print("   (no fixpoint after %d rounds: stopping; try widening)" % k)
                    break
                head = nxt
            self.iterations = k
            return self.branch(s[1], head, False)
        if kind == "assert":
            op, a, b = s[1]
            diff = self.expr(("-", a, b), env)
            safe = diff is not None and (diff[0] > 0 or diff[1] < 0) if op == "!=" else True
            if not safe:
                self.alarms.append((s[1], show(diff)))
            return env
        raise ValueError(kind)
