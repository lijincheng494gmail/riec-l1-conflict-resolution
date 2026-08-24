"""
Sanity checker for the experiment scaffold.

Run:
    python scripts/check_project.py

It checks:
- Python deps importable
- Raw data presence per case
- Prints what is runnable now
"""
from __future__ import annotations

from pathlib import Path
import importlib
import sys

ROOT = Path(__file__).resolve().parents[1]


def _check_import(pkg: str) -> bool:
    try:
        importlib.import_module(pkg)
        return True
    except Exception as e:
        print(f"[MISSING] import {pkg}: {e}")
        return False


def main() -> int:
    print("== RIEC RINENG scaffold: sanity check ==")
    print(f"Project root: {ROOT}")

    print("\n-- Dependencies --")
    ok = True
    for pkg in ["numpy", "pandas", "scipy", "sklearn", "matplotlib"]:
        ok = _check_import(pkg) and ok

    print("\n-- Data presence --")
    rtd = (ROOT / "data/raw/rtd/data3.csv").exists() or (ROOT / "data/raw/rtd/data1.csv").exists()
    optics_raw = any((ROOT / "data/raw/optics").glob("*.csv"))
    drying_raw = (ROOT / "data/raw/drying/drying_curves.csv").exists()
    optics_demo = (ROOT / "data/demo/optics_demo.csv").exists()
    drying_demo = (ROOT / "data/demo/drying_demo.csv").exists()

    optics = optics_raw or optics_demo
    drying = drying_raw or drying_demo

    print(f"RTD runnable:    {rtd} (expected data/raw/rtd/data3.csv)")
    print(f"Optics runnable: {optics} (raw={optics_raw}, demo={optics_demo})")
    print(f"Drying runnable: {drying} (raw={drying_raw}, demo={drying_demo})")

    print("\n-- Next commands --")
    if rtd:
        print("python scripts/run_rtd.py")
    else:
        print("RTD: missing data, please check data/raw/rtd/")
    if optics:
        print("python scripts/run_optics.py")
    else:
        print("Optics: add spectra CSV to data/raw/optics/")
    if drying:
        print("python scripts/run_drying.py")
    else:
        print("Drying: add drying_curves.csv to data/raw/drying/")

    print("\nAll cases:")
    print("bash scripts/run_all.sh")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
