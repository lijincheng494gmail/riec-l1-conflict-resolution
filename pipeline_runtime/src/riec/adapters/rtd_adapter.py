"""
RTD data adapter for Case II.

Raw inputs:
- data1.csv: columns [序号, 时间, 电导]
- data3.csv: columns [时间, 电导1, 电导2, 电导3]

We convert tracer response C(t) into an empirical RTD kernel E(t) by:
1) baseline subtraction
2) non-negativity clamp
3) normalization: E(t) = C(t) / integral(C(t) dt)

Output:
A long-form DataFrame with columns:
- t: time
- E: empirical RTD kernel value
- run_id: group label for L0 split (run-level holdout)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
import pandas as pd
def _trapz(y, x):
    """Compatibility wrapper for NumPy <2 vs 2.x (trapz -> trapezoid)."""
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    if hasattr(np, "trapz"):
        val = np.trapz(y, x)
    else:
        # NumPy 2.x: np.trapz removed, use trapezoid
        val = np.trapezoid(y, x)
    return float(val)


def compute_rtd_E(t: np.ndarray, c: np.ndarray, baseline_points: int = 50) -> np.ndarray:
    """
    Compute empirical RTD kernel E(t) from tracer response c(t).

    Parameters
    ----------
    t : array-like, time
    c : array-like, tracer response (conductivity)
    baseline_points : int, how many initial points to estimate baseline

    Returns
    -------
    E : ndarray, normalized RTD kernel (integral ~ 1)
    """
    t = np.asarray(t, dtype=float)
    c = np.asarray(c, dtype=float)

    if len(t) != len(c):
        raise ValueError("t and c must have same length.")
    if len(t) < baseline_points + 5:
        baseline_points = max(5, len(t) // 10)

    # baseline from the initial segment
    baseline = float(np.median(c[:baseline_points]))
    c_adj = c - baseline
    c_adj[c_adj < 0] = 0.0

    area = _trapz(c_adj, t)
    if not np.isfinite(area) or area <= 0:
        raise ValueError("Cannot normalize tracer response: integral is non-positive.")
    E = c_adj / area
    return E


def load_rtd_runs_long(path_data3: str) -> pd.DataFrame:
    """
    Load the 3-run dataset (data3.csv) and return a long-form DataFrame:
    columns: t, E, run_id
    """
    df = pd.read_csv(path_data3)
    # Expected: 时间, 电导1, 电导2, 电导3
    if "时间" not in df.columns:
        raise ValueError(f"Unexpected columns: {df.columns.tolist()}")
    t = df["时间"].to_numpy(dtype=float)

    run_cols = [c for c in df.columns if c != "时间"]
    if len(run_cols) < 1:
        raise ValueError("No run columns found in data3.csv")

    rows = []
    for j, col in enumerate(run_cols, start=1):
        c = df[col].to_numpy(dtype=float)
        E = compute_rtd_E(t, c)
        rows.append(pd.DataFrame({"t": t, "E": E, "run_id": f"run{j}"}))
    out = pd.concat(rows, ignore_index=True)
    return out
