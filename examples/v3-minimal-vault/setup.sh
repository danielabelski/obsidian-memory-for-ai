#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

chmod +x tools/*.sh tools/pre-commit

if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

PY=.venv/bin/python
"$PY" -m pip install -r requirements.txt
./tools/rebuild-views.sh
"$PY" tools/lint.py

echo "v3 example vault setup complete."
