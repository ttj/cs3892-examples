"""Session 24's toy network and its bounds (nnv.py), reused here unchanged.

Session 25 asks new questions of the same 2 -> 2 -> 2 ReLU network, so it imports session 24's
nnv.py rather than keeping a second copy that could drift.
"""
import sys
from pathlib import Path

S24 = Path(__file__).resolve().parents[2] / "cs3892-2026-11-19-nn-verification-robustness" / "python"
sys.path.insert(0, str(S24))
from nnv import *  # noqa: E402,F401,F403
import nnv  # noqa: E402,F401
