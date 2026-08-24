# Reproducibility guide

## Environment

Recommended: Python 3.11 or 3.12.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Sanity check

```bash
cd 03_analysis_code/pipeline_runtime
python scripts/check_project.py
```

## Reproduce empirical cases

```bash
bash scripts/run_all.sh
```

Individual cases:

```bash
python scripts/run_optics.py
python scripts/run_rtd.py
python scripts/run_drying.py
```

## Reproduce major-revision comparison tables

```bash
python scripts/revision_compare_standard_criteria.py --source existing --tag arrays_round1_2026-04-24
python scripts/revision_lambda_sensitivity.py --tag arrays_round1_2026-04-24
python scripts/revision_neff_sensitivity.py --tag arrays_round1_2026-04-24
python scripts/revision_fold_statistics.py --tag arrays_round1_2026-04-24
python scripts/revision_write_summary.py --tag arrays_round1_2026-04-24
```

## Reproduce controlled conflict-resolution audit

```bash
bash scripts/run_controlled_conflict_audit_quick.sh
```

The public manuscript reports the deterministic residual-anchored path. Stochastic smoke-test runs are not used for inferential claims.

## Notes

The runtime writes outputs in place and to `05_results_workspace/revision_experiments/`. Use git status or a clean copy if you want to compare fresh outputs with the bundled reference outputs.
