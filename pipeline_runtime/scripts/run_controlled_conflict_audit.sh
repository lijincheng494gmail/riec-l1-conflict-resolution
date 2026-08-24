#!/usr/bin/env bash
set -euo pipefail

# Run from 03_analysis_code/pipeline_runtime or from any folder.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${RUNTIME_ROOT}"

REPLICATES="${1:-0}"
python scripts/check_project.py
python scripts/revision_controlled_conflict_audit.py --replicates "${REPLICATES}"
