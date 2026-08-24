"""Create a short markdown summary and copy the reviewer letter into the package."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from riec.revision_support import ensure_revision_outdir, ensure_revision_response_dir, markdown_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Write summary markdown for the Arrays revision rerun package.')
    parser.add_argument('--tag', default='arrays_round1_2026-04-24', help='Output folder name under 05_results_workspace/revision_experiments/')
    parser.add_argument('--review-letter', default=str(Path('/mnt/data/粘贴的文本 (1).txt')), help='Path to the raw reviewer letter text file to copy into 06_revision_response.')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    outdir = ensure_revision_outdir(ROOT, args.tag)
    response_dir = ensure_revision_response_dir(ROOT, args.tag)
    scores = pd.read_csv(outdir / 'grouped_metrics_all_cases.csv')
    winners = pd.read_csv(outdir / 'criterion_winners.csv')
    summary = markdown_summary(scores_df=scores, winners_df=winners)
    (outdir / 'REVISION_ANALYSIS_SUMMARY.md').write_text(summary + '\n', encoding='utf-8')
    (response_dir / 'arrays_round1_rerun_summary.md').write_text(summary + '\n', encoding='utf-8')
    review_letter = Path(args.review_letter)
    if review_letter.exists():
        shutil.copy2(review_letter, response_dir / 'reviewer_letter_raw.txt')
    print(f'[OK] wrote {outdir / "REVISION_ANALYSIS_SUMMARY.md"}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
