"""Session 19 -- insertion sort in Python, the code the slides translate into Lean (S19/Sort.lean).

`insertion_sort` is the textbook version: a loop, in place, shifting larger elements right.
`isort` / `insert` is the same algorithm read as functions on lists -- the shape Lean's
`S19.isort` / `S19.insert` has, one line for one line. The Lean proof is about the Lean
functions. Whether it says anything about these is the semantic-alignment question.
"""


def insertion_sort(a):
    """Sort the list `a` in place (CLRS 2.1): grow a sorted prefix a[0..i-1] one element at a time."""
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:     # shift every larger element one place right
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key


def insert(x, ys):
    """Lean:  | [] => [x]   | y :: ys => if x ≤ y then x :: y :: ys else y :: insert x ys"""
    if not ys:
        return [x]
    if x <= ys[0]:
        return [x] + ys
    return [ys[0]] + insert(x, ys[1:])


def isort(xs):
    """Lean:  | [] => []   | x :: xs => insert x (isort xs)"""
    if not xs:
        return []
    return insert(xs[0], isort(xs[1:]))
