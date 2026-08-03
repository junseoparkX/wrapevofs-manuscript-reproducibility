# Reproducibility guide

## Build the manuscript

The manuscript is designed for LuaLaTeX and Overleaf. From `manuscript/`:

```bash
latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex
```

The verified build has 43 pages. It contains no unresolved references or citations and no reported overfull or underfull boxes.

## Regenerate figures from frozen aggregate tables

Create a Python environment and install the plotting requirements:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python analysis/regret_revision/generate_revision_figures.py
python analysis/regret_revision/generate_supplementary_revision_figures.py
```

These scripts consume the checked-in aggregate audit and plot-source CSVs. They do not run GA, RFECV, Direct selection, held-out evaluation, Bayesian analysis, STABL, BLiP, bootstrap resampling, or feature-selection experiments.

## Controlled-input analysis script

`analysis/regret_revision/build_revision_analyses.py` is retained for provenance, but complete execution requires the separately controlled ADNI, AMP-AD, and CGGA source artifacts and a sibling checkout of the companion package. Those controlled inputs are intentionally absent. Do not interpret failure to reproduce the raw-to-aggregate stage without them as an invitation to fabricate, impute, or replace missing artifacts.

## Companion package validation

The software implementation and tests live at [junseoparkX/wrapevofs-package](https://github.com/junseoparkX/wrapevofs-package). Version 0.2.0 is validated separately across its configured Python CI matrix. The manuscript repository does not vendor package code.

## Frozen-results rule

The CSV files under `audits/` and `analysis/regret_revision/` are authoritative frozen outputs for the manuscript revision. Repository preparation must not alter their empirical numerical values.
