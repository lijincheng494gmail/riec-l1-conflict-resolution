# Reproducibility and audit principles

## Purpose

This note states the operational principles used in the package. They are written as rules because reproducibility is easier to audit when the rules are explicit.

## P1. Do not split within deployment groups

Curve points within the same physical condition or run should not be randomly distributed across training and validation folds. Whole groups are held out.

## P2. Preserve the full ledger

The output should not only say which model won. It should record all candidates, scores, grouped risks, structural signals, and gaps.

## P3. Separate description from decision

The evidence ledger is descriptive. The RIEC-L1 choice map is a decision rule. Mixing the two hides the point at which judgment enters the protocol.

## P4. Declare the decision context

The candidate library, baseline, grouping, penalty input, and schedule parameter should be declared before the final recommendation is interpreted.

## P5. Report margins, not only labels

A model label can hide a near tie. Score gaps and runner-up margins provide a more auditable account of the decision.

## P6. Do not interpret margins as p-values

Score margins, switching boundaries, and `c` switchpoints are diagnostics on the declared score scale. They are not confidence intervals, posterior probabilities, or formal tests.

## P7. Treat lambda as declared, not discovered

Changing `c` after seeing the winner turns the protocol into post-hoc justification. If a different `c` is used, it should be declared and accompanied by sensitivity diagnostics.

## P8. Separate empirical evidence, deterministic path, and stochastic simulation

`D_emp`, `D_path(alpha)`, and `D_sim` answer different questions. They should not be combined as if they were the same evidence object.

## P9. Keep public reproducibility separate from editorial correspondence

The public repository contains code, public data, documentation, and paper assets. It does not contain reviewer correspondence, cover letters, marked manuscripts, or internal issue reports.

## P10. Prefer narrow claims that survive audit

A conservative, well-defined claim is more valuable than a broad claim that fails under inspection. RIEC-L1 is framed as a conflict-resolution layer, not as a universal selector.
