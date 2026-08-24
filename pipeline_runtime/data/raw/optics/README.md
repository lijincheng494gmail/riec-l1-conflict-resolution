# Optics raw data (place your files here)

Expected minimal format (CSV suggested):
- columns: `wavenumber`, `reflectance`
- optional: `condition_id` or `angle_deg` if you have multiple conditions

Examples:
- single condition: `spectra.csv`
- multiple conditions: `spectra_angle10.csv`, `spectra_angle15.csv` + `meta.json`

If no raw CSV is provided, the pipeline falls back to a small demo dataset
(`data/demo/optics_demo.csv`) so that `bash scripts/run_all.sh` works out of
the box. For the paper, replace the demo with your real spectra here.
