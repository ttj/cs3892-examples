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
[[ ${#targets[@]} -eq 0 ]] && targets=(notebooks/*.ipynb)

for nb in "${targets[@]}"; do
  echo "== executing $nb"
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
