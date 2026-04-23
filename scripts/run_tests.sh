#!/usr/bin/env bash
set -euo pipefail
echo "Creating virtualenv .venv if missing..."
python -m venv .venv || true
source .venv/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi
pip install pytest
echo "Running pytest..."
pytest -q
