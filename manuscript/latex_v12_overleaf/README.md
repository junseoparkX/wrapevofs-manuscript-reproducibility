# WrapEvoFS manuscript V12 — Nature Communications-informed submission package

V12 preserves V11 as immutable provenance and reorganizes the manuscript for a clearer first read. The main article and Supplementary Information build independently. The archived ADNI, AMP-AD, and CGGA analyses were not rerun. A subsequently completed private-radiomics bundle was audited and integrated in place: its 30 transferred GA jobs were not rerun, and the bundle's frozen strict locking and one-time held-out aggregation stages were executed once after all six development signatures were locked.

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
- `sections/supplementary.tex`: the complete algorithm under Supplementary Methods, formal properties, complexity, 23 supplementary figures, and 24 numbered supplementary tables.
- `figures/figure_1.pdf` and `figures/figure_1.svg`: supplied updated workflow, with vector/editable source retained.
- `figures/figure_2.pdf` and `figures/figure_2.svg`: native 180-mm updated-configuration verification figure.
- `figures/figure_3.png` and `figure_4.png`: archived ADNI and AMP-AD demonstration figures in first-appearance order.
- `figures/figure_5.pdf`, `figure_5.svg`, and `figure_5.png`: native 170-mm CGGA quantitative redesign with vector sources and a 600-dpi fallback.
- `scripts/build_v12_main_figure2.py`: deterministic Figure 2 builder using frozen source tables only.
- `scripts/build_cgga_figure5.py`: deterministic Figure 5 builder using the frozen aggregate tables in `supplementary_data/cgga_figure5/` only.
- `scripts/build_gridfree_figure4_svg.py`: deterministic presentation-only cleanup of the preserved Figure 4 SVG; it removes background grids and an empty annotation box without changing scientific values.
- `scripts/build_postfreeze_results.py`: deterministic builder for additive Supplementary Figures S21--S23 and Tables S22--S24 from frozen post-lock aggregate outputs.
- `scripts/build_radiomics_s20.py`: deterministic Supplementary Figure S20 builder using non-identifying aggregate radiomics source tables only.
- `scripts/count_v12_submission_words.py`: reproducible title, abstract, legend, and display-item count.
- `scripts/build_v12_submission_archive.ps1`: deterministic clean-archive builder that excludes LaTeX intermediates, local caches, and rendered QA scratch files.

## Main display map

1. Updated WrapEvoFS workflow and leakage boundary.
2. Development-only updated-configuration mechanism verification.
3. ADNI archived multiclass demonstration.
4. AMP-AD archived multicenter demonstration.
5. CGGA archived binary demonstration.

The three main tables summarize datasets, archived regret/compression, and the objective-flattening audit. Figures 1--4 retain their approved 180-mm placements; redesigned Figure 5 is placed at its native 170-mm width. Line art is retained as PDF/SVG where a native vector source exists; raster archival figures are not falsely described as vector.

## Scientific boundary

The updated 120-run comparison in Figure 2 is development-only. The frozen 24-condition AMP-AD signatures were subsequently evaluated once on their corresponding held-out centers and are reported additively in Supplementary Figure S21 and Table S22; held-out outcomes did not alter feature sets, locks, or parameters. Archived main Figures 4 and 5 remain complementary original-configuration demonstrations. The private radiomics analysis is a supplementary internal fixed-split demonstration; its two feature spaces share participants, and the perturbation-filtered view is not an external cohort. The formal locking guarantee is limited to the configured empirical development-CV score gap; it does not establish predictive superiority, external validity, biomarker stability, or unbiased generalization performance.
