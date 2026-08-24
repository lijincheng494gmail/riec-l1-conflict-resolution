"""Run Case I (Optics) end-to-end.

This script mirrors the RTD case structure:
1) load spectra (raw if provided, otherwise a small demo dataset)
2) define a proxy optics model library (cosine + polynomial baseline)
3) use GroupKFold (leave-one-condition-out) for L0 evaluation
4) compute BIC, CV risk, XPE, and C_lambda
5) save tables + quick plots

Expected raw data location
--------------------------
Put one or more CSVs under:
    data/raw/optics/

Each CSV should contain columns:
    wavenumber, reflectance, (optional condition_id)
If condition_id is missing, the filename stem is used.

Demo fallback
-------------
If no raw optics CSV exists, we fall back to:
    data/demo/optics_demo.csv
so the whole repository is runnable out-of-the-box.
"""

from __future__ import annotations

from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from riec.adapters.optics_adapter import load_optics_long
from riec.cv import make_group_splits
from riec.core import ModelSpec, run_riec_selection
from riec.models.optics_models import CosinePolyModel
from riec.reporting import save_metrics_table, save_selection_json, plot_bar_summary, plot_fit_overlay


def _resolve_data_paths() -> tuple[list[Path], str]:
    raw_dir = ROOT / "data/raw/optics"
    csvs = sorted(raw_dir.glob("*.csv"))
    if csvs:
        return csvs, "raw"

    demo = ROOT / "data/demo/optics_demo.csv"
    if demo.exists():
        return [demo], "demo"

    return [], "missing"


def main() -> int:
    paths, mode = _resolve_data_paths()
    out_dir = ROOT / "outputs/optics"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = ROOT / "figures/optics"
    fig_dir.mkdir(parents=True, exist_ok=True)
    table_dir = ROOT / "tables/optics"
    table_dir.mkdir(parents=True, exist_ok=True)

    if not paths:
        print("[Optics] SKIPPED: no raw data and no demo data found.")
        return 0

    print(f"[Optics] Loading ({mode}):")
    for p in paths:
        print(f"  - {p}")

    df = load_optics_long(paths)
    x = df["wavenumber"].to_numpy(dtype=float)
    y = df["reflectance"].to_numpy(dtype=float)

    splits = make_group_splits(df, group_col="condition_id")

    # Candidate library: same interference term, increasing baseline flexibility.
    degrees = [0, 1, 2]
    specs = {
        f"cos_poly_deg{d}": ModelSpec(
            name=f"cos_poly_deg{d}",
            param_count=d + 4,
            factory=(lambda d=d: CosinePolyModel(deg=d)),
        )
        for d in degrees
    }

    baseline_name = "cos_poly_deg0"
    n_eff = len(df)
    lambda_weight = 1.0 / np.log(max(n_eff, 3))
    print(f"[Optics] n_eff={n_eff}, lambda={lambda_weight:.4f}")

    scores_df, picks = run_riec_selection(
        x=x,
        y=y,
        models=list(specs.values()),
        splits=splits,
        baseline_name=baseline_name,
        lambda_weight=float(lambda_weight),
        n_eff=n_eff,
    )

    # Save outputs
    out_table = table_dir / "metrics.csv"
    out_json = out_dir / "selected.json"
    save_metrics_table(scores_df, out_table)
    save_selection_json(picks, out_json)

    plot_bar_summary(scores_df, "bic", fig_dir / "bic_bar.png", "Optics: BIC by model")
    plot_bar_summary(scores_df, "cv_risk", fig_dir / "cv_risk_bar.png", "Optics: CV risk (MSE) by model")
    plot_bar_summary(scores_df, "c_lambda", fig_dir / "c_lambda_bar.png", "Optics: C_lambda by model")
    plot_bar_summary(scores_df, "xpe", fig_dir / "xpe_bar.png", "Optics: XPE by model (baseline-relative)")

    # Overlay (L0 style): predict a held-out condition
    holdout = str(df["condition_id"].unique()[0])
    df_te = df[df["condition_id"] == holdout].copy()
    df_tr = df[df["condition_id"] != holdout].copy()
    x_tr = df_tr["wavenumber"].to_numpy(dtype=float)
    y_tr = df_tr["reflectance"].to_numpy(dtype=float)
    x_te = df_te["wavenumber"].to_numpy(dtype=float)
    y_te = df_te["reflectance"].to_numpy(dtype=float)

    preds = {}
    for key, model_name in picks.items():
        if model_name not in specs:
            continue
        m = specs[model_name].factory().fit(x_tr, y_tr)
        preds[f"{key}:{model_name}"] = m.predict(x_te)

    plot_fit_overlay(
        x_te,
        y_te,
        preds,
        fig_dir / f"fit_overlay_holdout_{holdout}.png",
        f"Optics: L0 hold-out prediction ({holdout})",
        xlabel="wavenumber",
        ylabel="reflectance",
    )

    print("\n[Optics] Done.")
    print(f"- metrics: {out_table}")
    print(f"- picks:   {out_json}")
    print(f"- figs:    {fig_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
