# Code architecture notes

## Purpose

This note maps the conceptual design of RIEC-L1 to the repository structure. The package is organized so that a reader can trace raw data to metrics, selections, figures, and paper-facing assets.

## Runtime package

The executable code lives under:

```text
03_analysis_code/pipeline_runtime/
```

Important files include:

- `src/riec/core.py`: core scoring functions and selection helpers;
- `src/riec/cv.py`: grouped cross-validation utilities;
- `src/riec/models/`: candidate libraries for optics, RTD, and drying;
- `src/riec/adapters/`: data preparation and case-specific adapters;
- `src/riec/revision_support.py`: revision diagnostics and controlled-audit support;
- `scripts/run_all.sh`: empirical benchmark runner;
- `scripts/run_controlled_conflict_audit_quick.sh`: deterministic controlled audit runner.

## Case scripts

Each empirical case has a runner:

- `scripts/run_optics.py`;
- `scripts/run_rtd.py`;
- `scripts/run_drying.py`.

Keeping case scripts separate makes case assumptions visible: optics uses condition groups, RTD uses run groups, and drying uses operating-condition groups.

## Outputs

The runtime writes:

- metrics tables;
- selected-model JSON summaries;
- figures;
- controlled-audit diagnostics;
- revision experiment outputs.

The key principle is that figures and paper tables should be reconstructable from stored ledger outputs.

## Results workspace

`05_results_workspace/current_main_results/` stores reference snapshots for the three empirical cases. `05_results_workspace/revision_experiments/` stores diagnostics added for revision and controlled-audit work.

This separation is intentional. It prevents controlled audit artifacts from being mistaken for the original empirical benchmark outputs.

## Paper assets

`paper_assets/` stores public-facing table, figure, and math-definition assets. Editorial correspondence, cover letters, reviewer responses, marked manuscripts, and internal issue reports are excluded from the public package.

## Reproducibility invariant

The intended trace is:

```text
raw CSV data -> case script -> metrics.csv -> selected.json -> figures/tables -> paper assets
```

A reader should be able to inspect each link in the chain rather than trust a single reported winner.
