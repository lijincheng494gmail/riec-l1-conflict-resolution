"""Controlled conflict-resolution audit for the ARRAY editor check.

Purpose
-------
This script adds a *behavioral* audit, not a new empirical benchmark.  It is
intended to answer the editor's question: what does RIEC-L1 add beyond putting
BIC and grouped CV side by side?

The audit anchors synthetic grouped curves to the real drying benchmark.  It
fits the compact Page model and the flexible Midilli model on the original
Drying design grid, then uses their fitted difference as a shape-departure
template:

    mu_i(alpha) = yhat_page_i + alpha * (yhat_midilli_i - yhat_page_i)

alpha therefore controls the strength of the flexible component relative to the
observed Page-vs-Midilli difference in the actual drying case.  For each
(alpha, noise) setting, grouped curves are regenerated, the core drying library
is evaluated under leave-one-condition-out CV, and BIC / grouped CV / RIEC
selection frequencies and conflict margins are reported.

What this audit DOES claim
--------------------------
- RIEC-L1 provides a pre-specified conflict-resolution operation over familiar
  evidence components.
- The operation can be audited through a margin:

      margin = [BIC_eff(flexible) - BIC_eff(compact)]
               - lambda_n * log[CV(compact) / CV(flexible)]

  margin > 0 keeps the compact side; margin < 0 crosses to the flexible side.

What this audit does NOT claim
------------------------------
- It does not prove RIEC-L1 is predictively superior to BIC, CV, or any model.
- It does not establish Page as statistically superior to Midilli in the real
  drying benchmark.
- It does not derive lambda_n as an oracle-optimal schedule.

Typical usage from 03_analysis_code/pipeline_runtime:

    python scripts/revision_controlled_conflict_audit.py --replicates 0
    python scripts/revision_controlled_conflict_audit.py --replicates 20

Outputs are written by default to:

    ../../05_results_workspace/revision_experiments/arrays_editor_check_YYYY-MM-DD/controlled_conflict_audit/
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

RUNTIME_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RUNTIME_ROOT / "src"))

from riec.adapters.drying_adapter import load_drying_long
from riec.cv import make_group_splits
from riec.core import bic_from_sse, mse
from riec.models.drying_models import (
    LewisDrying,
    PageDrying,
    MidilliDrying,
    TwoTermDrying,
    WeibullDrying,
)


@dataclass(frozen=True)
class Candidate:
    name: str
    k: int
    factory: object
    side: str  # compact or flexible


def _parse_float_list(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def _load_drying_data() -> pd.DataFrame:
    raw = RUNTIME_ROOT / "data/raw/drying/drying_curves.csv"
    demo = RUNTIME_ROOT / "data/demo/drying_demo.csv"
    if raw.exists():
        return load_drying_long(raw)
    if demo.exists():
        return load_drying_long(demo)
    raise FileNotFoundError("No drying_curves.csv or drying_demo.csv found.")


def _x_from_df(df: pd.DataFrame) -> np.ndarray:
    return np.column_stack([df["t"].to_numpy(float), df["T"].to_numpy(float)])


def _candidate_library() -> list[Candidate]:
    """Core drying library for the controlled audit.

    Arrhenius-tied candidates are excluded here because the audit is a
    Page-to-Midilli shape-departure analysis, not a temperature-coupling audit.
    The full empirical drying table still reports the Arrhenius candidates.
    """
    return [
        Candidate("lewis_1p", 1, LewisDrying, "compact"),
        Candidate("page_2p", 2, PageDrying, "compact"),
        Candidate("weibull_2p", 2, WeibullDrying, "compact"),
        Candidate("two_term_3p", 3, TwoTermDrying, "flexible"),
        Candidate("midilli_4p", 4, MidilliDrying, "flexible"),
    ]


def _fit_predict(candidate_cls, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    m = candidate_cls().fit(x, y)
    return m.predict(x)


def _safe_aicc(aic: float, n: int, k: int) -> float:
    denom = n - k - 1
    if denom <= 0:
        return float("inf")
    return float(aic + (2 * k * (k + 1)) / denom)


def evaluate_library(
    df: pd.DataFrame,
    y: np.ndarray,
    candidates: list[Candidate],
    splits: list[tuple[np.ndarray, np.ndarray]],
    n_eff: int,
    lambda_weight: float,
    baseline_name: str = "lewis_1p",
) -> pd.DataFrame:
    """Evaluate candidates on one generated dataset."""
    x = _x_from_df(df)
    n = len(y)

    rows = []
    for cand in candidates:
        # Full fit for SSE, AIC, AICc, BIC_eff.
        model_full = cand.factory().fit(x, y)
        yhat_full = model_full.predict(x)
        sse = float(np.sum((y - yhat_full) ** 2))
        sse_guard = max(sse, 1e-30)
        aic = float(n * np.log(sse_guard / n) + 2 * cand.k)
        aicc = _safe_aicc(aic, n=n, k=cand.k)
        bic = bic_from_sse(sse, n=n, k=cand.k, n_eff=n_eff)

        # Grouped CV risk.
        fold_mse = []
        for train_idx, test_idx in splits:
            model_fold = cand.factory().fit(x[train_idx], y[train_idx])
            yhat_te = model_fold.predict(x[test_idx])
            fold_mse.append(mse(y[test_idx], yhat_te))
        cv_risk = float(np.mean(fold_mse))

        rows.append(
            {
                "model_name": cand.name,
                "side": cand.side,
                "k_params": cand.k,
                "sse": sse,
                "aic": aic,
                "aicc": aicc,
                "bic": bic,
                "cv_risk": cv_risk,
            }
        )

    out = pd.DataFrame(rows)
    baseline_cv = float(out.loc[out["model_name"] == baseline_name, "cv_risk"].iloc[0])
    baseline_cv = max(baseline_cv, 1e-30)
    out["xpe"] = baseline_cv / out["cv_risk"].clip(lower=1e-30)
    out["c_lambda"] = out["bic"] - lambda_weight * np.log(out["xpe"].clip(lower=1e-30))
    return out


def _winner(metrics: pd.DataFrame, criterion: str) -> str:
    if criterion == "cv_risk":
        return str(metrics.sort_values(criterion, ascending=True).iloc[0]["model_name"])
    return str(metrics.sort_values(criterion, ascending=True).iloc[0]["model_name"])


def _side_of(model_name: str, candidates: list[Candidate]) -> str:
    for c in candidates:
        if c.name == model_name:
            return c.side
    raise KeyError(model_name)


def _best_side_row(metrics: pd.DataFrame, side: str) -> pd.Series:
    return metrics[metrics["side"] == side].sort_values("c_lambda", ascending=True).iloc[0]


def _compact_flexible_margin(metrics: pd.DataFrame, lambda_weight: float) -> dict:
    """Return the RIEC conflict margin between best compact and best flexible.

    margin > 0: compact side wins under the declared RIEC score.
    margin < 0: flexible side wins under the declared RIEC score.
    """
    compact = _best_side_row(metrics, "compact")
    flexible = _best_side_row(metrics, "flexible")
    cv_compact = max(float(compact["cv_risk"]), 1e-30)
    cv_flexible = max(float(flexible["cv_risk"]), 1e-30)
    bic_gap = float(flexible["bic"] - compact["bic"])
    log_cv_gain = float(np.log(cv_compact / cv_flexible))
    margin = float(bic_gap - lambda_weight * log_cv_gain)
    return {
        "best_compact_model": str(compact["model_name"]),
        "best_flexible_model": str(flexible["model_name"]),
        "best_compact_bic": float(compact["bic"]),
        "best_flexible_bic": float(flexible["bic"]),
        "best_compact_cv_risk": cv_compact,
        "best_flexible_cv_risk": cv_flexible,
        "bic_gap_flexible_minus_compact": bic_gap,
        "log_cv_gain_flexible_over_compact": log_cv_gain,
        "lambda_times_log_cv_gain": float(lambda_weight * log_cv_gain),
        "riec_conflict_margin": margin,
        "margin_rule_selected_side": "flexible" if margin < 0 else "compact",
    }


def _selection_frequencies(all_runs: pd.DataFrame, model_names: list[str]) -> pd.DataFrame:
    records = []
    criteria = {
        "BIC": "bic_best",
        "Grouped CV": "cv_best",
        "RIEC-L1": "riec_best",
    }
    for (alpha, noise_scale), grp in all_runs.groupby(["alpha", "noise_scale"]):
        n = len(grp)
        for crit_label, col in criteria.items():
            counts = grp[col].value_counts().to_dict()
            row = {"alpha": alpha, "noise_scale": noise_scale, "criterion": crit_label, "n_replicates": n}
            for m in model_names:
                row[m] = counts.get(m, 0) / n
            records.append(row)
    return pd.DataFrame(records).sort_values(["noise_scale", "alpha", "criterion"]).reset_index(drop=True)


def _summary_table(all_runs: pd.DataFrame) -> pd.DataFrame:
    records = []
    for (alpha, noise_scale), grp in all_runs.groupby(["alpha", "noise_scale"]):
        n = len(grp)
        records.append(
            {
                "alpha": alpha,
                "noise_scale": noise_scale,
                "n_replicates": n,
                "bic_cv_disagreement_rate": float(np.mean(grp["bic_best"] != grp["cv_best"])),
                "riec_matches_bic_rate": float(np.mean(grp["riec_best"] == grp["bic_best"])),
                "riec_matches_grouped_cv_rate": float(np.mean(grp["riec_best"] == grp["cv_best"])),
                "riec_compact_side_rate": float(np.mean(grp["riec_side"] == "compact")),
                "riec_flexible_side_rate": float(np.mean(grp["riec_side"] == "flexible")),
                "bic_flexible_side_rate": float(np.mean(grp["bic_side"] == "flexible")),
                "cv_flexible_side_rate": float(np.mean(grp["cv_side"] == "flexible")),
                "median_riec_conflict_margin": float(np.median(grp["riec_conflict_margin"])),
            }
        )
    return pd.DataFrame(records).sort_values(["noise_scale", "alpha"]).reset_index(drop=True)


def _margin_table(all_runs: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "bic_gap_flexible_minus_compact",
        "log_cv_gain_flexible_over_compact",
        "lambda_times_log_cv_gain",
        "riec_conflict_margin",
    ]
    records = []
    for (alpha, noise_scale), grp in all_runs.groupby(["alpha", "noise_scale"]):
        row = {"alpha": alpha, "noise_scale": noise_scale, "n_replicates": len(grp)}
        for c in cols:
            row[f"median_{c}"] = float(np.median(grp[c]))
            row[f"q25_{c}"] = float(np.quantile(grp[c], 0.25))
            row[f"q75_{c}"] = float(np.quantile(grp[c], 0.75))
        records.append(row)
    return pd.DataFrame(records).sort_values(["noise_scale", "alpha"]).reset_index(drop=True)



def _deterministic_scan(
    df: pd.DataFrame,
    yhat_page: np.ndarray,
    shape_delta: np.ndarray,
    residual_template: np.ndarray,
    candidates: list[Candidate],
    splits: list[tuple[np.ndarray, np.ndarray]],
    alpha_grid: list[float],
    n_eff: int,
    lambda_weight: float,
) -> pd.DataFrame:
    """Residual-anchored Page-to-Midilli alpha sweep.

    This scan is very fast and avoids the artifact of noiseless curves, where
    a flexible model can obtain near-zero SSE. The original Page residuals are
    kept as a fixed noise template, while alpha controls the strength of the
    Page-to-Midilli shape departure. At alpha=0 the scan recovers the observed
    drying response on the original design grid.
    """
    rows = []
    for alpha in alpha_grid:
        y_det = np.clip(yhat_page + alpha * shape_delta + residual_template, 0.0, 1.0)
        metrics = evaluate_library(df, y_det, candidates, splits, n_eff=n_eff, lambda_weight=lambda_weight)
        bic_best = _winner(metrics, "bic")
        cv_best = _winner(metrics, "cv_risk")
        riec_best = _winner(metrics, "c_lambda")
        margin = _compact_flexible_margin(metrics, lambda_weight=lambda_weight)
        row = {
            "alpha": alpha,
            "bic_best": bic_best,
            "cv_best": cv_best,
            "riec_best": riec_best,
            "bic_side": _side_of(bic_best, candidates),
            "cv_side": _side_of(cv_best, candidates),
            "riec_side": _side_of(riec_best, candidates),
        }
        row.update(margin)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("alpha").reset_index(drop=True)


def _plot_deterministic_scan(det: pd.DataFrame, out_pdf: Path, out_png: Path) -> None:
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(det["alpha"], det["riec_conflict_margin"], marker="o", label="RIEC compact-vs-flexible margin")
    ax.axhline(0.0, linestyle="--", linewidth=0.9, label="decision boundary")
    ax.set_xlabel("alpha: Page-to-Midilli departure strength")
    ax.set_ylabel("margin; >0 compact, <0 flexible")
    ax.set_title("Residual-anchored Page-to-Midilli conflict-boundary scan")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def _plot_selection_rates(summary: pd.DataFrame, out_pdf: Path, out_png: Path) -> None:
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    noise_levels = list(summary["noise_scale"].drop_duplicates().sort_values())
    fig, axes = plt.subplots(1, len(noise_levels), figsize=(5 * len(noise_levels), 4), sharey=True)
    if len(noise_levels) == 1:
        axes = [axes]
    for ax, ns in zip(axes, noise_levels):
        sub = summary[summary["noise_scale"] == ns].sort_values("alpha")
        ax.plot(sub["alpha"], sub["bic_flexible_side_rate"], marker="o", label="BIC flexible-side rate")
        ax.plot(sub["alpha"], sub["cv_flexible_side_rate"], marker="o", label="Grouped CV flexible-side rate")
        ax.plot(sub["alpha"], sub["riec_flexible_side_rate"], marker="o", label="RIEC-L1 flexible-side rate")
        ax.axhline(0.5, linestyle="--", linewidth=0.8)
        ax.set_title(f"noise scale = {ns:g}")
        ax.set_xlabel("alpha: Page-to-Midilli departure strength")
        ax.set_ylim(-0.02, 1.02)
        ax.grid(True, alpha=0.25)
    axes[0].set_ylabel("selection rate for flexible side")
    axes[-1].legend(loc="best", fontsize=8)
    fig.suptitle("Controlled conflict-resolution audit")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def _plot_margin_rates(summary: pd.DataFrame, out_pdf: Path, out_png: Path) -> None:
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    noise_levels = list(summary["noise_scale"].drop_duplicates().sort_values())
    fig, axes = plt.subplots(1, len(noise_levels), figsize=(5 * len(noise_levels), 4), sharey=False)
    if len(noise_levels) == 1:
        axes = [axes]
    for ax, ns in zip(axes, noise_levels):
        sub = summary[summary["noise_scale"] == ns].sort_values("alpha")
        ax.plot(sub["alpha"], sub["median_riec_conflict_margin"], marker="o", label="median RIEC margin")
        ax.axhline(0.0, linestyle="--", linewidth=0.8)
        ax.set_title(f"noise scale = {ns:g}")
        ax.set_xlabel("alpha")
        ax.grid(True, alpha=0.25)
    axes[0].set_ylabel("median margin; >0 compact, <0 flexible")
    fig.suptitle("RIEC compact-vs-flexible conflict margin")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)


def _write_summary_md(
    path: Path,
    args: argparse.Namespace,
    n_eff: int,
    lambda_weight: float,
    base_noise_sd: float,
    real_margin: dict,
    deterministic: pd.DataFrame,
    summary: pd.DataFrame,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# Controlled conflict-resolution audit summary")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This audit is a behavioral check of RIEC-L1 as a pre-specified conflict-resolution operation. "
        "It is not a fourth empirical benchmark and it is not evidence of universal predictive superiority."
    )
    lines.append("")
    lines.append("## Design")
    lines.append("")
    lines.append(f"- Replicates per alpha/noise setting: `{args.replicates}`")
    lines.append(f"- Alpha grid: `{args.alpha_grid}`")
    lines.append(f"- Noise-scale grid: `{args.noise_scales}`")
    lines.append(f"- Base seed: `{args.seed}`")
    lines.append(f"- n_eff: `{n_eff}`")
    lines.append(f"- lambda_n: `{lambda_weight:.6f}`")
    lines.append(f"- empirical Page residual SD: `{base_noise_sd:.6g}`")
    lines.append("")
    lines.append("## Real drying Page-vs-Midilli conflict margin")
    lines.append("")
    for k, v in real_margin.items():
        if isinstance(v, float):
            lines.append(f"- `{k}`: `{v:.6g}`")
        else:
            lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("Interpretation: a positive RIEC conflict margin keeps the compact side; a negative margin crosses to the flexible side.")
    lines.append("")
    lines.append("## Deterministic alpha scan")
    lines.append("")
    lines.append(deterministic.to_string(index=False))
    lines.append("")
    if not summary.empty:
        lines.append("## Stochastic compact summary table")
        lines.append("")
        lines.append(summary.to_string(index=False))
        lines.append("")
    else:
        lines.append("## Stochastic compact summary table")
        lines.append("")
        lines.append("No stochastic replicates were requested. Re-run with `--replicates N` to generate selection-frequency tables.")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def run_audit(args: argparse.Namespace) -> Path:
    out_dir = Path(args.out_dir) if args.out_dir else PROJECT_ROOT / "05_results_workspace/revision_experiments" / args.revision_label / "controlled_conflict_audit"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    df = _load_drying_data()
    x = _x_from_df(df)
    y_real = df["MR"].to_numpy(float)
    groups = df["condition_id"].to_numpy(str)
    splits = make_group_splits(df, "condition_id")
    candidates = _candidate_library()
    model_names = [c.name for c in candidates]

    # Fit Page and Midilli templates on the real drying design grid.
    yhat_page = _fit_predict(PageDrying, x, y_real)
    yhat_midilli = _fit_predict(MidilliDrying, x, y_real)
    shape_delta = yhat_midilli - yhat_page
    page_resid = y_real - yhat_page
    base_noise_sd = float(np.std(page_resid, ddof=1))
    base_noise_sd = max(base_noise_sd, 1e-6)

    n_eff = len(df)
    lambda_weight = 1.0 / math.log(max(n_eff, 3))

    # Record the actual observed drying margin for interpretability.
    real_metrics = evaluate_library(df, y_real, candidates, splits, n_eff=n_eff, lambda_weight=lambda_weight)
    real_margin = _compact_flexible_margin(real_metrics, lambda_weight=lambda_weight)
    real_metrics.to_csv(out_dir / "real_drying_core_library_metrics.csv", index=False)

    alpha_grid = _parse_float_list(args.alpha_grid)
    noise_scales = _parse_float_list(args.noise_scales)

    deterministic = _deterministic_scan(
        df=df,
        yhat_page=yhat_page,
        shape_delta=shape_delta,
        residual_template=page_resid,
        candidates=candidates,
        splits=splits,
        alpha_grid=alpha_grid,
        n_eff=n_eff,
        lambda_weight=lambda_weight,
    )
    deterministic.to_csv(out_dir / "controlled_conflict_deterministic_alpha_scan.csv", index=False)
    _plot_deterministic_scan(
        deterministic,
        fig_dir / "Supplementary_Figure_S3_Deterministic_Conflict_Boundary.pdf",
        fig_dir / "Supplementary_Figure_S3_Deterministic_Conflict_Boundary.png",
    )

    rng_master = np.random.default_rng(args.seed)
    run_rows = []
    metrics_rows = []
    if args.replicates > 0:
        print(f"[Audit] Running stochastic audit: {len(alpha_grid)} alpha values × {len(noise_scales)} noise levels × {args.replicates} replicates")
    else:
        print("[Audit] Replicates set to 0: deterministic alpha scan only.")

    for alpha in alpha_grid if args.replicates > 0 else []:
        mu = np.clip(yhat_page + alpha * shape_delta, 0.0, 1.0)
        for noise_scale in noise_scales:
            sigma = float(noise_scale * base_noise_sd)
            tau = float(args.group_noise_fraction * sigma)
            for rep in range(args.replicates):
                # Derive a stable independent seed for each run.
                run_seed = int(rng_master.integers(0, 2**31 - 1))
                rng = np.random.default_rng(run_seed)
                group_offsets = {g: rng.normal(0.0, tau) for g in np.unique(groups)}
                point_noise = rng.normal(0.0, sigma, size=len(mu))
                y_star = mu + point_noise + np.array([group_offsets[g] for g in groups], dtype=float)
                y_star = np.clip(y_star, 0.0, 1.0)

                metrics = evaluate_library(df, y_star, candidates, splits, n_eff=n_eff, lambda_weight=lambda_weight)
                bic_best = _winner(metrics, "bic")
                cv_best = _winner(metrics, "cv_risk")
                riec_best = _winner(metrics, "c_lambda")
                margin = _compact_flexible_margin(metrics, lambda_weight=lambda_weight)

                row = {
                    "alpha": alpha,
                    "noise_scale": noise_scale,
                    "replicate": rep,
                    "seed": run_seed,
                    "sigma": sigma,
                    "tau": tau,
                    "bic_best": bic_best,
                    "cv_best": cv_best,
                    "riec_best": riec_best,
                    "bic_side": _side_of(bic_best, candidates),
                    "cv_side": _side_of(cv_best, candidates),
                    "riec_side": _side_of(riec_best, candidates),
                }
                row.update(margin)
                run_rows.append(row)

                if args.save_metrics_long:
                    tmp = metrics.copy()
                    tmp.insert(0, "replicate", rep)
                    tmp.insert(0, "noise_scale", noise_scale)
                    tmp.insert(0, "alpha", alpha)
                    metrics_rows.append(tmp)

    if run_rows:
        all_runs = pd.DataFrame(run_rows)
        freq = _selection_frequencies(all_runs, model_names)
        summary = _summary_table(all_runs)
        margins = _margin_table(all_runs)

        all_runs.to_csv(out_dir / "controlled_conflict_all_runs.csv", index=False)
        freq.to_csv(out_dir / "controlled_conflict_selection_frequencies.csv", index=False)
        summary.to_csv(out_dir / "controlled_conflict_summary.csv", index=False)
        margins.to_csv(out_dir / "controlled_conflict_margins.csv", index=False)
        if args.save_metrics_long and metrics_rows:
            pd.concat(metrics_rows, ignore_index=True).to_csv(out_dir / "controlled_conflict_metrics_long.csv", index=False)

        _plot_selection_rates(
            summary,
            fig_dir / "Supplementary_Figure_S4_Stochastic_Selection_Rates.pdf",
            fig_dir / "Supplementary_Figure_S4_Stochastic_Selection_Rates.png",
        )
        _plot_margin_rates(
            summary,
            fig_dir / "Supplementary_Figure_S5_Stochastic_RIEC_Margins.pdf",
            fig_dir / "Supplementary_Figure_S5_Stochastic_RIEC_Margins.png",
        )
    else:
        all_runs = pd.DataFrame()
        freq = pd.DataFrame()
        summary = pd.DataFrame()
        margins = pd.DataFrame()

    _write_summary_md(
        out_dir / "CONTROLLED_CONFLICT_AUDIT_SUMMARY.md",
        args=args,
        n_eff=n_eff,
        lambda_weight=lambda_weight,
        base_noise_sd=base_noise_sd,
        real_margin=real_margin,
        deterministic=deterministic,
        summary=summary,
    )

    manifest = {
        "purpose": "Controlled conflict-resolution audit for ARRAY editor check",
        "replicates": args.replicates,
        "alpha_grid": alpha_grid,
        "noise_scales": noise_scales,
        "seed": args.seed,
        "n_eff": n_eff,
        "lambda_weight": lambda_weight,
        "baseline": "lewis_1p",
        "compact_side": ["lewis_1p", "page_2p", "weibull_2p"],
        "flexible_side": ["two_term_3p", "midilli_4p"],
        "outputs": [str(p.relative_to(out_dir)) for p in sorted(out_dir.rglob("*")) if p.is_file()],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return out_dir


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run controlled conflict-resolution audit for RIEC-L1 revision.")
    p.add_argument("--replicates", type=int, default=0, help="Stochastic replicates per alpha/noise setting. Use 0 for deterministic alpha-scan only, 3-10 for smoke test, 20+ for stronger audit.")
    p.add_argument("--alpha-grid", default="0,0.05,0.1,0.15,0.2,0.25,0.5,1,2", help="Comma-separated Page-to-Midilli departure strengths.")
    p.add_argument("--noise-scales", default="0.5,1.0,1.5", help="Comma-separated multiples of empirical Page residual SD.")
    p.add_argument("--group-noise-fraction", type=float, default=0.25, help="Condition-level noise SD as fraction of point noise SD.")
    p.add_argument("--seed", type=int, default=20260512, help="Base random seed.")
    p.add_argument("--revision-label", default="arrays_editor_check_2026-05-13", help="Output subfolder under 05_results_workspace/revision_experiments.")
    p.add_argument("--out-dir", default=None, help="Optional explicit output folder.")
    p.add_argument("--save-metrics-long", action="store_true", help="Also save per-run per-model metrics; larger but useful for debugging.")
    return p


def main() -> int:
    args = build_arg_parser().parse_args()
    if args.replicates < 0:
        raise ValueError("--replicates must be non-negative")
    out_dir = run_audit(args)
    print("\n[Controlled conflict-resolution audit] Done.")
    print(f"Outputs: {out_dir}")
    print("Key files:")
    for name in [
        "CONTROLLED_CONFLICT_AUDIT_SUMMARY.md",
        "controlled_conflict_deterministic_alpha_scan.csv",
        "figures/Supplementary_Figure_S3_Deterministic_Conflict_Boundary.pdf",
        "controlled_conflict_summary.csv",
        "controlled_conflict_selection_frequencies.csv",
        "controlled_conflict_margins.csv",
        "figures/Supplementary_Figure_S4_Stochastic_Selection_Rates.pdf",
        "figures/Supplementary_Figure_S5_Stochastic_RIEC_Margins.pdf",
    ]:
        p = out_dir / name
        if p.exists():
            print(f"- {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
