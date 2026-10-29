"""Session 18 -- property-based testing, and the same specification in CBMC.

The specification of a sort, in two parts (it says WHAT, not which algorithm):
  sorted:      the output is nondecreasing;
  permutation: the output holds exactly the input's elements, duplicates included.

bad_sort is selection sort with one bug: it copies the minimum into place instead of
swapping it. Its output is always sorted, so a test that only checks order passes; it can
lose and duplicate elements, so the permutation property fails.

  1. Hypothesis (Python) generates random lists, runs both properties, and SHRINKS a
     failure to a minimal input: [0, -1] -> [-1, -1]. It samples: passing is not a proof.
  2. CBMC checks the same two properties as assertions (c/bad_sort.c) for EVERY array of 3
     ints: "sorted" SUCCESS, "permutation" FAILURE with a trace.
  3. As a Hoare triple / ACSL contract the same properties are a postcondition, which
     deductive verification proves for every length with loop invariants (slides 14-16).

Expected: the assertions at the bottom hold.
"""
from collections import Counter
from pathlib import Path

from hypothesis import find, given, settings, strategies as st

from cbmc_cli import run

C = Path(__file__).resolve().parent.parent / "c"


def bad_sort(xs):
    a = list(xs)
    for i in range(len(a)):
        m = min(range(i, len(a)), key=lambda j: a[j])
        a[i] = a[m]                       # BUG: should swap a[i] and a[m]
    return a


def is_sorted(ys):
    return all(p <= q for p, q in zip(ys, ys[1:]))


@settings(derandomize=True, database=None, max_examples=300)
@given(st.lists(st.integers()))
def test_sorted(xs):
    assert is_sorted(bad_sort(xs))


@settings(derandomize=True, database=None, max_examples=300)
@given(st.lists(st.integers()))
def test_permutation(xs):
    assert Counter(bad_sort(xs)) == Counter(xs)


test_sorted()                              # passes on 300 random lists
print("1. Hypothesis, 300 random lists each:")
print("     test_sorted       passed")
try:
    test_permutation()
    failed = False
except AssertionError:
    failed = True
print("     test_permutation  FAILED")
minimal = find(st.lists(st.integers()), lambda xs: Counter(bad_sort(xs)) != Counter(xs),
               settings=settings(derandomize=True, database=None))
print(f"     shrunk to the minimal input {minimal} -> {bad_sort(minimal)}")
assert failed
assert len(minimal) == 2 and minimal[1] < minimal[0]      # two elements, out of order: [0, -1] here
assert bad_sort(minimal) == [minimal[1], minimal[1]]      # the smaller one twice, the larger one lost

out = run("cbmc", C / "bad_sort.c", "--unwind", "4")
verdicts = [l.strip() for l in out.splitlines() if "sorted:" in l or "permutation:" in l]
print("\n2. $ cbmc bad_sort.c --unwind 4     (every array of 3 ints)")
for v in verdicts:
    print("     " + v.split("] ")[1])
assert any("sorted: SUCCESS" in v for v in verdicts)
assert any("permutation: FAILURE" in v for v in verdicts)

print("\n3. The same specification as a postcondition (Hoare triple / ACSL):")
print("     { true }  bad_sort(a, n)  { sorted(a) && permutation(a, old a) }")
print("     ensures sorted: \\forall integer i; 0 <= i < n-1 ==> a[i] <= a[i+1];")
print("     a proof would need loop invariants, and fails here, because the code is wrong.")
