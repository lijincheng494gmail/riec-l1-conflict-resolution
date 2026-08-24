"""Build the standard-criterion comparison tables for the Arrays revision."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from riec.revision_support import (
    ensure_revision_outdir,
    evaluate_case_bundle,
    load_case_bundle,
    rebuild_case_from_existing_metrics,
    winner_summary,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Compare AIC/AICc/BIC/grouped CV/RIEC across all cases.')
    parser.add_argument('--tag', default='arrays_round1_2026-04-24', help='Output folder name under 05_results_workspace/revision_experiments/')
    parser.add_argument('--source', choices=['existing', 'fit'], default='existing', help='existing = rebuild from current main metrics; fit = recompute from raw data.')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    outdir = ensure_revision_outdir(ROOT, args.tag)
    score_frames = []
    fold_frames = []
    for case in ['optics', 'rtd', 'drying']:
        if args.source == 'fit':
            bundle = load_case_bundle(ROOT, case)
            scores_df, fold_df = evaluate_case_bundle(bundle, n_eff=bundle.n, lambda_c=1.0, include_fold_rows=True)
            fold_frames.append(fold_df)
        else:
            scores_df = rebuild_case_from_existing_metrics(ROOT, case, n_eff=None, lambda_c=1.0)
        score_frames.append(scores_df)

    all_scores = pd.concat(score_frames, ignore_index=True)
    winners = winner_summary(all_scores)
    all_scores.to_csv(outdir / 'grouped_metrics_all_cases.csv', index=False)
    winners.to_csv(outdir / 'criterion_winners.csv', index=False)
    if fold_frames:
        pd.concat(fold_frames, ignore_index=True).to_csv(outdir / 'all_foldwise_group_mse.csv', index=False)

    print(f'[OK] wrote {outdir / "grouped_metrics_all_cases.csv"}')
    print(f'[OK] wrote {outdir / "criterion_winners.csv"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
