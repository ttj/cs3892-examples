"""HW4 -- the starter builds, every required theorem is still a `sorry`, and the checker catches cheats.

Runs ../check_hw4.py (which fetches Lean v4.33.0 through elan if this machine has none):

  1. on the starter as shipped: Defs.lean and lean-toolchain unchanged, all four parts build,
     and every one of the 20 required theorems reports "uses sorry";
  2. on a scratch copy where rung 1 is closed with `native_decide` and rung 2 with a
     home-made `axiom`: both must be reported as "disallowed axiom", not "proved";
  3. on a scratch copy with an edited Defs.lean: the checker must refuse to grade (exit 2).

No solution is involved: this is what a student's copy looks like before any work.

Expected: the assertions at the bottom hold.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HW = Path(__file__).resolve().parent.parent


def check(folder, *flags):
    r = subprocess.run([sys.executable, str(folder / "check_hw4.py"), "--json", *flags],
                       capture_output=True, text=True, cwd=folder, timeout=3600)
    return r.returncode, json.loads(r.stdout)


code, res = check(HW)
assert code == 0 and all(res["pinned"].values()), res["pinned"]
assert all(p["built"] for p in res["parts"].values()), res["parts"]
statuses = {t["name"].split(".")[-1]: t["status"] for t in res["theorems"]}
print(f"starter: {len(statuses)} theorems, all parts build;", res.get("lean_found", "")[:40])
assert len(statuses) == 20 and set(statuses.values()) == {"uses sorry"}, statuses

with tempfile.TemporaryDirectory() as td:
    cheat = Path(td) / "hw4"
    shutil.copytree(HW, cheat, ignore=shutil.ignore_patterns("python"))
    p = cheat / "HW4" / "Part1Ladder.lean"
    s = p.read_text()
    s = s.replace("theorem rung1_compute : triple 4 = 12 := by\n  sorry",
                  "theorem rung1_compute : triple 4 = 12 := by\n  native_decide", 1)
    s = s.replace("theorem rung2_arith (a b : Nat) (h1 : a + 2 ≤ b) (h2 : b < 7) : a < 5 := by\n  sorry",
                  "axiom shortcut : ∀ a b : Nat, a + 2 ≤ b → b < 7 → a < 5\n"
                  "theorem rung2_arith (a b : Nat) (h1 : a + 2 ≤ b) (h2 : b < 7) : a < 5 :=\n"
                  "  shortcut a b h1 h2", 1)
    p.write_text(s)
    _, res = check(cheat)
    got = {t["name"].split(".")[-1]: t["status"] for t in res["theorems"]}
    print("native_decide ->", got["rung1_compute"], "| home-made axiom ->", got["rung2_arith"])
    assert got["rung1_compute"] == "disallowed axiom" and got["rung2_arith"] == "disallowed axiom", got

    d = cheat / "HW4" / "Defs.lean"
    d.write_text(d.read_text().replace("| idle   {b : Bucket} : BucketStep N b b",
                                       "| idle   {b : Bucket} : BucketStep N b b\n  | skip {b : Bucket} : BucketStep N b b"))
    code, res = check(cheat)
    print("edited Defs.lean -> exit", code, "| pinned:", res["pinned"])
    assert code == 2 and res["pinned"]["HW4/Defs.lean"] is False
