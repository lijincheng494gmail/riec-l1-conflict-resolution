# pipeline/ — Reproducible experiment pipeline (RIEC-L0/L1)

This folder is the **only place you run experiments**. It implements:

- L0: leakage-aware splits (group / run-level / condition-level)
- L1: candidate model libraries indexed by (C,f)
- scoring: BIC / CV risk / XPE / C_lambda
- auto outputs: tables + figures for the paper

## What is included

- `src/` : RIEC selection engine + model libraries
- `scripts/` : runnable entry points (per case + run_all.sh)
- `data/raw/` : raw data inputs (preferred for paper)
  - `rtd/` is already included (data1.csv, data3.csv)
  - `optics/` and `drying/` contain format READMEs; you can add your real CSVs
- `data/demo/` : small demo datasets so the pipeline runs out-of-the-box
- `docs/cases/` : problem + model inventory + C/f mapping for the 3 cases
- `docs/model_tables/` : LaTeX tables of candidate model sets (for Supplement)
- `tools/` : your HTML workbenches (reference only)
- `sources/` : raw provenance files (PDF/HTML/CSV) used to build the case docs

## Outputs (generated)

When you run scripts, new files are generated into:

- `tables/<case>/metrics.csv`
- `figures/<case>/*.png`
- `outputs/<case>/*` (selected model summaries, configs, etc.)

A sample output from a previous run is kept in:

- `example_run/`

Your new runs will start from empty `tables/`, `figures/`, and `outputs/`.

## Quickstart

See `QUICKSTART.md`.
