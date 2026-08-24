# Research dossier QA report

Date: 2026-07-06

This update adds `docs/research_dossier/`, a curated methodological notebook documenting the design reasoning behind RIEC-L1. The dossier is public-facing and intentionally excludes editorial correspondence, reviewer responses, cover letters, marked manuscripts, internal issue reports, and private notes.

## Checks performed

- Added 12 markdown files under `docs/research_dossier/`.
- Added `docs/README.md` documentation index.
- Updated root `README.md` with a link to the methodological notebook.
- Updated `RELEASE_NOTES.md`.
- Removed Python bytecode caches from the release tree.
- Rebuilt `MANIFEST.tsv`.
- Ran `python scripts/check_project.py` successfully.
- Ran `bash scripts/run_controlled_conflict_audit_quick.sh` successfully.

## Public-release boundary

The dossier is a curated research-design record. It does not include:

- editorial correspondence;
- reviewer comments;
- response letters;
- cover letters;
- marked manuscripts;
- private revision logs;
- internal issue reports;
- screenshots from Editorial Manager.
