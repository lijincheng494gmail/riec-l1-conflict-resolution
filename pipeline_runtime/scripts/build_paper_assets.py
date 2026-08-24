"""
Build a paper asset snapshot: copy selected tables/figures into paper/assets_snapshot/.

This is useful before writing the Results section: you get a stable folder of
figure/table files to reference in the manuscript.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import datetime

ROOT = Path(__file__).resolve().parents[1]


def _copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def main() -> int:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    snap = ROOT / "paper/assets_snapshot" / ts
    snap.mkdir(parents=True, exist_ok=True)

    # RTD
    _copy_if_exists(ROOT / "tables/rtd/metrics.csv", snap / "tables/rtd_metrics.csv")
    for p in (ROOT / "figures/rtd").glob("*.png"):
        _copy_if_exists(p, snap / "figures/rtd" / p.name)

    # Optics/Drying (if any)
    if (ROOT / "tables/optics").exists():
        for p in (ROOT / "tables/optics").glob("*"):
            _copy_if_exists(p, snap / "tables/optics" / p.name)
    if (ROOT / "tables/drying").exists():
        for p in (ROOT / "tables/drying").glob("*"):
            _copy_if_exists(p, snap / "tables/drying" / p.name)

    print(f"[assets] snapshot created: {snap}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
