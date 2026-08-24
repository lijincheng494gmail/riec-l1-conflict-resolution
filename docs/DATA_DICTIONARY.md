# Data dictionary

## Optics

Location: `03_analysis_code/pipeline_runtime/data/raw/optics/`

Files: `SiC_angle10.csv`, `SiC_angle15.csv`, `Si_angle10.csv`, `Si_angle15.csv`.

Expected columns include:
- `wavenumber`: spectral coordinate;
- `reflectance`: observed response;
- `condition_id`: material-angle group, if present; otherwise the filename stem is used.

Grouped evaluation: leave-one-condition-out.

## RTD

Location: `03_analysis_code/pipeline_runtime/data/raw/rtd/data3.csv`.

The adapter converts tracer/electrical-conductivity traces into normalized residence-time-distribution response `E(t)` for each run.

Expected long-form output columns:
- `t`: time;
- `E`: normalized RTD response;
- `run_id`: repeated run group.

Grouped evaluation: leave-one-run-out.

## Drying

Location: `03_analysis_code/pipeline_runtime/data/raw/drying/drying_curves.csv`.

Expected columns:
- `material_id`: material/paddy type;
- `condition_id`: grouped drying condition;
- `T`: temperature;
- `t`: drying time;
- `MR`: moisture ratio response.

Grouped evaluation: leave-one-condition-out.

## Controlled audit

The deterministic controlled path is derived from the drying design grid and fitted Page/Midilli predictions. It is not an independent empirical sample, bootstrap, or Monte Carlo simulation.
