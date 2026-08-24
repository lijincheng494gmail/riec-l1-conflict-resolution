#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${RUNTIME_ROOT}"
python scripts/check_project.py
python scripts/revision_controlled_conflict_audit.py --replicates 0
