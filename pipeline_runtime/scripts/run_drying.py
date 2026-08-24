"""Run Case III (Drying kinetics) end-to-end.

This case is designed to support your "necessary complexity" storyline.
We use a public-style thin-layer drying dataset (long-form MR(t)) and
compare a small library of canonical models.

Raw data location
-----------------
Place a CSV at:
    data/raw/drying/drying_curves.csv
with columns:
    t, MR, condition_id, (optional T)

Demo fallback
-------------
If no raw data is found, we use:
    data/demo/drying_demo.csv
so the whole repository can run out-of-the-box.
"""

from __future__ import annotations

from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from riec.adapters.drying_adapter import load_drying_long
from riec.cv import make_group_splits
from riec.core import run_riec_selection
from riec.models.drying_models import (
    LewisDrying,
    PageDrying,
    MidilliDrying,
    TwoTermDrying,
    WeibullDrying,
    ArrheniusLewis,
    ArrheniusPage,
)
from riec.reporting import save_metrics_table, save_selection_json, plot_bar_summary, plot_fit_overlay


def _resolve_data_path() -> tuple[Path | None, str]:
    raw = ROOT / "data/raw/drying/drying_curves.csv"
    if raw.exists():
        return raw, "raw"
    demo = ROOT / "data/demo/drying_demo.csv"
    if demo.exists():
        return demo, "demo"
    return None, "missing"


def main() -> int:
    data_path, mode = _resolve_data_path()
    out_dir = ROOT / "outputs/drying"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = ROOT / "figures/drying"
    fig_dir.mkdir(parents=True, exist_ok=True)
    table_dir = ROOT / "tables/drying"
    table_dir.mkdir(parents=True, exist_ok=True)

    if data_path is None:
        print("[Drying] SKIPPED: no raw data and no demo data found.")
        return 0

    print(f"[Drying] Loading ({mode}): {data_path}")
    df = load_drying_long(data_path)

    # x includes temperature for Arrhenius-tied models
    t = df["t"].to_numpy(dtype=float)
    T = df["T"].to_numpy(dtype=float)
    # If T missing, keep NaNs; models will handle
    x = np.column_stack([t, T])
    y = df["MR"].to_numpy(dtype=float)

    splits = make_group_splits(df, group_col="condition_id")

    models = [
        LewisDrying(),
        PageDrying(),
        MidilliDrying(),
        TwoTermDrying(),
        WeibullDrying(),
        ArrheniusLewis(),
        ArrheniusPage(),
    ]
    baseline_name = "lewis_1p"

    n_eff = len(df)
    lambda_weight = 1.0 / np.log(max(n_eff, 3))
    print(f"[Drying] n_eff={n_eff}, lambda={lambda_weight:.4f}")

    scores_df, picks = run_riec_selection(
        x=x,
        y=y,
        models=models,
        splits=splits,
        baseline_name=baseline_name,
        lambda_weight=float(lambda_weight),
        n_eff=n_eff,
    )

    out_table = table_dir / "metrics.csv"
    out_json = out_dir / "selected.json"
    save_metrics_table(scores_df, out_table)
    save_selection_json(picks, out_json)

    plot_bar_summary(scores_df, "bic", fig_dir / "bic_bar.png", "Drying: BIC by model")
    plot_bar_summary(scores_df, "cv_risk", fig_dir / "cv_risk_bar.png", "Drying: CV risk (MSE) by model")
    plot_bar_summary(scores_df, "c_lambda", fig_dir / "c_lambda_bar.png", "Drying: C_lambda by model")
    plot_bar_summary(scores_df, "xpe", fig_dir / "xpe_bar.png", "Drying: XPE by model (baseline-relative)")

    # Overlay (L0 style): predict a held-out condition
    holdout = str(df["condition_id"].unique()[0])
    df_te = df[df["condition_id"] == holdout].copy()
    df_tr = df[df["condition_id"] != holdout].copy()

    x_tr = np.column_stack([df_tr["t"].to_numpy(float), df_tr["T"].to_numpy(float)])
    y_tr = df_tr["MR"].to_numpy(float)
    x_te = np.column_stack([df_te["t"].to_numpy(float), df_te["T"].to_numpy(float)])
    y_te = df_te["MR"].to_numpy(float)

    # helper map by model name
    name_to_cls = {
        "lewis_1p": LewisDrying,
        "page_2p": PageDrying,
        "midilli_4p": MidilliDrying,
        "two_term_3p": TwoTermDrying,
        "weibull_2p": WeibullDrying,
        "arrhenius_lewis_2p": ArrheniusLewis,
        "arrhenius_page_3p": ArrheniusPage,
    }

    preds = {}
    for key, model_name in picks.items():
        cls = name_to_cls.get(model_name)
        if cls is None:
            continue
        m = cls().fit(x_tr, y_tr)
        preds[f"{key}:{model_name}"] = m.predict(x_te)

    plot_fit_overlay(
        df_te["t"].to_numpy(float),
        y_te,
        preds,
        fig_dir / f"fit_overlay_holdout_{holdout}.png",
        f"Drying: L0 hold-out prediction ({holdout})",
        xlabel="t",
        ylabel="MR",
    )

    print("\n[Drying] Done.")
    print(f"- metrics: {out_table}")
    print(f"- picks:   {out_json}")
    print(f"- figs:    {fig_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
