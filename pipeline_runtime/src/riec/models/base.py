"""
Minimal model interface for RIEC-L1 experiments.

All candidate models must implement:
- fit(x, y): returns self
- predict(x): returns y_hat
- param_count: int

Optionally:
- name: str
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
import numpy as np


class BaseModel(Protocol):
    name: str
    param_count: int

    def fit(self, x: np.ndarray, y: np.ndarray) -> "BaseModel":
        ...

    def predict(self, x: np.ndarray) -> np.ndarray:
        ...
