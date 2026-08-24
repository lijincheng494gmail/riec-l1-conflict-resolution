"""
Split helpers for RIEC-L0.

Currently supports:
- GroupKFold: leave-one-group-out style evaluation (prevents point-wise leakage).
"""
from __future__ import annotations

from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold


def make_group_splits(df: pd.DataFrame, group_col: str) -> List[Tuple[np.ndarray, np.ndarray]]:
    """
    Create GroupKFold splits where each group is held out once.

    Returns a list of (train_idx, test_idx) index arrays.
    """
    groups = df[group_col].to_numpy()
    unique_groups = np.unique(groups)
    n_splits = len(unique_groups)
    if n_splits < 2:
        raise ValueError(f"Need at least 2 groups for group CV; got {n_splits}")

    gkf = GroupKFold(n_splits=n_splits)
    X_dummy = np.zeros((len(df), 1))
    splits = []
    for tr, te in gkf.split(X_dummy, y=None, groups=groups):
        splits.append((tr, te))
    return splits
