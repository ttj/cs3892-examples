"""Session 21 -- the Hennessy-Milner theorem, and trace equivalence vs bisimilarity, as Cslib states them.

theoryEq_eq_bisimilarity: in an image-finite LTS (finitely many successors per state and label),
two states satisfy the same HML formulas exactly when they are bisimilar. bisimilarity_neq_traceEq:
some LTS has trace-equivalent states that are not bisimilar -- Cslib's own witness is session 14's
pair of vending machines. #print axioms shows what the proof rests on: Lean's standard three.

Expected: the assertions at the bottom hold.
"""
from lean_cli import messages, show

F = "S21/Results.lean"
show(F, "hm")
rc, ms = messages(F)
assert rc == 0, ms
out = [t for _, t in ms]
hm = [t for t in out if t.startswith("@Logic.HML.theoryEq_eq_bisimilarity")][0]
tr = [t for t in out if t.startswith("LTS.Bisimilarity.bisimilarity_neq_traceEq")][0]
ax = [t for t in out if t.startswith("'Cslib.Logic.HML.theoryEq_eq_bisimilarity'")][0]
print("Lean says:\n  " + "\n  ".join([hm, tr, ax]).replace("\n", "\n  ") + "\n")
assert "[image_finite : ∀ (s : State) (μ : Label), Finite ↑(lts.image s μ)]" in hm
assert hm.endswith("Logic.HML.TheoryEq lts = lts.HomBisimilarity")
assert tr.endswith("∃ State Label lts, lts.HomBisimilarity ≠ lts.HomTraceEq")
assert ax.endswith("depends on axioms: [propext, Classical.choice, Quot.sound]")
print("same HML theory = bisimilar (image-finite); bisimilar is strictly finer than same traces")
