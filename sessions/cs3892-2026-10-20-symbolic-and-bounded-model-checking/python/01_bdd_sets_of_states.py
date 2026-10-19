"""Session 16 -- a set of states is a Boolean function, and a BDD stores it.

The course's running counter has x in 0..25, so a state is five bits
x4 x3 x2 x1 x0 (most significant first). A SET of states is the Boolean
function that is true exactly on its members. The property "x <= 10" is such
a set: 11 of the 32 bit patterns.

A model checker does not list those 11 states. It stores the function as a
reduced ordered BDD (bdd.py), and asks questions of the diagram. This file
shows three things:

  1. the reduction: the full decision tree for "x <= 10" against the BDD;
  2. canonicity: two different formulas for the same set give the SAME node;
  3. variable order matters: "register a equals register b" is small when the
     bits of a and b are interleaved, and large when all of a comes first.

Expected: the assertions at the bottom hold.
"""

from bdd import BDD, at_most, number

X = [0, 1, 2, 3, 4]                      # x4 x3 x2 x1 x0, tested in this order
b = BDD(nvars=5)
P = at_most(b, X, 10)                    # the set { x : x <= 10 }

print("1. The set 'x <= 10' over five bits")
print("   states in the set      :", b.count(P, X), "of", 2 ** 5)
print("   full decision tree     :", 2 ** 6 - 1, "nodes (31 tests + 32 leaves)")
print("   reduced ordered BDD    :", b.size(P), "nodes (leaves included)")
assert b.count(P, X) == 11 and b.size(P) == 7

print("\n2. Canonical: the same set always gets the same diagram")
# x <= 10 written by hand: x4 = 0, and not (x3 = 1 and (x2 = 1 or (x1 = 1 and x0 = 1)))
x4, x3, x2, x1, x0 = (b.var(v) for v in X)
same = b.AND(b.NOT(x4), b.NOT(b.AND(x3, b.OR(x2, b.AND(x1, x0)))))
print("   x <= 10 written two ways ->", "the same node" if same == P else "different nodes")
assert same == P
print("   (so 'are these two sets equal?' costs one comparison of node numbers)")

print("\n3. Variable order: are two 4-bit registers a and b equal?")
def equal_registers(order):
    bb = BDD(nvars=8)
    pos = {name: i for i, name in enumerate(order)}
    r = 1
    for i in range(4):
        r = bb.AND(r, bb.NOT(bb.XOR(bb.var(pos["a%d" % i]), bb.var(pos["b%d" % i]))))
    return bb.size(r)
interleaved = equal_registers(["a0", "b0", "a1", "b1", "a2", "b2", "a3", "b3"])
separated = equal_registers(["a0", "a1", "a2", "a3", "b0", "b1", "b2", "b3"])
print("   order a0 b0 a1 b1 ...  :", interleaved, "nodes")
print("   order a0 a1 a2 a3 b0 ...:", separated, "nodes")
assert interleaved == 14 and separated == 47
print("   with n bits per register: 3n + 2 nodes interleaved, 3 * 2^n - 1 separated")
print("   (n = 20: 62 nodes against more than three million -- same function)")
