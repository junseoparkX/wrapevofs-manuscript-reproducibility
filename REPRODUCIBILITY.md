# Reproducibility guide

## Build the submission PDFs

The manuscript is designed for LuaLaTeX and Overleaf. From `manuscript/latex_v14_overleaf/`:

```bash
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error main.tex
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error supplementary_information.tex
```

The verified outputs contain 19 main-article pages and 46 Supplementary pages. A clean extraction of the submission source independently rebuilt both entry points with no unresolved references or overfull/underfull boxes.

## Validate frozen results and figure presentation

From `manuscript/latex_v14_overleaf/` with the Python requirements installed:

```bash
python scripts/validate_final_qa_frozen_values.py
python scripts/validate_main_panel_labels.py
python scripts/validate_cgga_figure5_provenance.py
python scripts/validate_radiomics_integration.py
python scripts/validate_locking_simulation_s24_integration.py
```

The validators check frozen numerical invariants, within-figure panel-label consistency, source-table mappings, radiomics integration boundaries, and the controlled locking-layer simulation integration. They do not rerun GA or empirical feature selection. The completed fully nested TCGA results and their independent numerical audit are documented in `V14_VALIDATION_REPORT.md` and the source records under `supplementary_data/tcga_nested_v1_v2/`.

## Rebuild presentation assets

Relevant deterministic builders are kept in `manuscript/latex_v14_overleaf/scripts/`. Each script documents its frozen aggregate inputs and output scope. In particular:

- `build_v12_main_figure2.py` rebuilds the updated-mechanism verification figure;
- `build_cgga_figure5.py` rebuilds the current CGGA main figure;
- `build_cgga_s9_clean.py` rebuilds Supplementary Figure S9;
- `prepare_170mm_figure_assets.py` creates the continued-page S8 and S19 assets;
- `build_postfreeze_results.py` rebuilds the post-freeze AMP-AD result figures;
- `render_locking_simulation_s24.ps1` renders the controlled locking-simulation figure;
- `build_tcga_nested_figures.py` rebuilds the fully nested TCGA Figure 6 and supplementary audit figures from the preserved aggregate sources.

These are presentation or frozen-summary routes. Their presence does not imply that restricted raw-to-result workflows are publicly executable.

## Controlled-input boundary

Participant-level ADNI, AMP-AD, CGGA, and private-radiomics inputs remain controlled or provider supplied. Complete raw-to-aggregate reproduction may require authorized data access, source-specific preprocessing, and separately retained run artifacts. Missing controlled inputs must not be fabricated, imputed, or replaced.

The companion software implementation and tests live at [junseoparkX/wrapevofs-package](https://github.com/junseoparkX/wrapevofs-package).
