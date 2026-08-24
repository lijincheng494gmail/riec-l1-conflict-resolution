# Problem origin and scope

## Purpose

This note records the problem framing that led to RIEC-L1. The important point is that the problem is not unrestricted model discovery. The target setting is finite-library engineering model selection, where a small number of interpretable candidates are already available and the analyst must justify whether additional structural flexibility is worth its cost.

## Starting point: finite engineering candidate libraries

Many engineering datasets are analyzed using candidate families that have already been accepted by a field or by a project team. In this package, the examples are optical spectra, residence-time-distribution curves, and thin-layer drying curves. In each case, the analyst does not need an arbitrary function class; they need a defensible choice among a finite list of candidates.

This finite-library framing changes the decision problem. A black-box search over a large model class asks: which function minimizes prediction error? A finite engineering library asks: when does a more flexible, less compact, or less interpretable candidate earn its additional structure under deployment-aligned evidence?

## Why grouped evaluation came first

The three examples are curve datasets. A row is not necessarily an independent deployment instance. Randomly splitting individual points from a curve can leak the same physical trajectory into both training and validation folds. That is why the evaluation layer uses whole-condition or whole-run holdouts:

- optics: material-angle conditions;
- RTD: complete tracer runs;
- drying: operating-condition curves.

This grouped split is the primary safeguard against curve-dependence leakage. Effective-sample-size calibration is not used as the main protection against leakage in the present benchmarks.

## Why side-by-side criteria were insufficient

After grouped risk is computed, standard criteria can disagree. A compact candidate can receive a better BIC-style structural signal, while a more flexible candidate can receive a slightly better grouped-CV risk. Reporting both values is useful, but it leaves the final action to the analyst. Different analysts may make different post-hoc decisions from the same table.

RIEC-L1 was designed to make the conflict resolution explicit. It does not hide BIC or grouped CV. It keeps them in the ledger and declares in advance how their disagreement will be converted into a recommendation.

## Scope of the current package

The package supports three one-dimensional engineering curve cases and a deterministic controlled audit based on the drying design. It does not establish general performance in high-dimensional adaptive model spaces, multi-output systems, fully Bayesian posterior comparison, or large automated model registries.

The contribution is operational and methodological: define the statistical objects, preserve the full ledger, apply a declared choice map, and report the resulting margins and boundaries.
