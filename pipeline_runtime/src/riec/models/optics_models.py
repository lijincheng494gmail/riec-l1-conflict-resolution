"""Candidate models for Case I (optical thickness via spectral fitting).

The original optics workbench behind your HTML report contains a rich model
library (TMM, roughness, polarization, dispersion families...). For this
RINENG experiment package we implement a small, stable *proxy* family that:

1) is cheap to fit,
2) exposes a clear (C,f) complexity ladder, and
3) is sufficient to demonstrate RIEC-L1 model selection.

Model family
------------
We model a single-spectrum reflectance curve as:

    y(w) = P_f(w) + A cos(omega * w + phi)

where:
- w is the wavenumber axis,
- P_f is a polynomial baseline of degree f,
- (A, omega, phi) is a sinusoidal interference term.

The complexity level f controls only the baseline (not the sinusoid), giving
you a clean demonstration of: "does extra flexibility pay off out-of-fold?"

This is NOT a substitute for a full thin-film transfer-matrix model; it is a
lightweight, audit-able proxy to keep the code runnable on any machine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
from scipy import optimize


def _as_1d(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim != 1:
        raise ValueError("Optics models expect 1D x (wavenumber).")
    return x


def _poly_design(xn: np.ndarray, deg: int) -> np.ndarray:
    """Vandermonde design for polynomial baseline on a normalized axis."""
    return np.vander(xn, N=deg + 1, increasing=True)


def _guess_omega(w: np.ndarray, y: np.ndarray) -> float:
    """Crude frequency guess using FFT on a detrended spectrum."""
    w = np.asarray(w, dtype=float)
    y = np.asarray(y, dtype=float)
    n = w.size
    if n < 32:
        return 0.01
    # assume approximately uniform grid
    dw = float(np.median(np.diff(w)))
    if dw <= 0:
        return 0.01
    # detrend with a line
    p = np.polyfit(w, y, deg=1)
    y_det = y - np.polyval(p, w)
    y_det = y_det - np.mean(y_det)
    # FFT peak
    ft = np.fft.rfft(y_det)
    freqs = np.fft.rfftfreq(n, d=dw)
    # ignore zero frequency
    if freqs.size < 3:
        return 0.01
    idx = int(np.argmax(np.abs(ft[1:])) + 1)
    f0 = float(freqs[idx])
    omega0 = 2.0 * np.pi * f0
    # clamp to a safe range
    return float(np.clip(omega0, 1e-6, 0.2))


@dataclass
class CosinePolyModel:
    """Polynomial baseline + single cosine interference proxy."""

    deg: int = 0
    name: str = "cos_poly"
    param_count: int = 0

    # fitted parameters
    coef: np.ndarray | None = None  # polynomial coefficients (deg+1)
    A: float | None = None
    omega: float | None = None
    phi: float | None = None

    # normalization for numeric stability
    x0: float | None = None
    xs: float | None = None

    def __post_init__(self) -> None:
        self.deg = int(self.deg)
        if self.deg < 0:
            raise ValueError("deg must be >= 0")
        self.name = f"cos_poly_deg{self.deg}"
        # (deg+1) baseline + A + omega + phi
        self.param_count = int(self.deg + 4)

    def _normalize_x(self, w: np.ndarray) -> np.ndarray:
        if self.x0 is None or self.xs is None:
            raise RuntimeError("Model not initialized.")
        return (w - self.x0) / self.xs

    def _forward(self, w: np.ndarray, coef: np.ndarray, A: float, omega: float, phi: float) -> np.ndarray:
        w = _as_1d(w)
        xn = (w - self.x0) / self.xs
        Phi = _poly_design(xn, self.deg)
        base = Phi @ coef
        return base + A * np.cos(omega * w + phi)

    def fit(self, w: np.ndarray, y: np.ndarray) -> "CosinePolyModel":
        w = _as_1d(w)
        y = np.asarray(y, dtype=float)
        if y.shape != w.shape:
            raise ValueError("w and y must have the same shape")

        # numeric stabilization for polynomial
        self.x0 = float(np.mean(w))
        span = float(np.max(w) - np.min(w))
        self.xs = float(span if span > 0 else 1.0)
        xn = (w - self.x0) / self.xs

        # initial guesses
        coef0 = np.zeros(self.deg + 1, dtype=float)
        coef0[0] = float(np.mean(y))
        A0 = float(0.5 * (np.max(y) - np.min(y) + 1e-12))
        omega0 = _guess_omega(w, y)
        phi0 = 0.0
        p0 = np.concatenate([coef0, [A0, omega0, phi0]])

        # bounds: keep omega positive; phi within [-pi, pi]
        lower = np.full_like(p0, -np.inf)
        upper = np.full_like(p0, np.inf)
        lower[-2] = 1e-6  # omega
        upper[-2] = 0.5
        lower[-1] = -np.pi
        upper[-1] = np.pi

        def residual(p: np.ndarray) -> np.ndarray:
            coef = p[: self.deg + 1]
            A, omega, phi = p[-3], p[-2], p[-1]
            yhat = self._forward(w, coef, A, omega, phi)
            return (yhat - y)

        res = optimize.least_squares(
            residual,
            x0=p0,
            bounds=(lower, upper),
            max_nfev=20000,
        )
        p_hat = res.x
        self.coef = p_hat[: self.deg + 1]
        self.A = float(p_hat[-3])
        self.omega = float(p_hat[-2])
        self.phi = float(p_hat[-1])
        return self

    def predict(self, w: np.ndarray) -> np.ndarray:
        if self.coef is None or self.A is None or self.omega is None or self.phi is None:
            raise RuntimeError("Model not fitted.")
        w = _as_1d(w)
        return self._forward(w, self.coef, self.A, self.omega, self.phi)
