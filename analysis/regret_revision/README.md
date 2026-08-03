# Regret-revision analysis materials

The checked-in CSV files are frozen aggregate plot sources used by the manuscript revision.

- `generate_revision_figures.py` renders the main revision figures from `audits/` and the frozen paired-interval CSV in this directory.
- `generate_supplementary_revision_figures.py` renders the revision-only supplementary diagnostics.
- `build_revision_analyses.py` documents the controlled-input raw-to-aggregate procedure. It requires a sibling checkout of `wrapevofs-package` plus provider-controlled ADNI, AMP-AD, and CGGA artifacts that are intentionally not included here.

Repository preparation did not execute these scripts and did not alter any empirical numerical value.
