# Algorithm design record

## Purpose

This note records the deterministic workflow used by RIEC-L1. The goal is to make the method executable and auditable rather than a loose narrative about being conservative or balanced.

## Inputs

A RIEC-L1 run requires:

- dataset `D`;
- deployment-relevant group labels;
- finite candidate library `M_set`;
- baseline model `M0`;
- effective row-count calibration input `n_eff`;
- declared schedule parameter `c`;
- model-fitting and grouped-validation routines.

The candidate library and baseline should be declared before looking at the final winner.

## Core workflow

1. Identify the evidence object: empirical benchmark `D_emp` or deterministic audit path `D_path(alpha)`.
2. Declare the decision context `theta`.
3. Fit each candidate and compute SSE and pseudo-likelihood-style structural signals.
4. Run grouped holdout and compute `E_CV`.
5. Compute `XPE` relative to the baseline.
6. Build the evidence ledger.
7. Compute `C_lambda` and select the score minimizer.
8. Report score gaps, runner-up margin, and pairwise switching diagnostics.
9. Output figures and tables that preserve the ledger, not only the winner.

## Why the baseline is explicit

The baseline defines the scale of XPE. Different baselines can change the interpretation of relative improvement. RIEC-L1 is therefore conditional on the declared baseline.

## Why grouped CV is not optional

The examples are curve datasets. Random point-wise splitting can leak trajectory-level information. The grouped split is the main design element that aligns evaluation with deployment.

## Why the runner-up matters

A model label alone is not enough. If the runner-up margin is tiny, the recommendation is fragile on the declared score scale. If the margin is larger, the decision is more separated from near-tie alternatives. This is not a confidence interval, but it is an audit signal.

## Why post-hoc tuning is avoided

The schedule parameter `c` should not be tuned after seeing the desired winner. If a different value of `c` is used, it should be declared and reported with switchpoints or sensitivity analysis. This preserves the distinction between a pre-specified decision rule and a retrospective justification.

## Implementation mapping

The code follows this design:

- core scoring functions are in `src/riec/core.py`;
- grouped CV utilities are in `src/riec/cv.py`;
- case-specific models are in `src/riec/models/`;
- case runners are in `scripts/run_optics.py`, `scripts/run_rtd.py`, and `scripts/run_drying.py`;
- revision diagnostics and controlled audit support are in `src/riec/revision_support.py` and revision scripts.

The output design keeps metrics tables, selected JSON summaries, and figures separate so that the recommendation can be traced back to the underlying ledger.
