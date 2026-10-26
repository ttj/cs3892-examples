#!/usr/bin/env python3
"""Check HW4: build each part, and say for every required theorem whether it is proved.

    python3 check_hw4.py            # the table; exits 0 unless Defs.lean or lean-toolchain was changed
    python3 check_hw4.py --strict   # exits 1 unless every theorem is proved: the acceptance test
    python3 check_hw4.py --json     # the same results, machine-readable

A theorem counts as PROVED only when all of these hold:
  * its part builds;
  * its statement is exactly the original one (compared after Lean elaborates it,
    with full names, so a renamed or shadowed definition is caught too);
  * `#print axioms` lists nothing beyond propext, Classical.choice and Quot.sound.
    `sorry` shows up there as sorryAx, `native_decide` as Lean.ofReduceBool, and an
    `axiom` you declare yourself by its name; each of those fails the theorem.
HW4/Defs.lean and lean-toolchain must be unchanged (checked by SHA-256).

Needs only Python 3.10+ and Lean. If `lake` is not found, this installs elan, the Lean
version manager, into ~/.elan (no root needed), and the first build downloads Lean
v4.33.0 (about 575 MB, once).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAN_VERSION = "4.33.0"
ELAN_INIT = "https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh"
PINNED = {
    "HW4/Defs.lean": "6186b0453b11b3f82218dd4de7aa902e8aed598ed33a04cffe6cdbf987c0dd17",
    "lean-toolchain": "302cd63c54178885b89e669f33b38f12f4dd7ae7e5cac537b3203e3768d8fb2b",
}
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}

# (module, theorem, points, statement as Lean prints it with pp.fullNames)
THEOREMS = [
    ("HW4.Part1Ladder", "HW4.Part1.rung1_compute", 2, "HW4.triple 4 = 12"),
    ("HW4.Part1Ladder", "HW4.Part1.rung2_arith", 2, "∀ (a b : Nat), a + 2 ≤ b → b < 7 → a < 5"),
    ("HW4.Part1Ladder", "HW4.Part1.rung3_and_intro", 2, "∀ (x : Nat), x = 4 → x + 1 = 5 ∧ 2 * x = 8"),
    ("HW4.Part1Ladder", "HW4.Part1.rung4_exists_elim", 2, "∀ (x : Nat), (∃ k, x = 2 * k ∧ k > 3) → x ≥ 8"),
    ("HW4.Part1Ladder", "HW4.Part1.rung5_imp", 2, "∀ (P Q R : Prop), (P → Q) → (Q → R) → P → R"),
    ("HW4.Part1Ladder", "HW4.Part1.rung6_induction", 2, "∀ (n : Nat), HW4.triple n = 3 * n"),
    ("HW4.Part1Ladder", "HW4.Part1.rung7_cases", 3, "∀ (l : HW4.Light), l.next.next.next = l"),
    ("HW4.Part2Sets", "HW4.Part2.subset_antisymm", 4,
     "∀ {α : Type} (A B : HW4.Set α), A ⊆ B → B ⊆ A → A = B"),
    ("HW4.Part2Sets", "HW4.Part2.demorgan_inter", 4, "∀ {α : Type} (A B : HW4.Set α), (A ∩ B)ᶜ = Aᶜ ∪ Bᶜ"),
    ("HW4.Part2Sets", "HW4.Part2.union_distrib_inter", 4,
     "∀ {α : Type} (A B C : HW4.Set α), A ∪ B ∩ C = (A ∪ B) ∩ (A ∪ C)"),
    ("HW4.Part2Sets", "HW4.Part2.diff_union", 4,
     "∀ {α : Type} (A B C : HW4.Set α), A \\ (B ∪ C) = A \\ B ∩ (A \\ C)"),
    ("HW4.Part2Sets", "HW4.Part2.subset_inter_iff", 4,
     "∀ {α : Type} (A B C : HW4.Set α), C ⊆ A ∩ B ↔ C ⊆ A ∧ C ⊆ B"),
    ("HW4.Part3Bucket", "HW4.Part3.P_not_inductive", 6, "¬HW4.InductiveInvariant HW4.bucket10 HW4.P"),
    ("HW4.Part3Bucket", "HW4.Part3.Q_not_inductive", 6, "¬HW4.InductiveInvariant HW4.bucket10 HW4.Q"),
    ("HW4.Part3Bucket", "HW4.Part3.inv_init", 4,
     "∀ (b : HW4.Bucket), HW4.bucket10.init b → HW4.Part3.Inv b"),
    ("HW4.Part3Bucket", "HW4.Part3.inv_step", 8,
     "∀ (b c : HW4.Bucket), HW4.Part3.Inv b → HW4.bucket10.step b c → HW4.Part3.Inv c"),
    ("HW4.Part3Bucket", "HW4.Part3.used_le_10", 6,
     "∀ (b : HW4.Bucket), HW4.Reachable HW4.bucket10 b → b.used ≤ 10"),
    ("HW4.Part4Parametric", "HW4.Part4.used_le_N", 10,
     "∀ (N : Nat) (b : HW4.Bucket), HW4.Reachable (HW4.bucket N) b → b.used ≤ N"),
    ("HW4.Part4Parametric", "HW4.Part4.reach_k", 6,
     "∀ (N k : Nat), k ≤ N → HW4.Reachable (HW4.bucket N) { used := k, left := N - k }"),
    ("HW4.Part4Parametric", "HW4.Part4.bound_tight", 2,
     "∀ (N : Nat), ∃ b, HW4.Reachable (HW4.bucket N) b ∧ b.used = N"),
]
PARTS = ["HW4.Part1Ladder", "HW4.Part2Sets", "HW4.Part3Bucket", "HW4.Part4Parametric"]
PART_TITLE = {"HW4.Part1Ladder": "Part 1 — tactic ladder",
              "HW4.Part2Sets": "Part 2 — sets",
              "HW4.Part3Bucket": "Part 3 — the token bucket",
              "HW4.Part4Parametric": "Part 4 — every capacity N"}


def say(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def find_lake() -> str:
    """lake from $LAKE, the PATH, or ~/.elan/bin; otherwise install elan (no root)."""
    for cand in (os.environ.get("LAKE"), shutil.which("lake"), str(Path.home() / ".elan/bin/lake")):
        if cand and Path(cand).exists():
            return cand
    say("lake not found: installing elan (the Lean version manager) into ~/.elan ...")
    with tempfile.TemporaryDirectory() as td:
        script = Path(td) / "elan-init.sh"
        with urllib.request.urlopen(ELAN_INIT, timeout=120) as r:
            script.write_bytes(r.read())
        subprocess.run(["sh", str(script), "-y", "--default-toolchain", "none", "--no-modify-path"],
                       check=True)
    lake = Path.home() / ".elan/bin/lake"
    if not lake.exists():
        raise SystemExit("elan installed, but ~/.elan/bin/lake is missing")
    return str(lake)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lake_run(lake: str, *args: str, capture: bool = True) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PATH"] = str(Path(lake).parent) + os.pathsep + env.get("PATH", "")
    return subprocess.run([lake, *args], cwd=HERE, env=env, text=True,
                          capture_output=capture, timeout=3600)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def check() -> dict:
    res = {"lean": LEAN_VERSION, "pinned": {}, "parts": {}, "theorems": []}
    for rel, want in PINNED.items():
        p = HERE / rel
        res["pinned"][rel] = p.exists() and sha256(p) == want
    if not all(res["pinned"].values()):
        return res

    lake = find_lake()
    # Let elan fetch the pinned toolchain with its progress visible (first run only).
    probe = lake_run(lake, "env", "lean", "--version", capture=True)
    if probe.returncode != 0 or LEAN_VERSION not in probe.stdout:
        say(f"fetching Lean v{LEAN_VERSION} (about 575 MB, once) ...")
        lake_run(lake, "env", "lean", "--version", capture=False)
        probe = lake_run(lake, "env", "lean", "--version", capture=True)
    res["lean_found"] = probe.stdout.strip()

    lake_run(lake, "build", "HW4.Defs")
    for part in PARTS:
        b = lake_run(lake, "build", part)
        out = b.stdout + b.stderr
        errors = [l for l in out.splitlines() if re.search(r"error:", l)]
        res["parts"][part] = {"built": b.returncode == 0, "errors": errors[:12]}

    checkdir = HERE / ".lake" / "hw4_check"
    checkdir.mkdir(parents=True, exist_ok=True)
    for part in PARTS:
        mine = [t for t in THEOREMS if t[0] == part]
        if not res["parts"][part]["built"]:
            for _, name, pts, _ in mine:
                res["theorems"].append(dict(name=name, part=part, points=pts,
                                            status="part does not build", detail=""))
            continue
        src = [f"import {part}", "set_option pp.fullNames true", "set_option format.width 100000"]
        for _, name, _, _ in mine:
            src += [f'#eval IO.println "@@ {name}"', f"#check @{name}", f"#print axioms {name}"]
        f = checkdir / f"{part.split('.')[-1]}.lean"
        f.write_text("\n".join(src) + "\n")
        r = lake_run(lake, "env", "lean", str(f))
        blocks = {}
        cur = None
        for line in (r.stdout + r.stderr).splitlines():
            m = re.match(r"@@ (\S+)$", line)
            if m:
                cur = m.group(1)
                blocks[cur] = []
            elif cur:
                blocks[cur].append(line)
        for _, name, pts, want in mine:
            lines = blocks.get(name, [])
            text = "\n".join(lines)
            typ = next((l.split(" : ", 1)[1] for l in lines
                        if re.match(rf"@?{re.escape(name)} : ", l)), None)
            ax = None
            m = re.search(rf"'{re.escape(name)}' depends on axioms: \[(.*?)\]", text)
            if m:
                ax = [a.strip() for a in m.group(1).split(",") if a.strip()]
            elif f"'{name}' does not depend on any axioms" in text:
                ax = []
            if typ is None or ax is None:
                status, detail = "missing", next((l for l in lines if "error" in l), "not found")
            elif norm(typ) != norm(want):
                status, detail = "statement changed", f"expected: {want}   found: {typ}"
            elif "sorryAx" in ax:
                status, detail = "uses sorry", ""
            elif set(ax) - ALLOWED_AXIOMS:
                status, detail = "disallowed axiom", ", ".join(sorted(set(ax) - ALLOWED_AXIOMS))
            else:
                status, detail = "proved", ", ".join(ax) or "no axioms"
            res["theorems"].append(dict(name=name, part=part, points=pts, status=status, detail=detail))
    return res


def report(res: dict) -> None:
    print(f"HW4 check — Lean v{LEAN_VERSION}   ({res.get('lean_found', '')})")
    for rel, ok in res["pinned"].items():
        print(f"  {rel:16} {'unchanged' if ok else 'CHANGED — restore it: git checkout -- ' + rel}")
    if not all(res["pinned"].values()):
        print("\nNot graded: a given file was changed.")
        return
    total = got = 0
    for part in PARTS:
        info = res["parts"][part]
        mine = [t for t in res["theorems"] if t["part"] == part]
        print(f"\n{PART_TITLE[part]} ({sum(t['points'] for t in mine)} points)"
              f"{'' if info['built'] else '   DOES NOT BUILD'}")
        for e in info["errors"][:6]:
            print(f"    {e}")
        for t in mine:
            total += t["points"]
            got += t["points"] if t["status"] == "proved" else 0
            short = t["name"].split(".")[-1]
            print(f"  {t['status']:20} {short:22} {t['points']:>2}   {t['detail']}")
    n_ok = sum(t["status"] == "proved" for t in res["theorems"])
    print(f"\nProved {n_ok} of {len(res['theorems'])} theorems: {got} of {total} points."
          "\nGraded by hand: Part 4's written question (2) and Part 5's AI log (15).")


def main() -> int:
    res = check()
    if "--json" in sys.argv:
        print(json.dumps(res, indent=1, ensure_ascii=False))
    else:
        report(res)
    if not all(res["pinned"].values()):
        return 2
    if "--strict" in sys.argv:
        return 0 if res["theorems"] and all(t["status"] == "proved" for t in res["theorems"]) else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
