#!/usr/bin/env bash
# Execute notebooks headlessly, top to bottom, and fail on the first error.
#
#   bash scripts/run_notebooks.sh                  # every notebook
#   bash scripts/run_notebooks.sh notebooks/x.ipynb
#
# This is what keeps the Colab link honest: the notebook runs the real example
# files, so if an example changes and the notebook stops working, CI says so
# instead of a student finding out in class.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${PYTHON:-python3}"
cd "$ROOT"

targets=("$@")
if [[ ${#targets[@]} -eq 0 ]]; then
  targets=(notebooks/*.ipynb)
  # Notebooks of HEAVY sessions (see check_examples.sh) run only when named or with HEAVY=1.
  if [[ "${HEAVY:-0}" != "1" ]]; then
    keep=(); for nb in "${targets[@]}"; do s="$(basename "$nb" .ipynb)"; [[ -f "sessions/$s/HEAVY" ]] && echo "== $nb: skipped (HEAVY; run it by name)" || keep+=("$nb"); done
    targets=("${keep[@]}")
  fi
fi

for nb in "${targets[@]}"; do
  echo "== executing $nb"
  # FRESH=1 starts every notebook the way a new Colab runtime does: no Z3 and
  # no downloaded tools. Without it, the first notebook that installs Z3 hides
  # every later one that forgot to -- which is how sessions 15 and 16 shipped a
  # setup cell that passed CI and failed on Colab with "No module named 'z3'".
  if [[ "${FRESH:-0}" == "1" ]]; then
    "$PY" -m pip uninstall -y -q z3-solver >/dev/null 2>&1 || true
    rm -rf "$HOME/.cache/cs3892"
  fi
  "$PY" - "$nb" <<'PYEOF'
import sys, nbformat
from nbclient import NotebookClient
path = sys.argv[1]
nb = nbformat.read(path, as_version=4)
NotebookClient(nb, timeout=600, kernel_name="python3",
               resources={"metadata": {"path": "."}}).execute()
print(f"   ok: {len(nb.cells)} cells executed")
PYEOF
done
echo
echo "PASSED — notebooks execute end to end"
