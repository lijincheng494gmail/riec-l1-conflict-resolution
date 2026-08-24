# Mathematical design notes

## Purpose

This note collects the mathematical ideas behind the RIEC-L1 score. It is not a proof of universal optimality. It explains how the finite-library decision rule is constructed and how to interpret its boundaries.

## Grouped risk

For candidate `M`, the deployment-aligned risk is computed by holding out whole groups:

```text
E_CV(M) = grouped held-out mean squared error
```

The group definition is case-specific. The purpose is to align validation with deployment, not to estimate an independent row-level error under random point splitting.

## Pseudo-likelihood-style structural signal

The BIC-style coordinate is:

```text
BIC_eff(M) = n_eff log[SSE(M)/n_eff] + k_M log(n_eff)
```

In the present package, AIC, AICc, and `BIC_eff` are pseudo-likelihood-style comparison signals. They are computed consistently across the finite library but are not interpreted as fully specified correlated-error likelihood comparisons or Bayes factors.

## Baseline-normalized gain

The baseline-relative grouped predictive gain is:

```text
XPE(M) = E_CV(M0) / E_CV(M)
```

`XPE(M) > 1` indicates grouped-CV improvement over the declared baseline. The baseline must be declared because XPE is relative.

## RIEC-L1 score

The RIEC-L1 score is:

```text
C_lambda(M) = BIC_eff(M) - lambda_n log[XPE(M)]
```

Lower values are preferred. The score is not a probability, posterior weight, or p-value.

## Choice map

The decision rule is:

```text
M_RIEC = argmin_M C_lambda(M)
```

The output is conditional on the declared decision context.

## Candidate score gaps

For any candidate `M`:

```text
G_theta(M) = C_lambda(M) - C_lambda(M_RIEC)
```

The runner-up margin is:

```text
G_theta* = min_{M != M_RIEC} G_theta(M)
```

A small margin indicates near-tie behavior under the declared score. It does not imply statistical equivalence.

## Pairwise switching condition

For two candidates `A` and `B`, `B` is preferred over `A` when:

```text
C_lambda(B) - C_lambda(A) < 0
```

Expanding the score gives:

```text
[BIC_eff(B) - BIC_eff(A)]
- lambda_n log[E_CV(A) / E_CV(B)] < 0
```

Equivalently:

```text
BIC_eff(B) - BIC_eff(A)
< lambda_n log[E_CV(A) / E_CV(B)]
```

This is the pairwise conflict-resolution boundary.

## c-switchpoint

With:

```text
lambda_n = c / log(n_eff)
```

and if the denominator is positive, the `c` value at which `A` and `B` switch is:

```text
c*(A,B) = [BIC_eff(B)-BIC_eff(A)] log(n_eff)
          / log[E_CV(A)/E_CV(B)]
```

This is not an estimator of an optimal `c`. It is an interpretability relation: it says how much declared predictive-gain tolerance would be required for one candidate to replace another under the score.

## Lambda is not oracle-derived

The default `c = 1` is a reproducibility default, not a universal tuning law. A principled oracle derivation would require assumptions about deployment utility, loss asymmetry, data generation, candidate-library construction, model misspecification, and the engineering cost of added complexity. Those assumptions are not identified by the three benchmark datasets.

## n_eff is a calibration input, not the main dependence safeguard

The primary protection against curve dependence is grouped validation. In the present benchmarks, `n_eff = n` is used as a row-count penalty-calibration input, and sensitivity checks only stress row-count reductions. The package does not validate a group-count effective-sample-size estimator.
