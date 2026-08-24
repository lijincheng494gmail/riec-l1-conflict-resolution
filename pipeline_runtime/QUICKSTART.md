# Quickstart (bash)

## 0) Create a virtual environment (recommended)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r environment/requirements.txt
```

## 1) Sanity check (paths + deps)
```bash
python scripts/check_project.py
```

## 2) Run RTD case (works out-of-the-box; uses provided CSVs)
```bash
python scripts/run_rtd.py
```

Outputs:
- `tables/rtd/metrics.csv`
- `figures/rtd/*`
- `outputs/rtd/selected.json`

## 3) Run all cases
```bash
bash scripts/run_all.sh
```
Notes:
- If you do not provide raw data for Optics/Drying, the scripts fall back to
  small demo datasets in `data/demo/` so the repository runs out-of-the-box.
  For the paper, replace the demo with your real/public datasets under:
  - `data/raw/optics/`
  - `data/raw/drying/`

## 4) Build paper assets snapshot (optional)
```bash
python scripts/build_paper_assets.py
```

