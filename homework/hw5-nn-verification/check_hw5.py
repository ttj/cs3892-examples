"""HW5 checker: does each part run, and does it say what it should?

    python3 check_hw5.py            # a table, one row per part; exit 0 unless the setup is broken
    python3 check_hw5.py --strict   # the acceptance test: exit 0 only when every part is OK
    python3 check_hw5.py --json     # the same, machine-readable (CI uses it)

What is checked:
  setup   hw5lib.py, the network and the images are the shipped ones (SHA-256), and the tools
          are the pinned versions (a different version is reported, not refused)
  Part 1  make_vnnlib parses, and MEANS the robustness property, on five (image, eps) queries
          (the box pixel by pixel, the unsafe output region as a set)
  Part 2  binary_search brackets the threshold of several monotone predicates within tol
  Part 3  FINDING is a grid query where CROWN says "unknown" and the MILP decides
  Part 4  nothing to check: run part4_bounds.py and answer in your report
  Part 5  all six .vnnlib files are there; the _fixed ones parse and mean the intended property
          (the _llm ones are reported, right or wrong: finding what is wrong is the exercise)

Exit codes: 0 ok (or, without --strict, any state of the parts), 1 --strict and something is
not OK, 2 the shipped files were changed (the checker refuses to grade).
"""
from __future__ import annotations

import hashlib
import importlib
import json
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

PINNED = {
    "hw5lib.py": "5270e2f278b89d65592373b6a52daff35bb9ffbbedc77f51f153f86034db4b50",
    "net/mnist14_mlp.npz": "92e903b805cb27baea5a4103a016d518b30a9ca5e41e24b18ab2c99213d95c5f",
    "data/mnist14_test.npz": "28172b2ab577ec53d5379474ffe9dc406ef09288cb7fef7d858e3540b2a9a440",
    "data/part5_intended.npz": "e6c282f24e2cb68b1a79fbba130fa2a391545492e814dc92b0e85ee9c66535ac",
}
VERSIONS = {"torch": "2.11.0", "auto_LiRPA": "0.8.0", "highspy": "1.15.1", "numpy": "2.2.6"}
PART1_QUERIES = [(4, 0.02), (4, 0.03), (4, 0.05), (0, 0.01), (7, 0.004)]
# Part 5: (image, eps) of each property. The intended OUTPUT regions are not printed here (they
# are the answer to Part 5.2): data/part5_intended.npz holds only which points of a fixed sample
# (hw5lib.output_samples) each region contains, enough to say "matches" or to give a witness.
P5 = {"P5a": (2, 0.02), "P5b": (3, 0.05), "P5c": (1, 0.01)}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def box(lib, x0, eps):
    import numpy as np
    return np.clip(x0 - eps, 0, 1), np.clip(x0 + eps, 0, 1)


def intended(lib, kind, i, eps, extra=None):
    """Part 1's robustness property, as the Spec it should parse to: the standard VNN-COMP form,
    taught in session 25 and shown in the handout. (Reading it is allowed; writing the VNN-LIB
    that means it, and saying why it is the counterexample, is the exercise.)"""
    import numpy as np
    assert kind == "robust"
    X, Y, _ = lib.load_images()
    lo, hi = box(lib, X[i], eps)
    y = int(Y[i])
    e = np.eye(lib.N_OUT)
    return lib.Spec(lo, hi, [[(e[y] - e[j], 0.0)] for j in range(lib.N_OUT) if j != y])


def check_part1(lib):
    mod = importlib.import_module("part1_query")
    X, Y, _ = lib.load_images()
    for i, eps in PART1_QUERIES:
        text = mod.make_vnnlib(X[i], int(Y[i]), eps)
        if text is None:
            return "placeholder", "make_vnnlib returns None"
        if not isinstance(text, str):
            return "wrong", f"make_vnnlib must return a str, got {type(text).__name__}"
        try:
            got = lib.parse_vnnlib(text)
        except lib.VnnlibError as ex:
            return "wrong", f"image {i}, eps {eps}: syntax: {ex}"
        diffs = lib.compare_specs(got, intended(lib, "robust", i, eps))
        if diffs:
            return "wrong", f"image {i}, eps {eps}: " + "; ".join(diffs)
    return "ok", f"{len(PART1_QUERIES)} queries parse and mean the robustness property"


def check_part2(lib):
    mod = importlib.import_module("part2_frontier")
    if mod.binary_search(lambda e: e < 0.5, 0.0, 1.0, 0.1) is None:
        return "placeholder", "binary_search returns None"
    for thr, lo, hi, tol in ((0.0371, 0.0, 0.08, 0.001), (0.5, 0.0, 1.0, 1e-4), (0.0791, 0.0, 0.08, 0.001),
                             (0.0004, 0.0, 0.08, 0.001)):
        calls = []

        def pred(e, thr=thr):
            calls.append(e)
            return e <= thr
        out = mod.binary_search(pred, lo, hi, tol)
        try:
            a, b = out
        except (TypeError, ValueError):
            return "wrong", f"binary_search must return a pair (a, b), got {out!r}"
        if not (pred(a) and not pred(b) and 0 <= b - a <= tol + 1e-12 and lo <= a <= b <= hi):
            return "wrong", f"threshold {thr} on [{lo}, {hi}], tol {tol}: got ({a}, {b})"
        if len(calls) > 2 * 64:
            return "wrong", f"binary_search called pred {len(calls)} times for tol {tol}"
    return "ok", "brackets the threshold of four monotone predicates"


def check_part3(lib):
    mod = importlib.import_module("part3_compare")
    if mod.FINDING is None:
        return "placeholder", "FINDING is None"
    try:
        i, eps = mod.FINDING
    except (TypeError, ValueError):
        return "wrong", f"FINDING must be (image, eps), got {mod.FINDING!r}"
    if i not in mod.IMAGES or eps not in mod.EPS:
        return "wrong", f"FINDING {mod.FINDING} is not a query of the grid"
    W = lib.load_net()
    spec = intended(lib, "robust", i, eps)
    c, m = lib.lirpa_check(W, spec, "CROWN"), lib.milp_check(W, spec)
    if c.verdict != "unknown" or m.verdict not in ("verified", "falsified"):
        return "wrong", f"FINDING {mod.FINDING}: CROWN {c.verdict}, MILP {m.verdict}"
    return "ok", f"FINDING {mod.FINDING}: CROWN unknown, MILP {m.verdict}"


def check_part5(lib):
    import numpy as np
    notes, status = [], "ok"
    X, _, _ = lib.load_images()
    with np.load(HERE / "data" / "part5_intended.npz") as z:
        bits = {k: z[k] for k in z.files}
    for name, (i, eps) in P5.items():
        lo, hi = box(lib, X[i], eps)
        for which in ("llm", "fixed"):
            p = HERE / "part5" / f"{name}_{which}.vnnlib"
            if not p.exists():
                return "wrong", f"{p.name} is missing"
            text = p.read_text()
            if "PLACEHOLDER" in text:
                return "placeholder", f"{p.name} is still the placeholder"
            try:
                got = lib.parse_vnnlib(text)
                diffs = lib.compare_to_bits(got, lo, hi, bits[name])
                verdict = "matches the property" if not diffs else "MEANS SOMETHING ELSE: " + "; ".join(diffs)
            except lib.VnnlibError as ex:
                verdict, diffs = f"SYNTAX ERROR: {ex}", ["syntax"]
            notes.append(f"{p.name}: {verdict}")
            if which == "fixed" and diffs:
                status = "wrong"
    return status, "\n      ".join(notes)


def main(argv) -> int:
    strict, as_json = "--strict" in argv, "--json" in argv
    res = {"pinned": {}, "versions": {}, "parts": {}}
    for rel, want in PINNED.items():
        p = HERE / rel
        res["pinned"][rel] = p.exists() and sha256(p) == want
    try:
        import importlib.metadata as md
        for pkg, want in VERSIONS.items():
            try:
                got = md.version(pkg if pkg != "auto_LiRPA" else "auto-lirpa")
            except md.PackageNotFoundError:
                got = None
            res["versions"][pkg] = {"want": want, "got": got, "ok": bool(got) and got.split("+")[0] == want}
    except Exception:                                        # pragma: no cover
        pass
    missing = [k for k, v in res["versions"].items() if not v["got"]]
    if not all(res["pinned"].values()) or missing:
        why = ("changed: " + ", ".join(k for k, v in res["pinned"].items() if not v)) if not all(
            res["pinned"].values()) else "not installed: " + ", ".join(missing) + " (see README: pip install)"
        res["error"] = why
        if as_json:
            print(json.dumps(res, indent=1))
        else:
            print(f"cannot grade -- {why}")
        return 2
    import hw5lib as lib
    for part, fn in (("1", check_part1), ("2", check_part2), ("3", check_part3), ("5", check_part5)):
        try:
            status, detail = fn(lib)
        except Exception as ex:                            # a student's code raising is reported
            status, detail = "error", f"{type(ex).__name__}: {ex}\n" + traceback.format_exc(limit=2)
        res["parts"][part] = {"status": status, "detail": detail}
    res["parts"]["4"] = {"status": "info", "detail": "run part4_bounds.py and answer in your report"}
    all_ok = all(v["status"] in ("ok", "info") for v in res["parts"].values())
    if as_json:
        print(json.dumps(res, indent=1))
    else:
        bad = [k for k, v in res["versions"].items() if not v["ok"]]
        print("setup: shipped files unchanged; tools " + ("as pinned" if not bad else
              "DIFFER from the pins: " + ", ".join(f"{k} {res['versions'][k]['got']} (pinned "
                                                     f"{res['versions'][k]['want']})" for k in bad)))
        for k in sorted(res["parts"]):
            v = res["parts"][k]
            print(f"  Part {k}: {v['status']:<12} {v['detail']}")
        print("\nall parts OK" if all_ok else "\nnot every part is OK yet")
    return 1 if (strict and not all_ok) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
