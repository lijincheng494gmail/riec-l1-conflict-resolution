# Controlled conflict-resolution audit

The controlled audit is a deterministic residual-anchored path based on the drying benchmark. It is used to inspect the decision rule, not to claim another empirical validation benchmark.

The path is:

```text
y_i(alpha) = yhat_Page,i + alpha [yhat_Midilli,i - yhat_Page,i] + r_Page,i
```

where `alpha` controls the strength of the Page-to-Midilli fitted departure while preserving the original drying design and Page residual pattern.

The audit reports:
- a library-level compact-versus-flexible margin `H_CF(alpha)`;
- a fixed Page-versus-Midilli pairwise gap `Delta_PM(alpha)`;
- boundary decomposition of BIC gap and predictive correction.

Interpretation limits:
- not a fourth empirical benchmark;
- not independent external validation;
- not stochastic simulation;
- not evidence of predictive dominance.
