"""
Run Case II (RTD) end-to-end.

This script:
1) loads raw tracer response runs from data/raw/rtd/data3.csv
2) constructs empirical E(t) per run
3) defines a small RTD model library (Gamma, Lognormal, Axial Dispersion)
4) uses GroupKFold (leave-one-run-out) to compute CV risk (L0)
5) computes BIC, XPE, and C_lambda (L1)
6) saves:
   - tables/rtd/metrics.csv
   - outputs/rtd/selected.json
   - figures/rtd/*.png
"""
from __future__ import annotations

from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from riec.adapters.rtd_adapter import load_rtd_runs_long
from riec.cv import make_group_splits
from riec.models.rtd_models import GammaRTD, LogNormalRTD, AxialDispersionRTD
from riec.core import run_riec_selection
from riec.reporting import save_metrics_table, save_selection_json, plot_bar_summary, plot_fit_overlay


def main() -> int:
    data_path = ROOT / "data/raw/rtd/data3.csv"
    if not data_path.exists():
        print(f"[ERROR] Missing {data_path}.")
        return 1

    print(f"[RTD] Loading: {data_path}")
    df = load_rtd_runs_long(str(data_path))
    # long form columns: t, E, run_id
    # For fitting, treat each row as a sample (t -> E)
    x = df["t"].to_numpy(dtype=float)
    y = df["E"].to_numpy(dtype=float)

    # L0: group splits by run_id
    splits = make_group_splits(df, group_col="run_id")

    # L1: model library
    models = [GammaRTD(), LogNormalRTD(), AxialDispersionRTD()]
    baseline_name = "gamma_2p"

    # lambda weight
    n_eff = len(df)  # simplified
    lambda_weight = 1.0 / np.log(max(n_eff, 3))

    print(f"[RTD] n_eff={n_eff}, lambda={lambda_weight:.4f}")
    scores_df, picks = run_riec_selection(
        x=x,
        y=y,
        models=models,
        splits=splits,
        baseline_name=baseline_name,
        lambda_weight=float(lambda_weight),
        n_eff=n_eff,
    )

    # Save outputs
    out_table = ROOT / "tables/rtd/metrics.csv"
    out_json = ROOT / "outputs/rtd/selected.json"
    save_metrics_table(scores_df, out_table)
    save_selection_json(picks, out_json)

    # Simple plots
    fig_dir = ROOT / "figures/rtd"
    plot_bar_summary(scores_df, "bic", fig_dir / "bic_bar.png", "RTD: BIC by model")
    plot_bar_summary(scores_df, "cv_risk", fig_dir / "cv_risk_bar.png", "RTD: CV risk (MSE) by model")
    plot_bar_summary(scores_df, "c_lambda", fig_dir / "c_lambda_bar.png", "RTD: C_lambda by model")
    plot_bar_summary(scores_df, "xpe", fig_dir / "xpe_bar.png", "RTD: XPE by model (baseline-relative)")

    # Fit overlay (L0 style): pick one run as held-out and predict it
    holdout_run = str(df["run_id"].unique()[0])
    df_te = df[df["run_id"] == holdout_run].copy()
    df_tr = df[df["run_id"] != holdout_run].copy()
    x_tr = df_tr["t"].to_numpy(dtype=float)
    y_tr = df_tr["E"].to_numpy(dtype=float)
    x_te = df_te["t"].to_numpy(dtype=float)
    y_te = df_te["E"].to_numpy(dtype=float)

    preds = {}
    for key, model_name in picks.items():
        if model_name == "gamma_2p":
            m = GammaRTD().fit(x_tr, y_tr)
        elif model_name == "lognormal_2p":
            m = LogNormalRTD().fit(x_tr, y_tr)
        elif model_name == "axdisp_2p":
            m = AxialDispersionRTD().fit(x_tr, y_tr)
        else:
            continue
        preds[f"{key}:{model_name}"] = m.predict(x_te)

    plot_fit_overlay(
        x_te,
        y_te,
        preds,
        fig_dir / f"fit_overlay_holdout_{holdout_run}.png",
        f"RTD: L0 hold-out prediction ({holdout_run})",
        xlabel="t",
        ylabel="E(t)",
    )

    print("\n[RTD] Done.")
    print(f"- metrics: {out_table}")
    print(f"- picks:   {out_json}")
    print(f"- figs:    {fig_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
