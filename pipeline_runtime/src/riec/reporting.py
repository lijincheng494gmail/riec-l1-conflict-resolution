"""
Reporting helpers: save tables and simple figures for the paper.

- Saves metrics table to CSV
- Generates quick plots (bar charts and fit overlays)
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def save_metrics_table(df: pd.DataFrame, out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)


def save_selection_json(picks: Dict[str, str], out_json: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(picks, f, indent=2, ensure_ascii=False)


def plot_bar_summary(df: pd.DataFrame, metric: str, out_path: Path, title: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 4))
    plt.bar(df["model_name"], df[metric])
    plt.xticks(rotation=30, ha="right")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_fit_overlay(
    t: np.ndarray,
    e_obs: np.ndarray,
    preds: Dict[str, np.ndarray],
    out_path: Path,
    title: str,
    max_points: int = 2000,
    xlabel: str = "x",
    ylabel: str = "y",
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # downsample for plotting speed
    if len(t) > max_points:
        idx = np.linspace(0, len(t) - 1, max_points).astype(int)
        t_plot, e_plot = t[idx], e_obs[idx]
    else:
        t_plot, e_plot = t, e_obs

    plt.figure(figsize=(10, 4))
    plt.plot(t_plot, e_plot, label="observed", linewidth=1.5)
    for name, yhat in preds.items():
        if len(yhat) != len(t):
            continue
        yhat_plot = yhat[idx] if len(t) > max_points else yhat
        plt.plot(t_plot, yhat_plot, label=name, linewidth=1.0)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
