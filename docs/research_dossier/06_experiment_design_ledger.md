# Experiment design ledger

## Purpose

This note explains the experiment families in the package and the evidence each family can support. It is deliberately conservative about interpretation.

## Empirical benchmark evidence

### Optics

The optics case contains dense spectral sampling but only a small number of material-angle deployment groups. Agreement among AIC, AICc, BIC-style signal, grouped CV, and RIEC-L1 should be interpreted as criterion agreement within the declared grouped design, not as thousands of independent deployment samples.

### RTD

The RTD case contains dense time sampling across tracer runs. The leave-one-run-out design evaluates whole-run generalization. Again, dense time points are not independent deployment units.

### Drying

The drying case has six held-out operating conditions. It is the weak-evidence disagreement case. Grouped CV favors a flexible candidate, while the declared RIEC-L1 rule remains on the compact Page/Weibull-equivalent two-parameter side under the default schedule. The paired fold checks are exploratory and low-powered.

## Standard-criteria comparison

The revision compares:

- AIC;
- AICc;
- BIC-style pseudo-likelihood signal;
- grouped CV;
- RIEC-L1.

This comparison is not framed as a victory table. It records where criteria agree and where they disagree.

## Sensitivity diagnostics

### Lambda schedule

The `c` sensitivity analysis shows how the recommendation changes under different declared predictive-gain tolerances. This does not estimate the true `c`; it documents schedule dependence.

### n_eff row-count stress

The `n_eff` sensitivity analysis reduces row-count calibration values. It does not validate a group-count effective-sample-size estimator.

### Fold-wise drying checks

The sign and Wilcoxon checks over six drying folds are exploratory paired checks. They are included to avoid overclaiming from a small grouped dataset.

## Controlled conflict-resolution audit

The controlled audit uses a deterministic residual-anchored path:

```text
D_path(alpha)
```

It modifies the drying response along a fitted Page-to-Midilli departure while preserving the original design and residual pattern. The purpose is to show how the declared rule behaves as the compact-versus-flexible margin changes.

It is not a fourth empirical benchmark, not an external validation dataset, and not a stochastic simulation.

## Evidence map

| Evidence object | Purpose | Supports | Does not support |
|---|---|---|---|
| `D_emp` | Empirical grouped ledgers | Case-specific criterion agreement/disagreement | Universal optimality |
| `lambda` sensitivity | Schedule diagnostics | Conditional dependence on `c` | Oracle tuning |
| `n_eff` stress | Penalty-calibration stress | Row-count robustness within tested range | Group-count effective sample size |
| Drying paired checks | Fold-level description | Weak-evidence disagreement | Confirmatory validation |
| `D_path(alpha)` | Rule-behavior audit | Deterministic margin transition | Monte Carlo operating characteristics |
