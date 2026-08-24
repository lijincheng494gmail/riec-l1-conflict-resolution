"""Export fold-wise group errors and pairwise tests for the drying case."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from riec.revision_support import ensure_revision_outdir, load_case_bundle, evaluate_case_bundle, pairwise_fold_tests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Fold-wise grouped MSE tables and pairwise tests for drying.')
    parser.add_argument('--tag', default='arrays_round1_2026-04-24', help='Output folder name under 05_results_workspace/revision_experiments/')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    outdir = ensure_revision_outdir(ROOT, args.tag)
    bundle = load_case_bundle(ROOT, 'drying')
    _, fold_df = evaluate_case_bundle(bundle, n_eff=bundle.n, lambda_c=1.0, include_fold_rows=True)
    pairwise = pairwise_fold_tests(fold_df, case='drying')
    fold_df.to_csv(outdir / 'drying_foldwise_group_mse.csv', index=False)
    pairwise.to_csv(outdir / 'drying_pairwise_group_tests.csv', index=False)
    print(f'[OK] wrote {outdir / "drying_foldwise_group_mse.csv"}')
    print(f'[OK] wrote {outdir / "drying_pairwise_group_tests.csv"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
