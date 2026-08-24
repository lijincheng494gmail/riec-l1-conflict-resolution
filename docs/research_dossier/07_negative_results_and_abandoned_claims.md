# Claims deliberately not made

## Purpose

This note records claims that the package deliberately avoids. This is not a failure log. It is an evidence-boundary discipline: a method is stronger when it is clear about what the evidence cannot establish.

## 1. RIEC-L1 is not a universal selector

The method is defined for finite, reviewable candidate libraries. It does not claim global optimality over unrestricted model classes.

## 2. RIEC-L1 is not a new risk estimator

Grouped CV risk and BIC-style structural signals are familiar ingredients. The contribution is the declared decision operation over the ledger, not a new estimator of risk.

## 3. The default lambda schedule is not oracle-derived

The default `c = 1` is a reproducibility default. It is not derived from a universal deployment utility function or asymptotic optimality theorem.

## 4. Drying does not prove Page/Weibull superiority

The drying case is a weak-evidence disagreement case. Exploratory paired checks do not show decisive separation between the grouped-CV-selected flexible model and the compact Page/Weibull-equivalent class. The RIEC-L1 output is conditional on the declared score.

## 5. Page and Weibull should not be over-separated in drying

In the drying library, Page and Weibull are algebraic reparameterizations of the same stretched-exponential form. Tiny numerical differences between their stored scores should not be interpreted as substantive scientific separation.

## 6. n_eff is not validated as a true independent-sample estimator

The package uses `n_eff = n` as a row-count penalty-calibration input and reports row-count stress checks. It does not estimate a true group-count effective sample size.

## 7. The controlled path is not a Monte Carlo simulation

`D_path(alpha)` is deterministic. It does not generate repeated samples, selection frequencies, or operating-characteristic confidence intervals.

## 8. Standard criteria are not defeated

The package does not claim that RIEC-L1 outperforms AIC, BIC, grouped CV, WAIC, or Bayesian comparison. It records how a declared finite-library decision rule behaves when familiar criteria agree or disagree.

## Why this matters

Overstating a method can make a result look stronger in the short term but weaker under review. RIEC-L1 is most defensible when its contribution is stated narrowly: it is an auditable conflict-resolution layer for finite engineering libraries.
