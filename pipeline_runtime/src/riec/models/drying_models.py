"""Candidate models for Case III (thin-layer drying kinetics).

This file implements a small, canonical model library used widely in
thin-layer drying papers. The focus here is not to invent a new kinetics
model, but to demonstrate how RIEC-L1 selects an appropriate complexity
level given credible L0 evaluation.

We fit moisture ratio curves MR(t) with squared loss.

Data interface
--------------
The models accept `x` either as:

- 1D array: `t`
- 2D array: columns `[t, T]` (T in Celsius), needed for Arrhenius-tied models

Implemented families
--------------------
- Lewis (Newton): MR = exp(-k t)
- Page:           MR = exp(-k t^n)
- Midilli:        MR = a exp(-k t^n) + b t
- Two-term:       MR = a exp(-k1 t) + (1-a) exp(-k2 t)
- Weibull:        MR = exp(-(t/alpha)^beta)
- Arrhenius-Lewis: k(T)=k0 exp(-Ea/(R(T+273.15)))
- Arrhenius-Page:  same k(T) with free n

This set is enough to encode several (C,f) worldviews:
physics-leaning (Arrhenius-tied) vs purely empirical (Midilli) vs moderate (Page).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import optimize


def _split_xt(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return (t, T) from x.

    If x is 1D, T is returned as NaN array.
    If x is 2D, interpret columns as [t, T].
    """
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        t = x
        T = np.full_like(t, np.nan, dtype=float)
        return t, T
    if x.ndim == 2 and x.shape[1] >= 2:
        t = x[:, 0]
        T = x[:, 1]
        return t, T
    raise ValueError("Drying models expect x as 1D t or 2D [t, T].")


def _safe_exp(z: np.ndarray) -> np.ndarray:
    return np.exp(np.clip(z, -700.0, 700.0))


def _clip_mr(mr: np.ndarray) -> np.ndarray:
    return np.clip(mr, 0.0, 1.2)


def _k_init_from_curve(t: np.ndarray, mr: np.ndarray) -> float:
    """Crude k initializer using log-linear slope for MR in (0, 1]."""
    t = np.asarray(t, dtype=float)
    mr = np.asarray(mr, dtype=float)
    mask = (mr > 1e-6) & (mr <= 1.0) & (t > 0)
    if np.sum(mask) < 5:
        return 0.01
    y = np.log(mr[mask])
    x = t[mask]
    # slope ~ -k
    A = np.vstack([x, np.ones_like(x)]).T
    slope, _ = np.linalg.lstsq(A, y, rcond=None)[0]
    k = float(max(-slope, 1e-6))
    return k


def _mse(y: np.ndarray, yhat: np.ndarray) -> float:
    return float(np.mean((y - yhat) ** 2))


@dataclass
class LewisDrying:
    name: str = "lewis_1p"
    param_count: int = 1
    k: float | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> "LewisDrying":
        t, _ = _split_xt(x)
        y = np.asarray(y, dtype=float)
        k0 = _k_init_from_curve(t, y)

        def residual(p: np.ndarray) -> np.ndarray:
            k = p[0]
            if k <= 0:
                return 1e6 * np.ones_like(y)
            yhat = _safe_exp(-k * t)
            return yhat - y

        res = optimize.least_squares(residual, x0=np.array([k0]), bounds=(1e-9, np.inf), max_nfev=20000)
        self.k = float(res.x[0])
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        if self.k is None:
            raise RuntimeError("Model not fitted.")
        t, _ = _split_xt(x)
        return _clip_mr(_safe_exp(-self.k * t))


@dataclass
class PageDrying:
    name: str = "page_2p"
    param_count: int = 2
    k: float | None = None
    n: float | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> "PageDrying":
        t, _ = _split_xt(x)
        y = np.asarray(y, dtype=float)
        k0 = _k_init_from_curve(t, y)
        n0 = 1.0

        def residual(p: np.ndarray) -> np.ndarray:
            k, n = p
            if k <= 0 or n <= 0:
                return 1e6 * np.ones_like(y)
            yhat = _safe_exp(-k * (t ** n))
            return yhat - y

        res = optimize.least_squares(
            residual,
            x0=np.array([k0, n0]),
            bounds=(np.array([1e-9, 1e-6]), np.array([np.inf, 5.0])),
            max_nfev=30000,
        )
        self.k = float(res.x[0])
        self.n = float(res.x[1])
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        if self.k is None or self.n is None:
            raise RuntimeError("Model not fitted.")
        t, _ = _split_xt(x)
        return _clip_mr(_safe_exp(-self.k * (t ** self.n)))


@dataclass
class MidilliDrying:
    name: str = "midilli_4p"
    param_count: int = 4
    a: float | None = None
    k: float | None = None
    n: float | None = None
    b: float | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> "MidilliDrying":
        t, _ = _split_xt(x)
        y = np.asarray(y, dtype=float)
        k0 = _k_init_from_curve(t, y)
        p0 = np.array([1.0, k0, 1.0, 0.0])

        def residual(p: np.ndarray) -> np.ndarray:
            a, k, n, b = p
            if k <= 0 or n <= 0:
                return 1e6 * np.ones_like(y)
            yhat = a * _safe_exp(-k * (t ** n)) + b * t
            return yhat - y

        lower = np.array([0.0, 1e-9, 1e-6, -np.inf])
        upper = np.array([2.0, np.inf, 5.0, np.inf])
        res = optimize.least_squares(residual, x0=p0, bounds=(lower, upper), max_nfev=50000)
        self.a, self.k, self.n, self.b = (float(res.x[0]), float(res.x[1]), float(res.x[2]), float(res.x[3]))
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        if self.a is None or self.k is None or self.n is None or self.b is None:
            raise RuntimeError("Model not fitted.")
        t, _ = _split_xt(x)
        yhat = self.a * _safe_exp(-self.k * (t ** self.n)) + self.b * t
        return _clip_mr(yhat)


@dataclass
class TwoTermDrying:
    name: str = "two_term_3p"
    param_count: int = 3
    a: float | None = None
    k1: float | None = None
    k2: float | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> "TwoTermDrying":
        t, _ = _split_xt(x)
        y = np.asarray(y, dtype=float)
        k0 = _k_init_from_curve(t, y)
        p0 = np.array([0.5, k0, 2.0 * k0])

        def residual(p: np.ndarray) -> np.ndarray:
            a, k1, k2 = p
            if k1 <= 0 or k2 <= 0:
                return 1e6 * np.ones_like(y)
            yhat = a * _safe_exp(-k1 * t) + (1.0 - a) * _safe_exp(-k2 * t)
            return yhat - y

        lower = np.array([0.0, 1e-9, 1e-9])
        upper = np.array([1.0, np.inf, np.inf])
        res = optimize.least_squares(residual, x0=p0, bounds=(lower, upper), max_nfev=50000)
        self.a, self.k1, self.k2 = float(res.x[0]), float(res.x[1]), float(res.x[2])
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        if self.a is None or self.k1 is None or self.k2 is None:
            raise RuntimeError("Model not fitted.")
        t, _ = _split_xt(x)
        yhat = self.a * _safe_exp(-self.k1 * t) + (1.0 - self.a) * _safe_exp(-self.k2 * t)
        return _clip_mr(yhat)


@dataclass
class WeibullDrying:
    name: str = "weibull_2p"
    param_count: int = 2
    alpha: float | None = None
    beta: float | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> "WeibullDrying":
        t, _ = _split_xt(x)
        y = np.asarray(y, dtype=float)
        alpha0 = float(np.median(t[t > 0]) if np.any(t > 0) else 1.0)
        beta0 = 1.0

        def residual(p: np.ndarray) -> np.ndarray:
            alpha, beta = p
            if alpha <= 0 or beta <= 0:
                return 1e6 * np.ones_like(y)
            yhat = _safe_exp(-((t / alpha) ** beta))
            return yhat - y

        res = optimize.least_squares(
            residual,
            x0=np.array([alpha0, beta0]),
            bounds=(np.array([1e-9, 1e-6]), np.array([np.inf, 10.0])),
            max_nfev=30000,
        )
        self.alpha, self.beta = float(res.x[0]), float(res.x[1])
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        if self.alpha is None or self.beta is None:
            raise RuntimeError("Model not fitted.")
        t, _ = _split_xt(x)
        yhat = _safe_exp(-((t / self.alpha) ** self.beta))
        return _clip_mr(yhat)


def _arrhenius_k(T_c: np.ndarray, log_k0: float, Ea: float) -> np.ndarray:
    """k(T) with T in Celsius; Ea in J/mol."""
    R = 8.314
    T_k = T_c + 273.15
    return _safe_exp(log_k0 - Ea / (R * T_k))


@dataclass
class ArrheniusLewis:
    name: str = "arrhenius_lewis_2p"
    param_count: int = 2
    log_k0: float | None = None
    Ea: float | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> "ArrheniusLewis":
        t, T = _split_xt(x)
        y = np.asarray(y, dtype=float)
        # If T missing, fallback to a constant (still lets the model fit as a global Lewis)
        if np.all(np.isnan(T)):
            T = np.full_like(t, 25.0)

        k0_est = _k_init_from_curve(t, y)
        logk0_0 = float(np.log(max(k0_est, 1e-9)))
        Ea0 = 15000.0  # J/mol

        def residual(p: np.ndarray) -> np.ndarray:
            logk0, Ea = p
            if Ea <= 0:
                return 1e6 * np.ones_like(y)
            k = _arrhenius_k(T, logk0, Ea)
            yhat = _safe_exp(-k * t)
            return yhat - y

        lower = np.array([-50.0, 1e-6])
        upper = np.array([50.0, 200000.0])
        res = optimize.least_squares(residual, x0=np.array([logk0_0, Ea0]), bounds=(lower, upper), max_nfev=50000)
        self.log_k0, self.Ea = float(res.x[0]), float(res.x[1])
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        if self.log_k0 is None or self.Ea is None:
            raise RuntimeError("Model not fitted.")
        t, T = _split_xt(x)
        if np.all(np.isnan(T)):
            T = np.full_like(t, 25.0)
        k = _arrhenius_k(T, self.log_k0, self.Ea)
        return _clip_mr(_safe_exp(-k * t))


@dataclass
class ArrheniusPage:
    name: str = "arrhenius_page_3p"
    param_count: int = 3
    log_k0: float | None = None
    Ea: float | None = None
    n: float | None = None

    def fit(self, x: np.ndarray, y: np.ndarray) -> "ArrheniusPage":
        t, T = _split_xt(x)
        y = np.asarray(y, dtype=float)
        if np.all(np.isnan(T)):
            T = np.full_like(t, 25.0)

        k0_est = _k_init_from_curve(t, y)
        logk0_0 = float(np.log(max(k0_est, 1e-9)))
        Ea0 = 15000.0
        n0 = 1.0

        def residual(p: np.ndarray) -> np.ndarray:
            logk0, Ea, n = p
            if Ea <= 0 or n <= 0:
                return 1e6 * np.ones_like(y)
            k = _arrhenius_k(T, logk0, Ea)
            yhat = _safe_exp(-k * (t ** n))
            return yhat - y

        lower = np.array([-50.0, 1e-6, 1e-6])
        upper = np.array([50.0, 200000.0, 5.0])
        res = optimize.least_squares(residual, x0=np.array([logk0_0, Ea0, n0]), bounds=(lower, upper), max_nfev=80000)
        self.log_k0, self.Ea, self.n = float(res.x[0]), float(res.x[1]), float(res.x[2])
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        if self.log_k0 is None or self.Ea is None or self.n is None:
            raise RuntimeError("Model not fitted.")
        t, T = _split_xt(x)
        if np.all(np.isnan(T)):
            T = np.full_like(t, 25.0)
        k = _arrhenius_k(T, self.log_k0, self.Ea)
        return _clip_mr(_safe_exp(-k * (t ** self.n)))
