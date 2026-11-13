# Reproduce the v20 manuscript

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
python scripts/validate_tolerance_calibration.py
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
The PDFs contain 21 main pages and 60 supplementary pages, five main figures,
two main tables, 29 supplementary figures and 32 supplementary tables.

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

## Development-only allowance calibration

From `manuscript/source/`, reproduce all six branch/scorer choices using the non-participant audit inputs:

```bash
python supplementary_data/tolerance_calibration/calibrate_allowance.py --input supplementary_data/tolerance_calibration/candidate_development_audit.csv --output /tmp/wrapevofs-calibration --search grid
```

The main calibration example uses the earlier seven-point grid. Use `--search breakpoints` for the supplementary sensitivity. Full precision is retained for eligibility; displayed decimal allowances are rounded. Calibration uses development scores and feature masks only. The paired AUROC bootstrap additionally requires authorized held-out predictions; aggregate signature-level scores and reported contrasts are included. The all-240 overlap is a fitted objective, and the earlier reserved-seed check remains distinct.

The opt-in library calibration API requires `pip install wrapevofs==0.3.0`. To verify both library search modes and their canonical selected masks, run `python scripts/validate_tolerance_calibration.py --package` from `manuscript/source/`. The v0.2.0 pin above is retained for the recorded reference benchmark.

To reproduce the main analysis with the v0.3.0 API, pass `delta_grid=[0,0.0025,0.005,0.0075,0.01,0.015,0.02]` to `calibrate_tolerance`. The unchanged API default searches observed breakpoints. `analysis_hierarchy.json` records the post hoc presentation order; the original eight- and twelve-contrast families remain separate and unchanged.
