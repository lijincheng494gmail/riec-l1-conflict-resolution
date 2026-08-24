# Drying raw data (place your files here)

Expected minimal format (CSV suggested):
A long-form table with columns:
- `material_id` (optional)
- `condition_id` (required for LOCO-CV)
- `T` (temperature, optional)
- `v` (air velocity, optional)
- `t` (time)
- `MR` (moisture ratio, 0..1)

File name suggestion:
- `drying_curves.csv`

If no raw file is provided, the pipeline falls back to a small demo dataset
(`data/demo/drying_demo.csv`) so that `bash scripts/run_all.sh` works out of
the box. For the paper, replace the demo with a credible public dataset here.
