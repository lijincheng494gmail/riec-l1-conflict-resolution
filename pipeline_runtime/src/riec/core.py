"""
RIEC-L1 core utilities: BIC, CV risk, XPE, C_lambda, and selection.

This implementation is intentionally minimal and "engineering friendly":
- Uses squared loss and regression-style BIC computed from SSE.
- Uses GroupKFold splits to support leakage-aware evaluation (RIEC-L0).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Sequence, Tuple
import numpy as np
import pandas as pd


def bic_from_sse(sse: float, n: int, k: int, n_eff: int | None = None) -> float:
    """
    Regression-style BIC (up to an additive constant):

        BIC = n_eff * log(SSE / n_eff) + k * log(n_eff)

    where SSE = sum (y - yhat)^2.

    Notes:
    - If n_eff is None, use n.
    - This corresponds to Gaussian errors with unknown variance; constants are dropped.
    """
    if n_eff is None:
        n_eff = n
    n_eff = int(n_eff)
    if n_eff <= 0:
        raise ValueError("n_eff must be positive.")
    sse = float(sse)
    sse = max(sse, 1e-30)
    return float(n_eff * np.log(sse / n_eff) + k * np.log(n_eff))


def mse(y: np.ndarray, yhat: np.ndarray) -> float:
    return float(np.mean((y - yhat) ** 2))


def evaluate_model_on_indices(model, x: np.ndarray, y: np.ndarray, train_idx: np.ndarray, test_idx: np.ndarray) -> Tuple[float, float]:
    """
    Fit model on train split, return (test_mse, train_sse).
    """
    x_tr, y_tr = x[train_idx], y[train_idx]
    x_te, y_te = x[test_idx], y[test_idx]
    m = model.fit(x_tr, y_tr)
    yhat_te = m.predict(x_te)
    yhat_tr = m.predict(x_tr)
    test_mse = mse(y_te, yhat_te)
    train_sse = float(np.sum((y_tr - yhat_tr) ** 2))
    return test_mse, train_sse


@dataclass
class ModelScore:
    model_name: str
    k_params: int
    bic: float
    cv_risk: float
    xpe: float
    c_lambda: float


@dataclass(frozen=True)
class ModelSpec:
    """A factory-based model specification.

    Why this exists
    ---------------
    Many of your RIEC candidate models are not "default-constructible".
    For example, complexity levels often require explicit configuration
    (e.g. mixture size, polynomial degree, number of oscillators).

    Using a factory makes CV and full-data fits reproducible and removes the
    brittle assumption that we can always do `model.__class__()`.
    """

    name: str
    param_count: int
    factory: Callable[[], Any]


def _to_model_spec(model_like: Any) -> ModelSpec:
    """Convert a model instance or a ModelSpec into a ModelSpec."""
    if isinstance(model_like, ModelSpec):
        return model_like

    name = getattr(model_like, "name", model_like.__class__.__name__)
    k = int(getattr(model_like, "param_count", 0))

    def _factory() -> Any:
        m = model_like.__class__()
        # Make sure metadata is consistent even if the class defaults differ.
        try:
            m.name = name
        except Exception:
            pass
        try:
            m.param_count = k
        except Exception:
            pass
        return m

    return ModelSpec(name=str(name), param_count=int(k), factory=_factory)


def run_riec_selection(
    x: np.ndarray,
    y: np.ndarray,
    models: Sequence[Any],
    splits: Sequence[Tuple[np.ndarray, np.ndarray]],
    baseline_name: str,
    lambda_weight: float,
    n_eff: int | None = None,
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Evaluate all models and compute BIC, CV risk, XPE, and C_lambda.

    Parameters
    ----------
    x, y : arrays
    models : list of fitted-model objects (must implement fit/predict/name/param_count)
    splits : list of (train_idx, test_idx)
    baseline_name : which model is baseline for XPE
    lambda_weight : lambda value (already evaluated at n_eff)
    n_eff : effective sample size for BIC (optional)

    Returns
    -------
    scores_df : DataFrame sorted by C_lambda ascending
    picks : dict with keys ['bic_best','cv_best','riec_best']
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(y)

    # CV risk
    cv_risks = {}
    # For BIC we will fit on full data once
    bics = {}
    ks = {}

    model_specs = [_to_model_spec(m) for m in models]

    for spec in model_specs:
        name = spec.name
        k = int(spec.param_count)
        ks[name] = k

        fold_mse = []
        for train_idx, test_idx in splits:
            m = spec.factory()  # fresh instance each fold
            mse_te, _ = evaluate_model_on_indices(m, x, y, train_idx, test_idx)
            fold_mse.append(mse_te)
        cv_risks[name] = float(np.mean(fold_mse))

        # Full fit for BIC
        m_full = spec.factory()
        m_full.fit(x, y)
        yhat = m_full.predict(x)
        sse = float(np.sum((y - yhat) ** 2))
        bics[name] = bic_from_sse(sse, n=n, k=k, n_eff=n_eff)

    if baseline_name not in cv_risks:
        raise ValueError(f"baseline_name='{baseline_name}' not in models: {list(cv_risks.keys())}")

    base_cv = cv_risks[baseline_name]
    # stability guard
    base_cv = max(base_cv, 1e-30)

    rows = []
    for name in cv_risks:
        cv = max(cv_risks[name], 1e-30)
        xpe = base_cv / cv
        c_lam = bics[name] + lambda_weight * np.log(1.0 / xpe)
        rows.append(ModelScore(model_name=name, k_params=ks[name], bic=bics[name], cv_risk=cv, xpe=xpe, c_lambda=c_lam))

    df = pd.DataFrame([r.__dict__ for r in rows])
    # bests
    bic_best = df.sort_values("bic", ascending=True).iloc[0]["model_name"]
    cv_best = df.sort_values("cv_risk", ascending=True).iloc[0]["model_name"]
    riec_best = df.sort_values("c_lambda", ascending=True).iloc[0]["model_name"]

    df = df.sort_values("c_lambda", ascending=True).reset_index(drop=True)

    picks = {"bic_best": str(bic_best), "cv_best": str(cv_best), "riec_best": str(riec_best)}
    return df, picks
