# RIEC-L1 conflict-resolution layer: reproducibility package


> 中文使用说明：see `00_README_CN_请先读我.txt` for the all-in-one package guide.

This repository/archive accompanies the manuscript:

**RIEC-L1: An evidence-led conflict-resolution layer for finite candidate libraries in engineering data**

It contains the code, public tabular data, reference outputs, and reviewer-facing supplementary assets needed to reproduce the RIEC-L1 finite-library model-selection analyses for three engineering curve cases:

1. optical spectra fitting;
2. residence-time-distribution (RTD) modeling;
3. thin-layer drying kinetics.

The package also includes the deterministic residual-anchored controlled conflict-resolution audit used to explain the declared RIEC-L1 decision rule.

## What RIEC-L1 is

RIEC-L1 is not a new risk estimator or a universal model-selection theorem. It is a declared finite-library conflict-resolution layer. Given a candidate library, baseline, grouped split, penalty calibration, and score schedule, it maps a descriptive evidence ledger to a conditional recommendation. The recommendation is auditable through score gaps, runner-up margin, pairwise switching boundaries, and sensitivity diagnostics.

## Repository layout

```text
03_analysis_code/pipeline_runtime/     runnable Python code, public data, and main scripts
05_results_workspace/current_main_results/  reference outputs for the three empirical cases
05_results_workspace/revision_experiments/  revision and controlled-audit outputs
paper_assets/                          submitted figure/table/math-definition assets, no cover letters or responses
docs/                                  reproducibility, data, release, and Zenodo/GitHub notes
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

cd 03_analysis_code/pipeline_runtime
python scripts/check_project.py
bash scripts/run_all.sh
bash scripts/run_controlled_conflict_audit_quick.sh
```

The full `run_all.sh` can take several minutes because the optics case fits dense spectra. The controlled audit quick run is deterministic and comparatively fast.

## Main outputs

- empirical case metrics: `03_analysis_code/pipeline_runtime/tables/<case>/metrics.csv`
- empirical case selections: `03_analysis_code/pipeline_runtime/outputs/<case>/selected.json`
- empirical figures: `03_analysis_code/pipeline_runtime/figures/<case>/`
- standard-criteria comparison: `05_results_workspace/revision_experiments/arrays_round1_2026-04-24/`
- controlled audit outputs: `05_results_workspace/revision_experiments/arrays_editor_check_2026-05-13/controlled_conflict_audit/`

## Scope and evidence boundaries

This package supports finite candidate-library engineering curve analyses. It does not claim universal model-selection optimality, an oracle-derived lambda schedule, a validated group-count effective-sample-size estimator, or predictive dominance over AIC/BIC/grouped CV.

## Methodological notebook

For readers interested in the design reasoning behind RIEC-L1, this release includes a curated methodological notebook at:

```text
docs/research_dossier/00_readme_research_dossier.md
```

The notebook explains the problem framing, statistical objects, side-by-side inspection versus conflict resolution, pairwise switching boundaries, algorithm design, experiment design, code architecture, evidence boundaries, and future extensions. It is a public research-design record, not editorial correspondence.

## Suggested citation

Use the `CITATION.cff` file. If this archive is deposited on Zenodo, cite the Zenodo DOI as well.
