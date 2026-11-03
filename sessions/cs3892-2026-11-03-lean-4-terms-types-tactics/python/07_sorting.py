"""Session 19 -- insertion sort: tested, then proved for every list; and how it lines up with Python.

1. Lean runs the tests (`#eval`, `#guard`) and checks `isort_correct`: for EVERY list of
   integers, the output is sorted and a permutation of the input. `#print axioms` shows the
   proof rests on no `sorry`.
2. The bug: `isortBad` passes its tests, and Lean checks the counterexample [1, 1].
3. Python (isort.py): the textbook in-place loop and the functional mirror of the Lean code.
   Hypothesis checks the same two properties on random lists -- many lists, not every list.
4. Alignment, measured: the Lean `isort` and the Python loop agree on 300 random lists
   (differential testing -- evidence, not proof). Then two places they do NOT line up:
   floats with NaN (Python's <= is not a total order; the Lean model has only Int), and
   recursion depth (the functional Python mirror dies on a 5000-element list; the loop does not).

Expected: the assertions at the bottom hold.
"""
import math
import random
import sys
from collections import Counter

from lean_cli import lean, messages, show, LEAN_DIR
from isort import insertion_sort, isort

F = "S19/Sort.lean"
for r in ["sort-def", "sort-tests", "sort-spec", "perm", "sorted", "correct", "bad", "ch-sort"]:
    show(F, r)
rc, out = lean(F)
print("Lean says:\n  " + out.replace("\n", "\n  ") + "\n")
assert rc == 0 and "error" not in out and "warning" not in out, out
assert out.split("\n") == ["[1, 2, 5, 5, 6, 9]", "[-7, -1, 0, 3]", "[]",
                           "'S19.isort_correct' depends on axioms: [propext, Quot.sound]",
                           "[1, 2, 3]"], out

# --- a failing #guard is an error: the tests really are checked ------------------------------
src = (LEAN_DIR / F).read_text()
rc, msgs = messages(F, src.replace("#guard isort [3, 1, 2] == [1, 2, 3]",
                                   "#guard isort [3, 1, 2] == [3, 2, 1]"))
assert rc != 0 and any(sev == "error" for sev, _ in msgs), msgs
print("a wrong #guard is an error, so the tests on the slide are checked\n")

# --- Python: the same two properties, on random lists ----------------------------------------
try:
    from hypothesis import given, settings, strategies as st
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "hypothesis"], check=True)
    from hypothesis import given, settings, strategies as st


def spec(inp, out):
    return all(a <= b for a, b in zip(out, out[1:])) and Counter(out) == Counter(inp)


@settings(max_examples=300, deadline=None)
@given(st.lists(st.integers(-10**30, 10**30)))
def test_loop(xs):
    a = list(xs)
    insertion_sort(a)
    assert spec(xs, a)


@settings(max_examples=300, deadline=None)
@given(st.lists(st.integers()))
def test_mirror(xs):
    assert spec(xs, isort(xs))


test_loop()
test_mirror()
print("Hypothesis: 300 random lists each, loop and mirror both sorted + permutation")

# --- Lean vs Python on the same inputs: differential testing ---------------------------------
rng = random.Random(3892)
cases = [[rng.randint(-50, 50) for _ in range(rng.randint(0, 12))] for _ in range(300)]
evals = "\n".join(f"#eval isort {c}" for c in cases)
rc, msgs = messages(F, src.replace("end S19", evals + "\nend S19"))
assert rc == 0, msgs
lean_out = [t for sev, t in msgs if sev == "information" and t.startswith("[")]
lean_out = lean_out[-len(cases):]
agree = 0
for c, lo in zip(cases, lean_out):
    a = list(c)
    insertion_sort(a)
    agree += (str(a) == lo)
print(f"Lean isort and the Python loop agree on {agree} of {len(cases)} random lists")
assert agree == len(cases)

# --- where the Lean model and Python part ways ------------------------------------------------
nan = float("nan")
a = [3.0, nan, 1.0]
insertion_sort(a)
print("Python, floats with NaN:", a, "-> sorted?", all(x <= y for x, y in zip(a, a[1:])))
assert a[0] == 3.0 and a[2] == 1.0 and math.isnan(a[1])     # not sorted, no error raised

big = list(range(5000, 0, -1))
try:
    isort(big)
    deep = "ok"
except RecursionError:
    deep = "RecursionError"
b = list(big)
insertion_sort(b)
print("Python, 5000 elements: functional mirror ->", deep, "| loop ->", "ok" if b == sorted(big) else "WRONG")
assert deep == "RecursionError" and b == sorted(big)

print("\nisort is correct for every Int list (Lean); Python agrees on the inputs tried, "
      "and differs on NaN and deep recursion")
