"""A reduced ordered binary decision diagram (ROBDD) in about eighty lines.

Imported by the session 16 examples. It is the textbook construction (Bryant,
1986; Andersen's lecture notes), small enough to read in one sitting:

  * a node is (variable, low, high): "if the variable is 0 go low, else high";
  * the two leaves are FALSE (0) and TRUE (1);
  * `node` refuses to build a redundant test (low == high) and never builds the
    same node twice (the unique table). Those two rules are the REDUCTION, and
    they are why the same Boolean function always gets the same diagram.

Variables are numbered; a smaller number is tested nearer the root. Real
model checkers (NuSMV's CUDD) add complement edges, garbage collection and
dynamic reordering; none of that changes what a BDD is.
"""


class BDD:
    def __init__(self, nvars):
        self.nvars = nvars
        self.nodes = [(nvars, 0, 0), (nvars, 1, 1)]     # 0 = FALSE, 1 = TRUE
        self.unique = {}
        self.memo = {}

    def node(self, v, low, high):
        if low == high:                                 # rule 1: no redundant test
            return low
        key = (v, low, high)
        if key not in self.unique:                      # rule 2: share equal nodes
            self.unique[key] = len(self.nodes)
            self.nodes.append(key)
        return self.unique[key]

    def var(self, v):
        return self.node(v, 0, 1)

    def level(self, u):
        return self.nodes[u][0]

    def apply(self, op, u, w):
        """op is a function on two bits; the result is the diagram of op(u, w)."""
        key = (op, u, w)
        if key in self.memo:
            return self.memo[key]
        if u <= 1 and w <= 1:
            r = int(op(u, w))
        else:
            v = min(self.level(u), self.level(w))
            u0, u1 = (self.nodes[u][1], self.nodes[u][2]) if self.level(u) == v else (u, u)
            w0, w1 = (self.nodes[w][1], self.nodes[w][2]) if self.level(w) == v else (w, w)
            r = self.node(v, self.apply(op, u0, w0), self.apply(op, u1, w1))
        self.memo[key] = r
        return r

    def AND(self, u, w): return self.apply(lambda a, b: a & b, u, w)
    def OR(self, u, w):  return self.apply(lambda a, b: a | b, u, w)
    def XOR(self, u, w): return self.apply(lambda a, b: a ^ b, u, w)
    def NOT(self, u):    return self.apply(lambda a, b: 1 - a, u, 1)

    def exists(self, vs, u):
        """Existential quantification: forget the variables in vs."""
        vs = frozenset(vs)
        cache = {}
        def go(x):
            if x <= 1:
                return x
            if x not in cache:
                v, lo, hi = self.nodes[x]
                a, b = go(lo), go(hi)
                cache[x] = self.OR(a, b) if v in vs else self.node(v, a, b)
            return cache[x]
        return go(u)

    def rename(self, u, mapping):
        """Replace variable v by mapping[v]. The mapping must keep the order."""
        cache = {}
        def go(x):
            if x <= 1:
                return x
            if x not in cache:
                v, lo, hi = self.nodes[x]
                cache[x] = self.node(mapping.get(v, v), go(lo), go(hi))
            return cache[x]
        return go(u)

    def size(self, u):
        """Number of nodes reachable from u, the two leaves included when used."""
        seen, todo = set(), [u]
        while todo:
            x = todo.pop()
            if x not in seen:
                seen.add(x)
                if x > 1:
                    todo += [self.nodes[x][1], self.nodes[x][2]]
        return len(seen)

    def count(self, u, vs):
        """How many assignments to the variables vs make u true."""
        vs = sorted(vs)
        def go(x, i):
            if i == len(vs):
                return 1 if x == 1 else 0
            if x <= 1 or self.level(x) != vs[i]:
                return 2 * go(x, i + 1) if x != 0 else 0
            return go(self.nodes[x][1], i + 1) + go(self.nodes[x][2], i + 1)
        return go(u, 0)


def number(b, bits, n):
    """The diagram of 'the unsigned number on these bits (most significant first) equals n'."""
    r = 1
    for i, v in enumerate(bits):
        bit = (n >> (len(bits) - 1 - i)) & 1
        r = b.AND(r, b.var(v) if bit else b.NOT(b.var(v)))
    return r


def at_most(b, bits, n):
    """The diagram of 'the number on these bits is <= n', built as a union of points."""
    r = 0
    for m in range(n + 1):
        r = b.OR(r, number(b, bits, m))
    return r
