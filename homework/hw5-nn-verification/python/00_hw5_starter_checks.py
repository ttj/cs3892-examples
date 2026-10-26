"""HW5 -- the starter runs, every part is still a placeholder, and the tools behave.

Runs ../check_hw5.py and the library directly:

  1. on the starter as shipped: the shipped files are unchanged, the tools are the pinned
     versions, and every part reports "placeholder";
  2. the meaning check: a correct robustness property matches, and four typical mistakes do
     NOT -- the SAFE condition written instead of the counterexample, "and" for "or", the box
     not clipped to [0, 1], and the wrong eps;
  3. soundness, cross-checked: on a grid of queries CROWN never verifies one the MILP falsifies,
     every counterexample the MILP or PGD returns is confirmed by a forward pass, and CROWN's
     "unknown" is decided by the MILP at least once (complete vs incomplete, visibly);
  4. on a scratch copy with an edited hw5lib.py: the checker refuses to grade (exit 2).

No solution is involved: this is what a student's copy looks like before any work.

Expected: the assertions at the bottom hold.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HW = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW))
import hw5lib as lib  # noqa: E402


def check(folder, *flags):
    r = subprocess.run([sys.executable, str(folder / "check_hw5.py"), "--json", *flags],
                       capture_output=True, text=True, cwd=folder, timeout=1800)
    return r.returncode, json.loads(r.stdout)


code, res = check(HW)
assert code == 0 and all(res["pinned"].values()), res
bad = {k: v for k, v in res["versions"].items() if not v["ok"]}
assert not bad, f"tools differ from the pins: {bad}"
status = {k: v["status"] for k, v in res["parts"].items()}
print("starter:", status)
assert status == {"1": "placeholder", "2": "placeholder", "3": "placeholder", "4": "info",
                  "5": "placeholder"}, status

# 2. the meaning check
W = lib.load_net()
X, Y, _ = lib.load_images()


def vnn(lo, hi, out):
    t = [f"(declare-const X_{i} Real)" for i in range(196)] + [f"(declare-const Y_{j} Real)" for j in range(10)]
    t += [f"(assert (>= X_{i} {l:.17g}))\n(assert (<= X_{i} {h:.17g}))" for i, (l, h) in enumerate(zip(lo, hi))]
    return "\n".join(t + [out])


i, eps, y = 4, 0.03, int(Y[4])
lo, hi = np.clip(X[i] - eps, 0, 1), np.clip(X[i] + eps, 0, 1)
want = lib.Spec(lo, hi, [[(np.eye(10)[y] - np.eye(10)[j], 0.0)] for j in range(10) if j != y])
others = [j for j in range(10) if j != y]
right = vnn(lo, hi, "(assert (or " + " ".join(f"(and (>= Y_{j} Y_{y}))" for j in others) + "))")
mistakes = {
    "the safe condition": vnn(lo, hi, "(assert (and " + " ".join(f"(> Y_{y} Y_{j})" for j in others) + "))"),
    "and for or": vnn(lo, hi, "(assert (and " + " ".join(f"(>= Y_{j} Y_{y})" for j in others) + "))"),
    "no clipping": vnn(X[i] - eps, X[i] + eps, "(assert (or " + " ".join(f"(>= Y_{j} Y_{y})" for j in others) + "))"),
    "wrong eps": vnn(np.clip(X[i] - 0.02, 0, 1), np.clip(X[i] + 0.02, 0, 1),
                     "(assert (or " + " ".join(f"(>= Y_{j} Y_{y})" for j in others) + "))"),
}
assert lib.compare_specs(lib.parse_vnnlib(right), want) == []
for name, text in mistakes.items():
    d = lib.compare_specs(lib.parse_vnnlib(text), want)
    print(f"  {name:20} caught: {d[0][:90]}")
    assert d, name
try:
    lib.parse_vnnlib(right.replace("(declare-const X_7 Real)", ""))
    raise AssertionError("an undeclared X_7 was accepted")
except lib.VnnlibError as ex:
    print("  undeclared X_7      caught:", str(ex)[:60])

# Part 5's intended regions are stored only as sample bits; a wrong P5b ("or" where the property
# needs one conjunction) must still be reported, with a witness.
with np.load(HW / "data" / "part5_intended.npz") as z:
    p5b = z["P5b"]
lo3, hi3 = np.clip(X[3] - 0.05, 0, 1), np.clip(X[3] + 0.05, 0, 1)
wrong = lib.parse_vnnlib(vnn(lo3, hi3, "(assert (or " + " ".join(f"(>= Y_8 Y_{j})" for j in range(10) if j != 8) + "))"))
d = lib.compare_to_bits(wrong, lo3, hi3, p5b)
print("  P5b with or         caught:", d[0][:70] if d else None)
assert d and d[0].startswith("output region differs")

# 3. soundness, cross-checked
decided_unknown = 0
for i in (0, 4, 6, 9):
    for eps in (0.01, 0.02, 0.03):
        yy = int(Y[i])
        s = lib.Spec(np.clip(X[i] - eps, 0, 1), np.clip(X[i] + eps, 0, 1),
                     [[(np.eye(10)[yy] - np.eye(10)[j], 0.0)] for j in range(10) if j != yy])
        c, m, p = lib.lirpa_check(W, s, "CROWN"), lib.milp_check(W, s), lib.pgd_attack(W, s, steps=100, restarts=2)
        assert not (c.verdict == "verified" and m.verdict == "falsified"), (i, eps)
        assert not (m.verdict == "verified" and p.verdict == "falsified"), (i, eps)
        for r in (m, p):
            if r.verdict == "falsified":
                assert lib._confirm(W, s, r.x, tol=1e-6), (i, eps, r.detail)
        decided_unknown += c.verdict == "unknown" and m.verdict in ("verified", "falsified")
print(f"soundness: 12 queries consistent; CROWN 'unknown' decided by the MILP {decided_unknown} times")
assert decided_unknown >= 1

# 4. an edited library is refused
with tempfile.TemporaryDirectory() as td:
    copy = Path(td) / "hw5"
    shutil.copytree(HW, copy, ignore=shutil.ignore_patterns("python", "__pycache__"))
    p = copy / "hw5lib.py"
    p.write_text(p.read_text().replace("TOL = 1e-6", "TOL = 1.0"))
    code, res = check(copy)
    print("edited hw5lib.py -> exit", code)
    assert code == 2 and res["pinned"]["hw5lib.py"] is False
