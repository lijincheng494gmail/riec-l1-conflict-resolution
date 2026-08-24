# Method overview

RIEC-L1 constructs an evidence ledger over a finite candidate library and applies a declared decision map.

For each candidate `M`, the runtime stores:
- grouped held-out risk `E_CV(M)`;
- pseudo-likelihood-style structural signals including `BIC_eff(M)`;
- baseline-normalized predictive gain `XPE(M)`;
- RIEC score `C_lambda(M) = BIC_eff(M) - lambda_n log[XPE(M)]`.

The selected candidate is `argmin C_lambda(M)`. Pairwise switching is interpreted through the boundary:

```text
BIC_eff(B) - BIC_eff(A) < lambda_n log[E_CV(A) / E_CV(B)]
```

The default `lambda_n = c/log(n_eff)` with `c=1` is a declared reproducibility default, not an oracle-derived tuning law. In the bundled benchmarks, `n_eff` is used as a row-count penalty-calibration input; grouped evaluation is the main safeguard against curve-level dependence.
