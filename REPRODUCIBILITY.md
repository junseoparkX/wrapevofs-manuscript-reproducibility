# Reproduce the published v19 manuscript

## Install

Use Python 3.10 or newer and a clean environment:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

The feature-selection implementation and its tests are maintained separately:
`python -m pip install wrapevofs==0.2.0`.

## Check the supplied manuscript

From `manuscript/source/`:

```bash
python scripts/validate_current_manuscript.py
python scripts/validate_repository_structure.py
python scripts/validate_figure1_freeze.py
python scripts/validate_final_qa_frozen_values.py
python scripts/validate_main_panel_labels.py
python scripts/validate_cgga_figure5_provenance.py
python scripts/validate_radiomics_integration.py
python scripts/validate_locking_simulation_integration.py
python scripts/validate_submission_pdfs.py main.pdf supplementary_information.pdf
```

`CURRENT_MANUSCRIPT.json` records the exact current source and artwork hashes.
The PDFs contain 19 main pages and 55 supplementary pages, five main figures,
two main tables, 29 supplementary figures and 30 supplementary tables.

## Compile

Install a TeX distribution with LuaLaTeX, BibTeX and latexmk, then run from
`manuscript/source/`:

```bash
latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex
latexmk -lualatex -interaction=nonstopmode -halt-on-error supplementary_information.tex
```

## Regenerate figures from frozen aggregates

Use a disposable checkout: renderers write output figures and local QA files.
The checked-in PDF/SVG assets are the authoritative publication files; font and
renderer versions can affect the bytes produced by a new rendering environment.
From `manuscript/source/`:

```bash
python scripts/v19_build_figures23.py
python scripts/v19_build_figures45.py
python v19_work/supplement_polish_20261105/modern/build_s29_vector.py
python v19_work/supplement_polish_20261105/modern/build_modern.py
```

These produce main Figures 2–5 and Supplementary Figures S1–S9, S28 and S29 using included
aggregate inputs. They no longer require a private editor-plugin installation
or the original fenn10 directory. The conceptual Figure 1 has an editable SVG.
`documentation/FIGURE_SOURCE_DATA_MANIFEST.csv` maps the remaining displays to
their source tables and rendering entry points. Older supplementary rendering
routes may require archived source assets or additional SVG/font libraries;
their supplied figures remain directly compilable.

## Analytic and data boundaries

`supplementary_data/cv_score_sensitivity/` contains the complete standard-library
fixed-bank reweighting analysis, inputs, outputs, protocol and integrity manifest.
`supplementary_data/ampad_center_sensitivity/` contains aggregate center-weighting
contrasts; recomputing the bootstrap intervals requires authorized saved predictions.
`supplementary_data/secondary_analysis_settings/` records the original Bayesian,
STABL and BLiP configurations and code excerpts.

Candidate banks, negative results, paired contrasts, locking audits and provenance
remain included. Participant-level records, model checkpoints and controlled
inputs are not distributed. Raw-to-result reproduction requires source access,
the stated preprocessing and the companion software. See `DATA_BOUNDARIES.md`.

## Canonical files and history

Exact duplicate working CSVs were consolidated. Historical source labels,
including those in the unchanged Source Data workbook, resolve through
`manuscript/source/documentation/AGGREGATE_PATH_ALIASES.json`; each alias includes
a retained canonical file with the same SHA-256. Do not remove the current
`v19_work/supplement_polish_20261105/modern/figures/` directory: the Supplementary
TeX directly uses its publication assets.

One-time editing utilities, superseded proposal text and old presentation
checkpoints are available in Git history at commit
`883f5db5310cf265c19b1824622884edac191af6`. Current validation is run by GitHub Actions.
