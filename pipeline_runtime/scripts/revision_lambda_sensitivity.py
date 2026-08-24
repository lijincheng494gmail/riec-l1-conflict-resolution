"""Sweep lambda=c/log(n_eff) for the drying case."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from riec.revision_support import ensure_revision_outdir, evaluate_case_bundle, load_case_bundle, rebuild_case_from_existing_metrics, winner_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Lambda sensitivity rerun for the drying case.')
    parser.add_argument('--tag', default='arrays_round1_2026-04-24', help='Output folder name under 05_results_workspace/revision_experiments/')
    parser.add_argument('--source', choices=['existing', 'fit'], default='existing', help='existing = rebuild from current main metrics; fit = recompute from raw data.')
    parser.add_argument('--c-grid', default='0,0.25,0.5,1,2,5,10,20,50,100,200', help='Comma-separated c values for lambda=c/log(n_eff).')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    outdir = ensure_revision_outdir(ROOT, args.tag)
    bundle = load_case_bundle(ROOT, 'drying')
    c_values = [float(x) for x in args.c_grid.split(',') if x.strip()]
    frames = []
    winner_rows = []
    for c in c_values:
        if args.source == 'fit':
            scores_df, _ = evaluate_case_bundle(bundle, n_eff=bundle.n, lambda_c=c, include_fold_rows=False)
        else:
            scores_df = rebuild_case_from_existing_metrics(ROOT, 'drying', n_eff=bundle.n, lambda_c=c)
        scores_df = scores_df.copy()
        scores_df['lambda_grid_c'] = c
        frames.append(scores_df)
        winner = winner_summary(scores_df).iloc[0].to_dict()
        winner_rows.append(winner)

    all_scores = pd.concat(frames, ignore_index=True)
    winners = pd.DataFrame(winner_rows)
    all_scores.to_csv(outdir / 'lambda_sensitivity_drying_full.csv', index=False)
    winners.to_csv(outdir / 'lambda_sensitivity_drying.csv', index=False)
    print(f'[OK] wrote {outdir / "lambda_sensitivity_drying.csv"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
