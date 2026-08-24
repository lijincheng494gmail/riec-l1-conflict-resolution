# Limitations and future extensions

## Purpose

This note lists limitations and possible extensions. It is intentionally explicit because each limitation points to a legitimate future research direction.

## Current limitations

### Finite-library scope

RIEC-L1 is defined for finite candidate libraries. It does not solve unrestricted model search or large adaptive model discovery.

### No oracle lambda

The default schedule is not derived from a universal utility function. Future work could specify an application-level utility model that trades predictive gain against structural cost.

### Pseudo-likelihood structural signals

AIC, AICc, and `BIC_eff` are used as consistent comparison coordinates, not as full correlated-error likelihoods. Future work could replace them with likelihoods that explicitly model curve correlation.

### Limited deployment groups

The empirical cases contain dense point-level data but few deployment groups. Larger grouped datasets would allow stronger statements about group-level generalization.

### No stochastic operating-characteristic study

The deterministic controlled path audits rule behavior but does not provide repeated-sampling operating characteristics. A future `D_sim` study would require predeclared data-generating equations, noise models, group heterogeneity, replicate counts, and Monte Carlo uncertainty.

## Theoretical extensions

Possible extensions include:

- a formal decision-utility derivation of `c`;
- Pareto-front interpretations of finite-library evidence ledgers;
- Bayesian versions where posterior predictive risk and model prior cost replace the current coordinates;
- explicit model-misspecification analysis;
- risk bounds conditional on finite candidate libraries and grouped split designs.

## Statistical extensions

Possible statistical extensions include:

- group-count effective-sample-size estimators;
- block bootstrap diagnostics;
- hierarchical residual models;
- correlated-error likelihoods;
- multi-output grouped risk measures.

## Engineering extensions

Possible engineering extensions include:

- model registries with predeclared candidate libraries;
- dashboard-style evidence ledgers;
- automated score-gap reports;
- decision logs for deployment teams;
- integration with laboratory or plant-level audit systems.

## Software extensions

Possible software extensions include:

- a command-line interface;
- YAML/JSON configuration for candidate libraries and baselines;
- automatic report generation;
- a plugin model registry;
- standardized export of ledgers and decision maps.

## Guiding future principle

Future extensions should preserve the core discipline: state the evidence object, declare the decision context, preserve the ledger, report the recommendation conditionally, and make boundaries visible.
