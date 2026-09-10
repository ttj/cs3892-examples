#!/usr/bin/env python3
"""Run one .smt2 file and print its verdict, using the Z3 Python bindings.

Why this exists: the `z3-solver` pip wheel ships the bindings but **no `z3`
CLI**, so on Google Colab there is nothing to shell out to. This gives every
environment one identical way to run an SMT-LIB file.

Each file may carry a first-line contract:

    ; EXPECT: unsat

which this script verifies. That keeps the expected answer next to the example
instead of in a table someone forgets to update.

    python3 scripts/run_smt2.py path/to/file.smt2
"""

from __future__ import annotations

import re
import sys


def expected(path: str) -> str | None:
    with open(path) as fh:
        for line in fh:
            m = re.match(r"\s*;\s*EXPECT:\s*(\w+)", line)
            if m:
                return m.group(1)
            if line.strip() and not line.lstrip().startswith(";"):
                break          # contract must be in the header comment
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = sys.argv[1]

    import z3
    s = z3.Solver()
    s.from_file(path)          # ignores (get-model); we print it ourselves
    result = s.check()
    print(f"{path}: {result}")
    if result == z3.sat:
        print(f"  model: {s.model()}")

    want = expected(path)
    if want is None:
        print(f"  !! no '; EXPECT:' contract in {path}", file=sys.stderr)
        return 1
    if str(result) != want:
        print(f"  !! expected {want}, got {result}", file=sys.stderr)
        return 1
    print(f"  ok (expected {want})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
