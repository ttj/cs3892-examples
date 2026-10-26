"""HW3 Part 4 -- measure a test suite for c/triangle.c: branch coverage, and does it catch the bug?

    python3 hw3_part4_coverage.py ../tests/example.txt
    python3 hw3_part4_coverage.py ../tests/cbmc.txt ../tests/llm.txt

For each test file:
  1. compiles triangle.c with gcc --coverage, runs every test, and checks each result
     against a reference model of the specification (in this file);
  2. prints the branch coverage gcov measures (gcov -b);
  3. does the same against the MUTANT (triangle.c compiled with -DMUTANT, which has one bug)
     and reports whether any test in the suite exposes it.

gcov counts branches of the compiled code, so each operand of || and && is its own branch.
CBMC's --cover branch counts decisions in its own program representation. The two numbers
need not agree; say why when they do not.

Exits 0 whatever the results.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

C = Path(__file__).resolve().parent.parent / "c"


def spec(a, b, c):
    """The specification, independent of triangle.c."""
    if min(a, b, c) <= 0 or a + b <= c or a + c <= b or b + c <= a:
        return 0
    if a == b == c:
        return 1
    if a == b or b == c or a == c:
        return 2
    return 3


def read_tests(path):
    tests = []
    for line in Path(path).read_text().splitlines():
        line = line.split("#")[0].strip()
        if line:
            tests.append(tuple(int(t) for t in line.replace(",", " ").split()[:3]))
    return tests


def measure(tests, mutant=False):
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        calls = "".join('    printf("%%d\\n", triangle(%d, %d, %d));\n' % t for t in tests)
        (d / "main.c").write_text("#include <stdio.h>\nint triangle(int, int, int);\nint main(void) {\n"
                                  + calls + "    return 0;\n}\n")
        (d / "triangle.c").write_text((C / "triangle.c").read_text())
        flags = ["-DMUTANT"] if mutant else []
        subprocess.run(["gcc", "--coverage", "-O0", *flags, "-c", "triangle.c", "-o", "triangle.o"], cwd=d, check=True)
        subprocess.run(["gcc", "--coverage", "-O0", "-o", "t", "triangle.o", "main.c"], cwd=d, check=True)
        got = [int(x) for x in subprocess.run(["./t"], cwd=d, capture_output=True, text=True, check=True).stdout.split()]
        gcov = subprocess.run(["gcov", "-b", "triangle.o"], cwd=d, capture_output=True, text=True).stdout
    branches = next((l for l in gcov.splitlines() if l.startswith("Taken at least once")), "no branch data")
    lines = next((l for l in gcov.splitlines() if l.startswith("Lines executed")), "")
    return got, lines, branches


if __name__ == "__main__":
    for path in sys.argv[1:] or [str(Path(__file__).resolve().parent.parent / "tests" / "example.txt")]:
        tests = read_tests(path)
        print("%s: %d tests" % (path, len(tests)))
        got, lines, branches = measure(tests)
        wrong = [(t, g, spec(*t)) for t, g in zip(tests, got) if g != spec(*t)]
        print("   triangle.c   %s   branches: %s" % (lines, branches.replace("Taken at least once:", "")))
        print("                %s" % ("every result matches the specification" if not wrong else
                                       "WRONG on %d tests, e.g. %s" % (len(wrong), wrong[0])))
        got_m, _, _ = measure(tests, mutant=True)
        caught = [(t, g, spec(*t)) for t, g in zip(tests, got_m) if g != spec(*t)]
        print("   the mutant   %s" % ("CAUGHT by %d tests, e.g. triangle%s = %d, should be %d"
                                      % (len(caught), caught[0][0], caught[0][1], caught[0][2]) if caught
                                      else "NOT caught: every test passes on the buggy version"))
        print()
