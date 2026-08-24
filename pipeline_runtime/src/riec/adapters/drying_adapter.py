"""Drying data adapter for Case III (thin-layer drying kinetics).

We expect a long-form CSV with at least:

- `t`           : time (same unit across rows, e.g. minutes)
- `MR`          : moisture ratio in [0, 1]
- `condition_id`: condition label used as the RIEC-L0 group

Optional (recommended):
- `T`           : air temperature (Celsius)
- `v`           : air velocity (m/s)

This adapter only standardizes column names and types. Computing MR from
raw moisture content is deliberately kept out of scope for this minimal
RINENG experiment scaffold.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd


def load_drying_long(path: str | Path) -> pd.DataFrame:
    """Load a drying dataset and return a standardized DataFrame."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(str(p))

    df = pd.read_csv(p)
    rename = {}
    # allow some common aliases
    if "time" in df.columns and "t" not in df.columns:
        rename["time"] = "t"
    if "mr" in df.columns and "MR" not in df.columns:
        rename["mr"] = "MR"
    if "condition" in df.columns and "condition_id" not in df.columns:
        rename["condition"] = "condition_id"
    df = df.rename(columns=rename)

    required = {"t", "MR", "condition_id"}
    if not required.issubset(set(df.columns)):
        raise ValueError(
            f"Drying CSV '{p.name}' must contain {sorted(required)}; got {df.columns.tolist()}"
        )

    out = df.copy()
    out["t"] = out["t"].astype(float)
    out["MR"] = out["MR"].astype(float)
    out["MR"] = out["MR"].clip(0.0, 1.0)
    out["condition_id"] = out["condition_id"].astype(str)

    # Provide a default temperature column if missing (needed by Arrhenius-tied models)
    if "T" not in out.columns:
        out["T"] = float(np.nan)
    else:
        out["T"] = out["T"].astype(float)

    # Sort for stable plotting
    out = out.sort_values(["condition_id", "t"], ascending=True).reset_index(drop=True)
    return out
