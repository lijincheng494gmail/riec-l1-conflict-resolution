"""Optics data adapter for Case I.

This project keeps the *model* logic decoupled from the *data* logic.
For optics spectra we standardize inputs into a long-form table:

Required columns
----------------
- `wavenumber`  : float, spectral axis (e.g., cm^-1)
- `reflectance` : float, measured reflectance/intensity (unitless)
- `condition_id`: str, group label for RIEC-L0 evaluation
                 (e.g., angle, measurement replicate, wafer id...)

Optional columns
----------------
- `angle_deg`   : float, for metadata only

Supported input layouts
-----------------------
1) A single CSV containing the required columns.
2) Multiple CSVs (one per condition). If `condition_id` is missing, we
   will use the filename stem as the condition id.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence

import numpy as np
import pandas as pd


def load_optics_long(paths: Sequence[str | Path]) -> pd.DataFrame:
    """Load one or more optics CSV files and return a standardized DataFrame."""
    if isinstance(paths, (str, Path)):
        paths = [paths]  # type: ignore[assignment]

    frames: List[pd.DataFrame] = []
    for p in paths:
        p = Path(p)
        if not p.exists():
            raise FileNotFoundError(str(p))
        df = pd.read_csv(p)

        # Normalize common column names
        rename = {}
        if "x" in df.columns and "wavenumber" not in df.columns:
            rename["x"] = "wavenumber"
        if "y" in df.columns and "reflectance" not in df.columns:
            rename["y"] = "reflectance"
        df = df.rename(columns=rename)

        required = {"wavenumber", "reflectance"}
        if not required.issubset(set(df.columns)):
            raise ValueError(
                f"Optics CSV '{p.name}' must contain {sorted(required)} (or x/y aliases); got {df.columns.tolist()}"
            )

        if "condition_id" not in df.columns:
            df = df.copy()
            df["condition_id"] = p.stem

        keep_cols = ["wavenumber", "reflectance", "condition_id"]
        if "angle_deg" in df.columns:
            keep_cols.append("angle_deg")

        out = df[keep_cols].copy()
        out["wavenumber"] = out["wavenumber"].astype(float)
        out["reflectance"] = out["reflectance"].astype(float)
        out["condition_id"] = out["condition_id"].astype(str)
        frames.append(out)

    data = pd.concat(frames, ignore_index=True)

    # Sort within each condition for nicer overlays
    data = data.sort_values(["condition_id", "wavenumber"], ascending=True).reset_index(drop=True)
    return data
