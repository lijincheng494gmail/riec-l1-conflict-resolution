# RIEC-L1 methodological notebook

This dossier is a curated research-design record for RIEC-L1. It is not the manuscript, not a reviewer response, and not a private scratchpad. Its purpose is to document how the method was framed, which mathematical objects matter, how the implementation follows the method, and what evidence boundaries should be respected when reading or extending the work.

RIEC-L1 is treated here as a finite-library conflict-resolution layer. It does not introduce a new risk estimator, a new information criterion, or a universal model-selection theory. It takes familiar evidence ingredients, such as grouped predictive risk and BIC-style structural cost, and turns their disagreement into a declared decision operation.

## Who this dossier is for

This dossier is intended for readers who want to understand the design reasoning behind the repository rather than only run the scripts. It is useful for:

- readers who want to see why side-by-side BIC and grouped-CV inspection was not considered a complete decision rule;
- researchers who want to reuse the conflict-resolution formalism in another finite candidate library;
- engineers who want to audit how a recommendation was obtained;
- contributors who want to understand how the code, evidence ledger, and paper assets fit together.

It is not intended to contain editorial correspondence, reviewer comments, cover letters, marked manuscripts, or private revision notes. Those are deliberately excluded from the public reproducibility package.

## How to read it

A short path is:

1. `01_problem_origin_and_scope.md` for the problem framing;
2. `03_from_side_by_side_to_conflict_resolution.md` for the key methodological idea;
3. `04_mathematical_design_notes.md` for the mathematical boundary conditions;
4. `05_algorithm_design_record.md` for the deterministic workflow;
5. `07_negative_results_and_abandoned_claims.md` for the evidence boundaries.

A code-oriented path is:

1. `02_statistical_objects.md`;
2. `05_algorithm_design_record.md`;
3. `08_code_architecture_notes.md`;
4. `09_reproducibility_and_audit_principles.md`.

A future-work path is:

1. `04_mathematical_design_notes.md`;
2. `06_experiment_design_ledger.md`;
3. `10_limitations_and_future_extensions.md`.

## Core idea in one paragraph

In engineering model selection, the analyst often does not search an unrestricted hypothesis space. Instead, they choose from a finite, reviewable library of interpretable candidates. Standard criteria can disagree: a BIC-style signal may prefer a compact candidate, while grouped cross-validation may favor a more flexible candidate. Side-by-side inspection can reveal the disagreement, but it does not prescribe a reproducible action. RIEC-L1 adds a declared decision operation: given a candidate library, baseline, grouped split, penalty calibration, and schedule parameter, it maps a descriptive evidence ledger to a conditional recommendation and exposes score gaps and switching boundaries for audit.

## Evidence boundaries

This dossier follows the same evidence boundaries as the manuscript release:

- no claim of universal model-selection optimality;
- no claim that the default `lambda_n = c/log(n_eff)` is oracle-derived;
- no claim that precise effective-sample-size calibration drives the present results;
- no claim that drying proves Page/Weibull or RIEC-L1 statistically superior to Midilli;
- no claim that the deterministic controlled path is a fourth empirical benchmark or Monte Carlo simulation;
- no claim of predictive dominance over AIC, BIC, grouped CV, WAIC, or Bayesian comparison.

The goal is not to make the method look stronger than the evidence supports. The goal is to make the decision rule, its evidence inputs, and its limits auditable.
