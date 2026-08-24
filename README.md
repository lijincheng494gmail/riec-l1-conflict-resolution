# RIEC-L1 conflict resolution

Reproducibility package for:

> Jincheng Li, Yuchen Zhao and Xifeng Li. **RIEC-L1: An evidence-led conflict-resolution layer for finite candidate libraries in engineering data.** *Array* 31 (2026), 101097. https://doi.org/10.1016/j.array.2026.101097

RIEC-L1 addresses a practical decision problem: reasonable criteria such as cross-validation error, information criteria and stability can disagree within the same finite model library. Instead of treating one criterion as universally decisive, the workflow records the disagreement, applies a declared conflict-resolution rule and returns an auditable selection.

## Repository map

- `pipeline_runtime/src/riec/` — method implementation;
- `pipeline_runtime/scripts/` — runnable case studies and controlled audits;
- `pipeline_runtime/data/` — compact engineering data and demos;
- `results/` — selected reference tables, sensitivity analyses and negative checks;
- `docs/research_dossier/` — problem origin, design decisions, abandoned claims and limitations;
- `assets/RIEC_L1_WORKFLOW.pdf` — compact workflow figure.

## Quickstart

```bash
cd pipeline_runtime
python -m venv .venv
source .venv/bin/activate
python -m pip install -r environment/requirements.txt
python scripts/check_project.py
python scripts/run_rtd.py
```

Run all three engineering cases with:

```bash
bash scripts/run_all.sh
```

See [`pipeline_runtime/QUICKSTART.md`](pipeline_runtime/QUICKSTART.md) and [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) for detailed commands.

## Scientific boundary

The published evidence supports the use of an explicit conflict-resolution layer in the studied finite engineering candidate libraries. It does not establish a universally optimal criterion, unrestricted external transport or a domain-independent predictor. The controlled audit and abandoned-claim record are retained so that disagreement is visible rather than edited away.

## License and citation

Code is released under the MIT License. Data terms are described in [`LICENSE_DATA.md`](LICENSE_DATA.md). Citation metadata are in [`CITATION.cff`](CITATION.cff).
