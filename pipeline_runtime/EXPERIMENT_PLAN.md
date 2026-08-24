# Experiment plan (freeze points before running)

This file is meant to be **frozen before full runs**.  
It captures the L0 evaluation world + L1 selection settings.

## Global (applies to all cases)
- Criterion: BIC + CV + XPE + C_lambda
- Default effective sample size: n_eff = n (simplified for this RINENG paper)
- lambda(n_eff): c / log(n_eff), with c = 1.0 (tunable)
- Baseline model: case-specific (usually the simplest worldview)

## Case I (Optics) — to be filled once raw spectra are added
- Data file(s): [TODO] place under `data/raw/optics/`
- Split (L0): cross-condition / cross-angle holdout (avoid point-wise leakage)
- Metric: held-out spectral RMSE/MSE
- Baseline: Two-beam (simplest)

## Case II (RTD) — included and runnable
- Data: `data/raw/rtd/data3.csv` (3 runs)
- Split (L0): leave-one-run-out (GroupKFold by run_id)
- Metric: held-out MSE on E(t)
- Baseline: Gamma(2-parameter)

## Case III (Drying) — to be filled once public dataset is chosen
- Data file(s): [TODO] place under `data/raw/drying/`
- Split (L0): leave-one-condition-out (LOCO-CV by condition_id)
- Metrics: curve MSE + time-to-target error t*
- Baseline: Lewis/Newton model

