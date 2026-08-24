"""Helpers for the Arrays major-revision reruns.

This module keeps the reviewer-facing reruns in one place so the new scripts
stay thin and consistent. It reuses the existing main-case loaders/models and
adds only the extra bookkeeping needed for:
- standard criterion comparisons (AIC/AICc/BIC/grouped CV/RIEC)
- lambda sensitivity
- n_eff sensitivity
- fold-wise variance / pairwise tests
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import itertools

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import GroupKFold

from riec.adapters.drying_adapter import load_drying_long
from riec.adapters.optics_adapter import load_optics_long
from riec.adapters.rtd_adapter import load_rtd_runs_long
from riec.core import ModelSpec, bic_from_sse, evaluate_model_on_indices
from riec.models.drying_models import (
    ArrheniusLewis,
    ArrheniusPage,
    LewisDrying,
    MidilliDrying,
    PageDrying,
    TwoTermDrying,
    WeibullDrying,
)
from riec.models.optics_models import CosinePolyModel
from riec.models.rtd_models import AxialDispersionRTD, GammaRTD, LogNormalRTD


@dataclass(frozen=True)
class LabeledSplit:
    train_idx: np.ndarray
    test_idx: np.ndarray
    holdout_group: str
    fold_id: int


@dataclass(frozen=True)
class CaseBundle:
    case: str
    df: pd.DataFrame
    x: np.ndarray
    y: np.ndarray
    group_col: str
    splits: list[LabeledSplit]
    model_specs: list[ModelSpec]
    baseline_name: str

    @property
    def n(self) -> int:
        return int(len(self.y))

    @property
    def n_groups(self) -> int:
        return int(self.df[self.group_col].nunique())




def current_main_metrics_path(runtime_root: str | Path, case: str) -> Path:
    runtime_root = Path(runtime_root).resolve()
    workspace_root = workspace_root_from_runtime(runtime_root)
    preferred = workspace_root / '05_results_workspace' / 'current_main_results' / case / 'tables' / 'metrics.csv'
    if preferred.exists():
        return preferred
    fallback = runtime_root / 'tables' / case / 'metrics.csv'
    if fallback.exists():
        return fallback
    raise FileNotFoundError(f'Cannot find current metrics for case={case!r}')


def reconstruct_sse_from_bic(bic: float, k: int, n_eff_used: int) -> float:
    n_eff_used = int(max(1, n_eff_used))
    bic = float(bic)
    k = int(k)
    return float(n_eff_used * np.exp((bic - k * np.log(n_eff_used)) / n_eff_used))


def rebuild_case_from_existing_metrics(
    runtime_root: str | Path,
    case: str,
    *,
    n_eff: int | None = None,
    lambda_weight: float | None = None,
    lambda_c: float = 1.0,
) -> pd.DataFrame:
    bundle = load_case_bundle(runtime_root, case)
    metrics_path = current_main_metrics_path(runtime_root, case)
    base = pd.read_csv(metrics_path)
    if n_eff is None:
        n_eff = bundle.n
    n_eff = int(max(1, n_eff))
    if lambda_weight is None:
        lambda_weight = default_lambda(n_eff=n_eff, c=lambda_c)
    lambda_weight = float(lambda_weight)

    df = base.copy()
    df['case'] = case
    df['n'] = int(bundle.n)
    df['n_groups'] = int(bundle.n_groups)
    df['group_col'] = bundle.group_col
    df['baseline_name'] = bundle.baseline_name
    df['n_eff'] = n_eff
    df['lambda_c'] = float(lambda_c)
    df['lambda_weight'] = lambda_weight
    # Current package tables were produced with n_eff = n in the main scripts.
    df['sse'] = [reconstruct_sse_from_bic(b, k, bundle.n) for b, k in zip(df['bic'], df['k_params'])]
    df['aic'] = [aic_from_sse(s, bundle.n, k) for s, k in zip(df['sse'], df['k_params'])]
    df['aicc'] = [aicc_from_sse(s, bundle.n, k) for s, k in zip(df['sse'], df['k_params'])]
    if n_eff != bundle.n:
        df['bic'] = [bic_from_sse(s, n=bundle.n, k=k, n_eff=n_eff) for s, k in zip(df['sse'], df['k_params'])]
    # recompute xpe to avoid dependency on the table order
    base_cv = float(df.loc[df['model_name'] == bundle.baseline_name, 'cv_risk'].iloc[0])
    base_cv = max(base_cv, 1e-30)
    df['xpe'] = base_cv / df['cv_risk'].clip(lower=1e-30)
    df['c_lambda'] = df['bic'] + lambda_weight * np.log(1.0 / df['xpe'].clip(lower=1e-30))
    wanted_cols = [
        'case', 'model_name', 'k_params', 'n', 'n_groups', 'group_col', 'baseline_name',
        'n_eff', 'lambda_c', 'lambda_weight', 'sse', 'aic', 'aicc', 'bic', 'cv_risk', 'xpe', 'c_lambda',
    ]
    return df[wanted_cols].sort_values(['case', 'c_lambda', 'cv_risk', 'bic', 'model_name']).reset_index(drop=True)

def workspace_root_from_runtime(runtime_root: str | Path) -> Path:
    runtime_root = Path(runtime_root).resolve()
    return runtime_root.parents[1]


def ensure_revision_outdir(runtime_root: str | Path, tag: str) -> Path:
    workspace_root = workspace_root_from_runtime(runtime_root)
    outdir = workspace_root / '05_results_workspace' / 'revision_experiments' / tag
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def ensure_revision_response_dir(runtime_root: str | Path, tag: str) -> Path:
    workspace_root = workspace_root_from_runtime(runtime_root)
    outdir = workspace_root / '06_revision_response' / tag
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def _fresh_model_spec(model_like: Any) -> ModelSpec:
    if isinstance(model_like, ModelSpec):
        return model_like
    name = str(getattr(model_like, 'name', model_like.__class__.__name__))
    k = int(getattr(model_like, 'param_count', 0))
    cls = model_like.__class__

    def _factory(cls=cls, name=name, k=k):
        m = cls()
        try:
            m.name = name
        except Exception:
            pass
        try:
            m.param_count = k
        except Exception:
            pass
        return m

    return ModelSpec(name=name, param_count=k, factory=_factory)


def make_labeled_group_splits(df: pd.DataFrame, group_col: str) -> list[LabeledSplit]:
    groups = df[group_col].to_numpy()
    unique_groups = np.unique(groups)
    n_splits = len(unique_groups)
    if n_splits < 2:
        raise ValueError(f'Need at least 2 groups for group CV; got {n_splits}')
    gkf = GroupKFold(n_splits=n_splits)
    x_dummy = np.zeros((len(df), 1), dtype=float)
    out: list[LabeledSplit] = []
    for fold_id, (tr, te) in enumerate(gkf.split(x_dummy, y=None, groups=groups), start=1):
        holdout = pd.unique(df.iloc[te][group_col]).tolist()
        label = ','.join(str(v) for v in holdout)
        out.append(LabeledSplit(train_idx=tr, test_idx=te, holdout_group=label, fold_id=fold_id))
    return out


def default_lambda(n_eff: int, c: float = 1.0) -> float:
    n_eff = max(int(round(n_eff)), 3)
    return float(c / np.log(n_eff))


def aic_from_sse(sse: float, n: int, k: int) -> float:
    sse = max(float(sse), 1e-30)
    n = int(max(n, 1))
    return float(n * np.log(sse / n) + 2 * k)


def aicc_from_sse(sse: float, n: int, k: int) -> float:
    aic = aic_from_sse(sse=sse, n=n, k=k)
    denom = n - k - 1
    if denom <= 0:
        return float('inf')
    return float(aic + (2 * k * (k + 1)) / denom)


def _resolve_optics_paths(runtime_root: Path) -> list[Path]:
    raw_dir = runtime_root / 'data' / 'raw' / 'optics'
    csvs = sorted(raw_dir.glob('*.csv'))
    if csvs:
        return csvs
    demo = runtime_root / 'data' / 'demo' / 'optics_demo.csv'
    if demo.exists():
        return [demo]
    raise FileNotFoundError('No optics CSV files found under data/raw/optics or data/demo/optics_demo.csv')


def _resolve_drying_path(runtime_root: Path) -> Path:
    raw = runtime_root / 'data' / 'raw' / 'drying' / 'drying_curves.csv'
    if raw.exists():
        return raw
    demo = runtime_root / 'data' / 'demo' / 'drying_demo.csv'
    if demo.exists():
        return demo
    raise FileNotFoundError('No drying CSV found under data/raw/drying or data/demo/drying_demo.csv')


def load_case_bundle(runtime_root: str | Path, case: str) -> CaseBundle:
    runtime_root = Path(runtime_root).resolve()
    case = str(case).lower()

    if case == 'rtd':
        data_path = runtime_root / 'data' / 'raw' / 'rtd' / 'data3.csv'
        if not data_path.exists():
            raise FileNotFoundError(f'Missing RTD data: {data_path}')
        df = load_rtd_runs_long(str(data_path))
        x = df['t'].to_numpy(dtype=float)
        y = df['E'].to_numpy(dtype=float)
        group_col = 'run_id'
        models = [GammaRTD(), LogNormalRTD(), AxialDispersionRTD()]
        baseline_name = 'gamma_2p'
    elif case == 'optics':
        paths = _resolve_optics_paths(runtime_root)
        df = load_optics_long(paths)
        x = df['wavenumber'].to_numpy(dtype=float)
        y = df['reflectance'].to_numpy(dtype=float)
        group_col = 'condition_id'
        degrees = [0, 1, 2]
        models = [
            ModelSpec(
                name=f'cos_poly_deg{d}',
                param_count=d + 4,
                factory=(lambda d=d: CosinePolyModel(deg=d)),
            )
            for d in degrees
        ]
        baseline_name = 'cos_poly_deg0'
    elif case == 'drying':
        data_path = _resolve_drying_path(runtime_root)
        df = load_drying_long(data_path)
        t = df['t'].to_numpy(dtype=float)
        T = df['T'].to_numpy(dtype=float)
        x = np.column_stack([t, T])
        y = df['MR'].to_numpy(dtype=float)
        group_col = 'condition_id'
        models = [
            LewisDrying(),
            PageDrying(),
            MidilliDrying(),
            TwoTermDrying(),
            WeibullDrying(),
            ArrheniusLewis(),
            ArrheniusPage(),
        ]
        baseline_name = 'lewis_1p'
    else:
        raise ValueError(f'Unknown case: {case}')

    splits = make_labeled_group_splits(df, group_col=group_col)
    specs = [_fresh_model_spec(m) for m in models]
    return CaseBundle(
        case=case,
        df=df,
        x=np.asarray(x, dtype=float),
        y=np.asarray(y, dtype=float),
        group_col=group_col,
        splits=splits,
        model_specs=specs,
        baseline_name=baseline_name,
    )


def evaluate_case_bundle(
    bundle: CaseBundle,
    *,
    n_eff: int | None = None,
    lambda_weight: float | None = None,
    lambda_c: float = 1.0,
    include_fold_rows: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    n = bundle.n
    if n_eff is None:
        n_eff = n
    n_eff = int(max(1, n_eff))
    if lambda_weight is None:
        lambda_weight = default_lambda(n_eff=n_eff, c=lambda_c)
    lambda_weight = float(lambda_weight)

    model_rows: list[dict[str, Any]] = []
    fold_rows: list[dict[str, Any]] = []
    cv_map: dict[str, float] = {}

    for spec in bundle.model_specs:
        fold_mse: list[float] = []
        for split in bundle.splits:
            m = spec.factory()
            mse_te, _ = evaluate_model_on_indices(m, bundle.x, bundle.y, split.train_idx, split.test_idx)
            fold_mse.append(float(mse_te))
            if include_fold_rows:
                fold_rows.append(
                    {
                        'case': bundle.case,
                        'fold_id': int(split.fold_id),
                        'holdout_group': str(split.holdout_group),
                        'model_name': spec.name,
                        'fold_mse': float(mse_te),
                    }
                )

        m_full = spec.factory()
        m_full.fit(bundle.x, bundle.y)
        yhat = m_full.predict(bundle.x)
        sse = float(np.sum((bundle.y - yhat) ** 2))
        aic = aic_from_sse(sse=sse, n=n, k=spec.param_count)
        aicc = aicc_from_sse(sse=sse, n=n, k=spec.param_count)
        bic = bic_from_sse(sse=sse, n=n, k=spec.param_count, n_eff=n_eff)
        cv = float(np.mean(fold_mse)) if fold_mse else float('nan')
        cv_map[spec.name] = cv
        model_rows.append(
            {
                'case': bundle.case,
                'model_name': spec.name,
                'k_params': int(spec.param_count),
                'n': int(n),
                'n_groups': int(bundle.n_groups),
                'group_col': bundle.group_col,
                'baseline_name': bundle.baseline_name,
                'n_eff': int(n_eff),
                'lambda_c': float(lambda_c),
                'lambda_weight': float(lambda_weight),
                'sse': float(sse),
                'aic': float(aic),
                'aicc': float(aicc),
                'bic': float(bic),
                'cv_risk': float(cv),
            }
        )

    df = pd.DataFrame(model_rows)
    if df.empty:
        return df, pd.DataFrame(fold_rows)
    base_cv = max(float(cv_map[bundle.baseline_name]), 1e-30)
    df['xpe'] = df['cv_risk'].clip(lower=1e-30).rdiv(base_cv)
    df['c_lambda'] = df['bic'] + lambda_weight * np.log(1.0 / df['xpe'].clip(lower=1e-30))
    df = df.sort_values(['case', 'c_lambda', 'cv_risk', 'bic', 'model_name'], ascending=[True, True, True, True, True]).reset_index(drop=True)
    fold_df = pd.DataFrame(fold_rows)
    return df, fold_df


def winner_summary(scores_df: pd.DataFrame) -> pd.DataFrame:
    if scores_df.empty:
        return pd.DataFrame(columns=['case', 'aic_best', 'aicc_best', 'bic_best', 'cv_best', 'riec_best'])
    out_rows = []
    for case, g in scores_df.groupby('case', sort=False):
        row = {
            'case': case,
            'n': int(g['n'].iloc[0]),
            'n_groups': int(g['n_groups'].iloc[0]),
            'group_col': str(g['group_col'].iloc[0]),
            'baseline_name': str(g['baseline_name'].iloc[0]),
            'n_eff': int(g['n_eff'].iloc[0]),
            'lambda_c': float(g['lambda_c'].iloc[0]),
            'lambda_weight': float(g['lambda_weight'].iloc[0]),
            'aic_best': str(g.sort_values(['aic', 'cv_risk', 'model_name']).iloc[0]['model_name']),
            'aicc_best': str(g.sort_values(['aicc', 'cv_risk', 'model_name']).iloc[0]['model_name']),
            'bic_best': str(g.sort_values(['bic', 'cv_risk', 'model_name']).iloc[0]['model_name']),
            'cv_best': str(g.sort_values(['cv_risk', 'bic', 'model_name']).iloc[0]['model_name']),
            'riec_best': str(g.sort_values(['c_lambda', 'cv_risk', 'bic', 'model_name']).iloc[0]['model_name']),
        }
        out_rows.append(row)
    return pd.DataFrame(out_rows)


def pairwise_fold_tests(fold_df: pd.DataFrame, case: str) -> pd.DataFrame:
    case_df = fold_df[fold_df['case'] == case].copy()
    if case_df.empty:
        return pd.DataFrame(
            columns=[
                'case', 'model_a', 'model_b', 'n_pairs', 'wins_model_a', 'wins_model_b', 'ties',
                'mean_mse_model_a', 'mean_mse_model_b', 'mean_diff_a_minus_b', 'median_diff_a_minus_b',
                'sign_test_pvalue', 'wilcoxon_pvalue', 'better_mean_model',
            ]
        )
    pivot = case_df.pivot(index='holdout_group', columns='model_name', values='fold_mse').sort_index(axis=1)
    rows: list[dict[str, Any]] = []
    for model_a, model_b in itertools.combinations(pivot.columns.tolist(), 2):
        pair = pivot[[model_a, model_b]].dropna()
        diff = pair[model_a] - pair[model_b]
        non_zero = diff[diff != 0]
        wins_a = int((diff < 0).sum())
        wins_b = int((diff > 0).sum())
        ties = int((diff == 0).sum())
        sign_p = float('nan')
        wilcoxon_p = float('nan')
        if len(non_zero) > 0:
            x = int(min((non_zero < 0).sum(), (non_zero > 0).sum()))
            n_non_zero = int(len(non_zero))
            sign_p = float(stats.binomtest(k=x, n=n_non_zero, p=0.5, alternative='two-sided').pvalue)
            try:
                wilcoxon_p = float(stats.wilcoxon(non_zero).pvalue)
            except ValueError:
                wilcoxon_p = float('nan')
        mean_a = float(pair[model_a].mean())
        mean_b = float(pair[model_b].mean())
        rows.append(
            {
                'case': case,
                'model_a': model_a,
                'model_b': model_b,
                'n_pairs': int(len(pair)),
                'wins_model_a': wins_a,
                'wins_model_b': wins_b,
                'ties': ties,
                'mean_mse_model_a': mean_a,
                'mean_mse_model_b': mean_b,
                'mean_diff_a_minus_b': float(diff.mean()),
                'median_diff_a_minus_b': float(diff.median()),
                'sign_test_pvalue': sign_p,
                'wilcoxon_pvalue': wilcoxon_p,
                'better_mean_model': model_a if mean_a < mean_b else model_b,
            }
        )
    return pd.DataFrame(rows).sort_values(
        ['case', 'sign_test_pvalue', 'wilcoxon_pvalue', 'model_a', 'model_b'],
        ascending=[True, True, True, True, True],
        na_position='last',
    ).reset_index(drop=True)


def markdown_summary(scores_df: pd.DataFrame, winners_df: pd.DataFrame) -> str:
    lines: list[str] = []
    lines.append('# Arrays revision rerun summary')
    lines.append('')
    lines.append('This package reruns the main three-case pipeline and adds the reviewer-driven supplements:')
    lines.append('- standard criterion comparisons (AIC/AICc/BIC/grouped CV/RIEC)')
    lines.append('- lambda sensitivity for the drying case')
    lines.append('- n_eff sensitivity across all three cases')
    lines.append('- fold-wise group error tables and pairwise tests for drying')
    lines.append('')
    if winners_df.empty:
        lines.append('No winner summary available.')
        return "\n".join(lines)
    lines.append('## Winner summary')
    lines.append('')
    for _, row in winners_df.iterrows():
        lines.append(
            f"- **{row['case']}**: AIC={row['aic_best']}, AICc={row['aicc_best']}, "
            f"BIC={row['bic_best']}, grouped CV={row['cv_best']}, RIEC={row['riec_best']}"
        )
    lines.append('')
    lines.append('## Main interpretation hook')
    lines.append('')
    lines.append('- Optics and RTD are agreement regimes: all major criteria pick the same model.')
    lines.append('- Drying is the disagreement regime: simpler information criteria, grouped CV, and RIEC do not all pick the same model, which is exactly the case where the paper needs a transparent compromise rule.')
    return "\n".join(lines)
