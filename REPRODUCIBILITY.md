# Reproducibility guide

## Build the manuscript

The manuscript uses LuaLaTeX. From `manuscript/source/`:

```bash
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error main.tex
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error supplementary_information.tex
```

The verified outputs contain 16 main-article pages and 48 Supplementary pages. The current build has no unresolved citations or references and no overfull or underfull boxes.

## Validate frozen results and presentation

Install the Python dependencies from the repository root, then run from `manuscript/source/`:

```bash
python scripts/validate_final_qa_frozen_values.py
python scripts/validate_main_panel_labels.py
python scripts/validate_cgga_figure5_provenance.py
python scripts/validate_radiomics_integration.py
python scripts/validate_locking_simulation_integration.py
python scripts/validate_display_citations.py
```

These validators check frozen numerical invariants, panel-label consistency, source-table mappings, radiomics integration boundaries, the controlled locking-layer simulation, and display-citation coverage. The fully nested TCGA and matched-selector audits are documented in `documentation/validation/VALIDATION_REPORT.md` and supported by aggregate records under `supplementary_data/tcga_nested_v1_v2/` and `supplementary_data/tcga_matched_comparator/`.

## Rebuild presentation assets

Deterministic builders are stored in `manuscript/source/scripts/`. Principal entry points include:

- `build_main_figure2.py` — updated-configuration mechanism verification;
- `build_cgga_figure5.py` — CGGA compression, incremental effects, and agreement;
- `build_tcga_nested_figures.py` — fully nested TCGA main and supplementary displays;
- `build_postfreeze_results.py` — post-freeze AMP-AD result figures;
- `build_radiomics_s20.py` — aggregate private-radiomics display;
- `build_locking_simulation.py` — controlled locking-layer simulation display;
- `build_submission_archive.ps1` — clean manuscript-source archive.

Each builder documents its inputs and output scope. Figure generation from included aggregate tables is distinct from rerunning GA, RFECV, Direct selection, model fitting, or held-out evaluation.

## Controlled-input boundary

Participant-level and provider-controlled inputs, raw predictions, model objects, and run checkpoints are excluded. Complete raw-to-aggregate reproduction may require authorized source access, source-specific preprocessing, and separately retained run artifacts. Missing controlled inputs must not be fabricated or replaced.

The companion software implementation and tests are maintained at [junseoparkX/wrapevofs-package](https://github.com/junseoparkX/wrapevofs-package).
