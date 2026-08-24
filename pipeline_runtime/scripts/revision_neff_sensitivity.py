"""Vary n_eff across a reasonable range for all three cases."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from riec.revision_support import ensure_revision_outdir, evaluate_case_bundle, load_case_bundle, rebuild_case_from_existing_metrics, winner_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='n_eff sensitivity rerun for all three cases.')
    parser.add_argument('--tag', default='arrays_round1_2026-04-24', help='Output folder name under 05_results_workspace/revision_experiments/')
    parser.add_argument('--source', choices=['existing', 'fit'], default='existing', help='existing = rebuild from current main metrics; fit = recompute from raw data.')
    parser.add_argument('--fractions', default='1.0,0.75,0.5,0.25', help='Comma-separated fractions applied to n to form test n_eff values.')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    outdir = ensure_revision_outdir(ROOT, args.tag)
    fractions = [float(x) for x in args.fractions.split(',') if x.strip()]
    score_frames = []
    winner_rows = []
    bundles = {case: load_case_bundle(ROOT, case) for case in ['optics', 'rtd', 'drying']}
    for case, bundle in bundles.items():
        seen: set[int] = set()
        test_values = []
        for frac in fractions:
            n_eff = max(1, int(round(bundle.n * frac)))
            if n_eff not in seen:
                seen.add(n_eff)
                test_values.append((frac, n_eff))
        for frac, n_eff in test_values:
            if args.source == 'fit':
                scores_df, _ = evaluate_case_bundle(bundle, n_eff=n_eff, lambda_c=1.0, include_fold_rows=False)
            else:
                scores_df = rebuild_case_from_existing_metrics(ROOT, case, n_eff=n_eff, lambda_c=1.0)
            scores_df = scores_df.copy()
            scores_df['n_eff_fraction'] = frac
            score_frames.append(scores_df)
            winner = winner_summary(scores_df).iloc[0].to_dict()
            winner['n_eff_fraction'] = frac
            winner_rows.append(winner)

    all_scores = pd.concat(score_frames, ignore_index=True)
    winners = pd.DataFrame(winner_rows)
    all_scores.to_csv(outdir / 'neff_sensitivity_full_scores.csv', index=False)
    winners.to_csv(outdir / 'neff_sensitivity_reasonable_range.csv', index=False)
    print(f'[OK] wrote {outdir / "neff_sensitivity_reasonable_range.csv"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
