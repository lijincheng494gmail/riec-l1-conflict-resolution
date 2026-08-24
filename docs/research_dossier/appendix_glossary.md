# Appendix: glossary

## AIC / AICc

Pseudo-likelihood-style comparison signals used as familiar reference criteria. They are not interpreted as full correlated-error likelihood comparisons in this package.

## BIC_eff

A BIC-style structural signal using an explicit `n_eff` penalty-calibration input. It is a comparison coordinate, not a full Bayes factor.

## Candidate library

A finite, reviewable set of candidate models. RIEC-L1 is not defined as unrestricted model search.

## c

Declared scale parameter in `lambda_n = c/log(n_eff)`. The default `c = 1` is a reproducibility default, not an oracle-derived optimum.

## c-switchpoint

For a pair of candidates, the value of `c` at which the RIEC-L1 score would switch from one candidate to the other.

## C_lambda

The RIEC-L1 score combining a BIC-style coordinate and a baseline-relative grouped predictive-gain coordinate.

## D_emp

Observed empirical benchmark data.

## D_path(alpha)

Deterministic residual-anchored intervention path used to audit the decision rule in the drying setting.

## D_sim

A stochastic simulation evidence object. Not reported in the current package.

## E_CV

Deployment-aligned grouped cross-validated mean squared error.

## Evidence ledger

A table of descriptive evidence for all candidates. It is not itself a decision rule.

## G_theta

Candidate score gap from the RIEC-selected model.

## G_theta*

Runner-up conflict margin under the declared score.

## Grouped CV

Cross-validation where complete deployment groups are held out.

## n_eff

Penalty-calibration input used in `BIC_eff` and `lambda_n`. In this package it is a row-count calibration input, not a validated group-count effective-sample-size estimator.

## Pairwise switching boundary

The inequality defining when one candidate can replace another under the RIEC-L1 score.

## RIEC-L1

A finite-library conflict-resolution layer that maps a descriptive evidence ledger to a conditional recommendation under a declared decision context.

## XPE

Baseline-normalized grouped predictive gain: `E_CV(M0)/E_CV(M)`.
