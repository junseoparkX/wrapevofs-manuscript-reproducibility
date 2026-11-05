# Reproducibility guide

## Environment

Create a clean Python environment from the repository root:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The associated software release can be installed independently with:

```bash
python -m pip install wrapevofs==0.2.0
```

## Build the manuscript

The manuscript uses LuaLaTeX. From `manuscript/source/`:

```bash
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error main.tex
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error supplementary_information.tex
```

The verified outputs contain 19 main-article pages and 54 Supplementary pages.
The final logs contain no unresolved citations or references and no overfull or
underfull boxes.

## Validate frozen results and presentation

Run the following commands from `manuscript/source/`:

```bash
python scripts/validate_current_manuscript.py
python scripts/validate_figure1_freeze.py
python scripts/validate_final_qa_frozen_values.py
python scripts/validate_main_panel_labels.py
python scripts/validate_cgga_figure5_provenance.py
python scripts/validate_radiomics_integration.py
python scripts/validate_locking_simulation_integration.py
python scripts/validate_submission_pdfs.py main.pdf supplementary_information.pdf
```

These checks cover frozen numerical invariants, canonical panel labels,
figure-source provenance, VGH radiomics integration boundaries, the controlled
locking-layer simulation, PDF page boundaries, blank pages, and Supplementary
display numbering. Detailed outcomes are recorded in
`manuscript/source/CURRENT_MANUSCRIPT.json`; earlier validation reports retain their historical scope.

## Rebuild presentation assets

Deterministic builders are stored in `manuscript/source/scripts/`. Principal
entry points include:

- `v19_build_figures23.py`: current development-only verification and TCGA candidate-bank geometry;
- `v19_build_figures45.py`: current TCGA benchmark and AMP-AD center-weighting displays;
- `supplementary_data/cv_score_sensitivity/run_cv_score_sensitivity.py`: self-contained fixed-score reweighting analysis (standard library; no refitting);
- `build_cgga_figure5.py`: CGGA compression and agreement display;
- `build_radiomics_s20.py`: aggregate VGH radiomics display;
- `build_locking_simulation.py`: controlled locking-layer simulation display.

Each builder documents its aggregate inputs and output scope. Rebuilding a
display from included source tables is distinct from rerunning GA, RFECV, Direct
selection, model fitting, or held-out evaluation.

## Controlled-input boundary

Participant-level and provider-controlled inputs, identifiers, imaging data,
prediction-level records, model objects, and run checkpoints are excluded.
Complete raw-to-aggregate reproduction requires the relevant data-use approval,
source-specific preprocessing, and separately retained run artifacts. Missing
controlled inputs must not be fabricated or substituted.

The maintained implementation and executable package tests are in the
[companion software repository](https://github.com/junseoparkX/wrapevofs-package).

## v19 additions

The fixed-bank sensitivity package retains exact input/output/protocol checksums.
Its two input CSVs contain feature masks and development fold scores, not participant rows.
The equal-center package supplies 12 aggregate contrasts and 48 center-specific contrasts;
recomputation of those intervals requires separately authorized saved predictions.
Current polished supplementary PDF/SVG files include paths under
`v19_work/supplement_polish_20261105/modern/figures/` as referenced by the unchanged TeX.
The adjacent source_data folder retains aggregate CSV copies. Archived presentation
scripts document the local rendering route and may require the original plotting
helpers/fonts or archived SVG sources; the compiled PDFs and editable SVGs are supplied.
This distinction does not affect compilation of the manuscript from the supplied TeX.
Cover letters, publisher forms and administrative correspondence remain local submission
collateral rather than public research data.
