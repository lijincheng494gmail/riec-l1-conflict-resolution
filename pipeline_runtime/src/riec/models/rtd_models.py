"""
RTD candidate models for Case II.

We fit parametric densities E(t) to an empirical RTD kernel estimated from tracer response.
Fitting objective: least squares on E(t) (with optional weighting by dt).

Implemented models (working):
- GammaRTD (2-parameter gamma density)
- LogNormalRTD (2-parameter lognormal density)
- AxialDispersionRTD (open-open boundary axial dispersion, 2 parameters: tau, Pe)

Notes:
- These are sufficient to validate the experiment scaffold end-to-end.
- You can extend this file to add defect models (bypass/dead-zone/recycle) later.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple
import numpy as np
from scipy import optimize, stats


def _safe_trapz(y: np.ndarray, x: np.ndarray) -> float:
    """Numerically integrate with minimal safety guards.
    Compatible with NumPy 1.x (np.trapz) and NumPy 2.x (np.trapezoid).
    """
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    if y.size != x.size:
        raise ValueError("trapz: x and y must have the same length")
    if y.size < 2:
        # Degenerate case (should not happen for RTD curves)
        return float(0.0)

    # NumPy 1.x: np.trapz exists
    # NumPy 2.x: np.trapz removed, use np.trapezoid
    if hasattr(np, "trapz"):
        val = np.trapz(y, x)
    else:
        val = np.trapezoid(y, x)

    return float(val)


def _unique_grid(t: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return sorted unique t-grid and inverse map back to the original array.

    This is critical for robustness when the caller passes concatenated
    multi-run RTD points (repeated t values across runs). Using `np.unique`
    ensures the grid is strictly non-decreasing and compatible with trapz.
    """
    t = np.asarray(t, dtype=float)
    t_unique, inv = np.unique(t, return_inverse=True)
    return t_unique, inv


def _collapse_duplicates(t: np.ndarray, e: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Collapse duplicated time points by averaging E(t) over duplicates.

    Parameters
    ----------
    t : array-like
        Time points (may contain duplicates if multiple runs are concatenated).
    e : array-like
        RTD kernel values aligned with `t`.

    Returns
    -------
    t_unique : ndarray
        Sorted unique time grid.
    e_mean : ndarray
        Averaged values on the unique grid, renormalized to integrate to ~1.
    """
    t_unique, inv = _unique_grid(t)
    e = np.asarray(e, dtype=float)
    if e.size != inv.size:
        raise ValueError("collapse_duplicates: t and e must have same length")
    sums = np.bincount(inv, weights=e)
    counts = np.bincount(inv)
    counts = np.maximum(counts, 1)
    e_mean = sums / counts
    e_mean = np.clip(e_mean, 0.0, None)
    # Renormalize for numerical stability (mean of densities should integrate to 1)
    area = _safe_trapz(e_mean, t_unique)
    if np.isfinite(area) and area > 0:
        e_mean = e_mean / area
    return t_unique, e_mean


def _normalize_density(t: np.ndarray, e: np.ndarray) -> np.ndarray:
    area = _safe_trapz(e, t)
    if not np.isfinite(area) or area <= 0:
        raise ValueError("Density normalization failed: integral is non-positive.")
    return e / area


def _mse(y: np.ndarray, yhat: np.ndarray) -> float:
    return float(np.mean((y - yhat) ** 2))


@dataclass
class GammaRTD:
    """Gamma density E(t) with free shape a>0 and scale s>0."""
    name: str = "gamma_2p"
    param_count: int = 2
    a: float | None = None
    s: float | None = None

    def _pdf(self, t: np.ndarray, a: float, s: float) -> np.ndarray:
        # SciPy gamma uses 'a' as shape, scale=s
        e = stats.gamma.pdf(t, a=a, scale=s)
        e = np.nan_to_num(e, nan=0.0, posinf=0.0, neginf=0.0)
        return e

    def fit(self, t: np.ndarray, e: np.ndarray) -> "GammaRTD":
        # IMPORTANT: callers may pass concatenated multi-run points where `t`
        # contains duplicates (one copy per run). We collapse duplicates onto a
        # unique sorted grid to ensure all integrations are well-defined.
        t_u, e_u = _collapse_duplicates(t, e)

        # moment-based init on the unique grid
        mu = float(_safe_trapz(t_u * e_u, t_u))
        var = float(_safe_trapz(((t_u - mu) ** 2) * e_u, t_u))
        var = max(var, 1e-12)
        a0 = max(mu * mu / var, 1e-3)
        s0 = max(var / mu, 1e-6)

        def obj(p: np.ndarray) -> float:
            a, s = p
            if a <= 0 or s <= 0:
                return 1e18
            pred = self._pdf(t_u, a, s)
            pred = _normalize_density(t_u, pred)
            return _mse(e_u, pred)

        res = optimize.minimize(
            obj,
            x0=np.array([a0, s0]),
            method="Nelder-Mead",
            options={"maxiter": 5000, "xatol": 1e-10, "fatol": 1e-12},
        )
        a_hat, s_hat = res.x
        self.a = float(max(a_hat, 1e-9))
        self.s = float(max(s_hat, 1e-9))
        return self

    def predict(self, t: np.ndarray) -> np.ndarray:
        if self.a is None or self.s is None:
            raise RuntimeError("Model not fitted.")
        t_u, inv = _unique_grid(t)
        pred_u = self._pdf(t_u, self.a, self.s)
        pred_u = _normalize_density(t_u, pred_u)
        return pred_u[inv]


@dataclass
class LogNormalRTD:
    """Lognormal density E(t) with parameters mu (log-mean) and sigma>0."""
    name: str = "lognormal_2p"
    param_count: int = 2
    mu: float | None = None
    sigma: float | None = None

    def _pdf(self, t: np.ndarray, mu: float, sigma: float) -> np.ndarray:
        # SciPy lognorm parameterization: s=sigma, scale=exp(mu)
        e = stats.lognorm.pdf(t, s=sigma, scale=np.exp(mu))
        e = np.nan_to_num(e, nan=0.0, posinf=0.0, neginf=0.0)
        return e

    def fit(self, t: np.ndarray, e: np.ndarray) -> "LogNormalRTD":
        t_u, e_u = _collapse_duplicates(t, e)

        # moment-based init on the unique grid
        mu_t = float(_safe_trapz(t_u * e_u, t_u))
        var_t = float(_safe_trapz(((t_u - mu_t) ** 2) * e_u, t_u))
        var_t = max(var_t, 1e-12)
        sigma0 = float(np.sqrt(np.log(1.0 + var_t / (mu_t ** 2 + 1e-12))))
        mu0 = float(np.log(mu_t + 1e-12) - 0.5 * sigma0 ** 2)

        def obj(p: np.ndarray) -> float:
            mu, sigma = p
            if sigma <= 0:
                return 1e18
            pred = self._pdf(t_u, mu, sigma)
            pred = _normalize_density(t_u, pred)
            return _mse(e_u, pred)

        res = optimize.minimize(
            obj,
            x0=np.array([mu0, sigma0]),
            method="Nelder-Mead",
            options={"maxiter": 5000, "xatol": 1e-10, "fatol": 1e-12},
        )
        mu_hat, sigma_hat = res.x
        self.mu = float(mu_hat)
        self.sigma = float(max(sigma_hat, 1e-9))
        return self

    def predict(self, t: np.ndarray) -> np.ndarray:
        if self.mu is None or self.sigma is None:
            raise RuntimeError("Model not fitted.")
        t_u, inv = _unique_grid(t)
        pred_u = self._pdf(t_u, self.mu, self.sigma)
        pred_u = _normalize_density(t_u, pred_u)
        return pred_u[inv]


@dataclass
class AxialDispersionRTD:
    """
    Axial dispersion model (open-open boundaries), parameterized by:
    - tau: mean residence time (scale)
    - Pe: Peclet number (>0)
    """
    name: str = "axdisp_2p"
    param_count: int = 2
    tau: float | None = None
    pe: float | None = None

    def _pdf_theta(self, theta: np.ndarray, pe: float) -> np.ndarray:
        # open-open RTD in dimensionless time theta=t/tau
        # E(theta) = (1 / (2*sqrt(pi/Pe))) * theta^{-3/2} * exp(-Pe*(1-theta)^2/(4*theta))
        # valid for theta>0
        theta = np.asarray(theta, dtype=float)
        e = np.zeros_like(theta)
        mask = theta > 0
        th = theta[mask]
        pref = 1.0 / (2.0 * np.sqrt(np.pi / pe))
        e_val = pref * (th ** (-1.5)) * np.exp(-(pe * (1.0 - th) ** 2) / (4.0 * th))
        e[mask] = e_val
        e = np.nan_to_num(e, nan=0.0, posinf=0.0, neginf=0.0)
        return e

    def _pdf(self, t: np.ndarray, tau: float, pe: float) -> np.ndarray:
        theta = t / tau
        e_theta = self._pdf_theta(theta, pe)
        e = e_theta / tau
        return e

    def fit(self, t: np.ndarray, e: np.ndarray) -> "AxialDispersionRTD":
        t_u, e_u = _collapse_duplicates(t, e)

        # init: tau ~ mean, pe moderate
        tau0 = float(_safe_trapz(t_u * e_u, t_u))
        tau0 = max(tau0, 1e-6)
        pe0 = 10.0

        def obj(p: np.ndarray) -> float:
            tau, pe = p
            if tau <= 0 or pe <= 0:
                return 1e18
            pred = self._pdf(t_u, tau, pe)
            pred = _normalize_density(t_u, pred)
            return _mse(e_u, pred)

        res = optimize.minimize(
            obj,
            x0=np.array([tau0, pe0]),
            method="Nelder-Mead",
            options={"maxiter": 8000, "xatol": 1e-10, "fatol": 1e-12},
        )
        tau_hat, pe_hat = res.x
        self.tau = float(max(tau_hat, 1e-9))
        self.pe = float(max(pe_hat, 1e-9))
        return self

    def predict(self, t: np.ndarray) -> np.ndarray:
        if self.tau is None or self.pe is None:
            raise RuntimeError("Model not fitted.")
        t_u, inv = _unique_grid(t)
        pred_u = self._pdf(t_u, self.tau, self.pe)
        pred_u = _normalize_density(t_u, pred_u)
        return pred_u[inv]
