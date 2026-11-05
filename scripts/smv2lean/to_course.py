#!/usr/bin/env python3
"""Translate an SMV model to Lean with smv2lean, retargeted to a session's own `TS`.

    python3 to_course.py path/to/model.smv S20          # print the Lean
    python3 to_course.py path/to/model.smv S20 out.lean # write it

smv2lean (ttj/leansmv) emits a file for leansmv's `VerifDemo.TransitionSystem`, whose structure
is `TransitionSystem` with fields `init` and `next`. The course's sessions use HW4's definitions:
`TS` with `init` and `step`, inside the session's namespace. Nothing else changes.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from smv2lean import SmvToLean, _capitalize  # noqa: E402
from smv_parser import parse_smv_file  # noqa: E402


def translate(smv_path, ns):
    """The Lean text for `smv_path`, in namespace `ns`, importing `ns`.TS."""
    name = _capitalize(os.path.splitext(os.path.basename(smv_path))[0])
    lean = SmvToLean(parse_smv_file(str(smv_path)), name, source_file=str(smv_path)).generate()
    for old, new in [("import VerifDemo.TransitionSystem", f"import {ns}.TS\n\nnamespace {ns}"),
                     (f"VerifDemo.NuXMV.{name}Proofs", f"{ns}.{name}Proofs"),
                     ("scripts/smv2lean.py", "scripts/smv2lean (ttj/leansmv)"),
                     ("  next s s' :=", "  step s s' :=")]:
        assert old in lean, old
        lean = lean.replace(old, new)
    lean = re.sub(r"\bTransitionSystem\b", "TS", lean)
    return lean.rstrip() + f"\n\nend {ns}\n"


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    text = translate(sys.argv[1], sys.argv[2])
    if len(sys.argv) == 4:
        open(sys.argv[3], "w", encoding="utf-8").write(text)
        print("wrote", sys.argv[3])
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(text, end="")
