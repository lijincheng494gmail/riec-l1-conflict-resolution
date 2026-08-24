# From side-by-side inspection to conflict resolution

## Purpose

This note explains the central methodological move in RIEC-L1. The method does not claim that BIC and grouped CV are new. The contribution is the declared operation that turns their disagreement into a reproducible recommendation.

## What side-by-side inspection can do

A side-by-side table can show the analyst that two criteria disagree. For example:

```text
BIC-style signal: compact candidate
Grouped CV: flexible candidate
```

This is already valuable. It prevents the analyst from hiding a conflict behind a single number. The evidence ledger should always preserve this descriptive view.

## What side-by-side inspection cannot do

A table does not answer the decision question:

```text
How much grouped-CV improvement is enough to justify the additional structural cost?
```

If the analyst decides informally after seeing the table, the recommendation can become post-hoc. Another analyst could inspect the same table and make a different argument. That may be acceptable for exploratory work, but it is weak as a reproducible engineering decision protocol.

## RIEC-L1 as a declared operation

RIEC-L1 adds a pre-specified mapping:

```text
ledger -> conditional recommendation
```

The mapping is not meant to erase the ledger. The selected model is reported together with the score gaps and switching diagnostics. The decision can therefore be audited.

## Pairwise boundary

For two candidates `A` and `B`, with lower score preferred, RIEC-L1 selects `B` over `A` when:

```text
BIC_eff(B) - BIC_eff(A)
< lambda_n log[E_CV(A) / E_CV(B)]
```

The left side is the BIC-style cost gap. The right side is the grouped-CV gain expressed on the declared score scale.

This inequality is the operational answer to the side-by-side problem. It defines the amount of grouped-CV gain required for `B` to compensate for its structural cost relative to `A`.

## Why this is auditable

The decision is auditable because the analyst can report:

- which candidate won;
- how far each candidate is from the winner;
- the runner-up margin;
- which pairwise boundary would need to be crossed to change the decision;
- whether a reasonable range of `c` values changes the recommendation.

This does not prove that the winner is statistically superior. It makes the reasoning that led to the recommendation reproducible.

## Drying as an example of weak evidence

The drying case is not treated as proof that the selected compact class is superior to the flexible Midilli model. Instead, it illustrates weak-evidence disagreement. Grouped CV slightly favors a flexible candidate, but the paired fold checks are inconclusive and the declared RIEC-L1 boundary remains on the compact Page/Weibull-equivalent side under the default schedule.

The value of the method in such a case is not predictive dominance. The value is avoiding an undocumented post-hoc escalation to a more flexible model when the score boundary has not been crossed.
