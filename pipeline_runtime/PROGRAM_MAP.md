# Program map (what each file does)

## Root docs
- `README.md`: what this project is
- `QUICKSTART.md`: how to run
- `EXPERIMENT_PLAN.md`: freeze points (L0 + L1 settings)

## Data
- `data/raw/rtd/data1.csv`: single run tracer response (conductivity vs time)
- `data/raw/rtd/data3.csv`: three repeated runs
- `data/raw/optics/`: put your spectra files here (see `data/raw/optics/README.md`)
- `data/raw/drying/`: put your drying dataset here (see `data/raw/drying/README.md`)

## Scripts (entry points)
- `scripts/check_project.py`: checks deps + file presence; prints what is runnable
- `scripts/run_rtd.py`: runs Case II end-to-end (loads data, builds E(t), evaluates models, saves tables+figures)
- `scripts/run_optics.py`: runs Case I end-to-end (raw data preferred; demo fallback available)
- `scripts/run_drying.py`: runs Case III end-to-end (raw data preferred; demo fallback available)
- `scripts/run_all.sh`: runs all three scripts
- `scripts/build_paper_assets.py`: copies key outputs into `paper/assets_snapshot/`

## Core library (`src/riec/`)
- `core.py`: BIC / CV / XPE / C_lambda computation and selection
- `cv.py`: split helpers (GroupKFold wrappers)
- `reporting.py`: save tables, generate simple plots
- `models/`: candidate model implementations (RTD + proxy optics + canonical drying)
- `adapters/`: data loaders and transformations per case (RTD/optics/drying)

