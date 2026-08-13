# WrapEvoFS manuscript V14 — fully nested TCGA integration

V14 preserves V13 as immutable provenance and adds the completed two-repeat, five-fold fully nested TCGA GBM/LGG analysis. Figure 6 emphasizes empirical-regret feasibility, eligible-pool representativeness, and participant-partition sensitivity. Supplementary Figures S25--S27 provide the complete candidate-bank audit, agreement and composition summaries, and the six-method repeated-OOF comparator audit. The integrated claims remain bounded: this is repeated internal OOF evidence, not external validation, biomarker stability, equivalence, or predictive superiority.

Package repository (private during revision): <https://github.com/junseoparkX/wrapevofs-package>

Manuscript reproducibility repository (private during revision): <https://github.com/junseoparkX/wrapevofs-manuscript-reproducibility>

## Build

Use LuaLaTeX and set `main.tex` or `supplementary_information.tex` as the root document.

```sh
latexmk -lualatex main.tex
latexmk -lualatex supplementary_information.tex
```

## Submission-facing structure

- `main.tex`: title, abstract, main article, and references.
- `supplementary_information.tex`: independently compilable Supplementary Information.
- `sections/main_text.tex`: Introduction, Results, Discussion, Methods, and declarations.
- `sections/supplementary.tex`: the executable algorithm under Supplementary Methods, formal properties, complexity, 27 supplementary figures, and 26 numbered supplementary tables.
- `figures/figure_1.pdf` and `figures/figure_1.svg`: supplied updated workflow, with vector/editable source retained.
- `figures/figure_2.pdf` and `figures/figure_2.svg`: native 180-mm updated-configuration verification figure.
- `figures/figure_3.png` and `figure_4.png`: archived ADNI and AMP-AD demonstration figures in first-appearance order.
- `figures/figure_5.pdf`, `figure_5.svg`, and `figure_5.png`: native 170-mm CGGA quantitative redesign with vector sources and a 600-dpi fallback.
- `figures/figure_6.pdf`, `figure_6.svg`, and `figure_6.png`: native 170-mm fully nested TCGA locking-geometry figure.
- `figures/figure_s25_repeat_1.pdf`, `figure_s25_repeat_2.pdf`, `figure_s26.*`, and `figure_s27.*`: TCGA candidate audit, agreement, and repeated-OOF comparator figures.
- `scripts/build_v12_main_figure2.py`: deterministic Figure 2 builder using frozen source tables only.
- `scripts/build_cgga_figure5.py`: deterministic Figure 5 builder using the frozen aggregate tables in `supplementary_data/cgga_figure5/` only.
- `scripts/build_gridfree_figure4_svg.py`: deterministic presentation-only cleanup of the preserved Figure 4 SVG; it removes background grids and an empty annotation box without changing scientific values.
- `scripts/build_postfreeze_results.py`: deterministic builder for additive Supplementary Figures S21--S23 and Tables S22--S24 from frozen post-lock aggregate outputs.
- `scripts/build_radiomics_s20.py`: deterministic Supplementary Figure S20 builder using non-identifying aggregate radiomics source tables only.
- `scripts/build_tcga_nested_figures.py`: deterministic Figure 6 and Supplementary Figures S25--S27 builder using the frozen figure-source tables in `supplementary_data/tcga_nested_v1_v2/`.
- `scripts/count_v13_submission_words.py`: reproducible title, abstract, legend, and display-item count.
- `scripts/build_v13_submission_archive.ps1`: deterministic clean-archive builder that excludes LaTeX intermediates, local caches, and rendered QA scratch files.

## Main display map

1. Updated WrapEvoFS workflow and leakage boundary.
2. Development-only updated-configuration mechanism verification.
3. ADNI archived multiclass demonstration.
4. AMP-AD archived multicenter demonstration.
5. CGGA archived binary demonstration.
6. Fully nested TCGA GBM/LGG locking geometry and partition sensitivity.

The three main tables summarize datasets, archived regret/compression, and the objective-flattening audit. Figures 1--4 retain their approved 180-mm placements; redesigned Figure 5 is placed at its native 170-mm width. Line art is retained as PDF/SVG where a native vector source exists; raster archival figures are not falsely described as vector.

## Scientific boundary

The updated 120-run comparison in Figure 2 is development-only. The frozen 24-condition AMP-AD signatures were subsequently evaluated once on their corresponding held-out centers and are reported additively in Supplementary Figure S21 and Table S22; held-out outcomes did not alter feature sets, locks, or parameters. Archived main Figures 4 and 5 remain complementary original-configuration demonstrations. The private radiomics analysis is a supplementary internal fixed-split demonstration; its two feature spaces share participants, and the perturbation-filtered view is not an external cohort. The formal locking guarantee is limited to the configured empirical development-CV score gap; it does not establish predictive superiority, external validity, biomarker stability, or unbiased generalization performance.
