#!/usr/bin/env bash
set -euo pipefail

echo "== Run all cases =="
python scripts/check_project.py
python scripts/run_rtd.py
python scripts/run_optics.py
python scripts/run_drying.py

echo "== Done =="
