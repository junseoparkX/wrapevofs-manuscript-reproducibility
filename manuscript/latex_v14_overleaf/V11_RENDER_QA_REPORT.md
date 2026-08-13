# V11 render and validation QA

## Build

- Compiler: LuaLaTeX via `latexmk`, with BibTeX.
- Output: `main.pdf`, 49 pages.
- Final build log: no LaTeX warnings, undefined references, overfull/underfull boxes, float-too-large warnings, missing characters, or fatal errors.
- Final PDF SHA-256: `1329c59ee37242c977e5a1004f012972cb9dc067d8e7eca68ab70098f39d98c7`.

## Visual inspection

All 49 pages were rendered to PNG at 110 dpi in `tmp/pdfs/v11_final_qa_final` and inspected as five contact sheets. Main Figures 2-5, Supplementary Figures S7-S19, and Supplementary Tables S14-S20 were also inspected page-by-page at original rendered resolution. Checks covered clipping, overlap, axis and panel labels, font substitution, caption placement, split-figure continuity, table width, and page margins.

Results:

- Figure 1 is unchanged and its checksum guard passes.
- Main figure numbering is stable: Figures 1-5, with updated evidence printed as Figure 5 despite appearing first in Results.
- New Figure 5, corrected S16, rebuilt S18, and continued S8/S19 are legible and unclipped.
- All displayed non-Figure-1 assets are 170 mm wide.
- Background plot grids are absent; scientific reference lines remain.
- Panel labels are bold; plot titles, annotations, values, and axis labels are normal weight in rebuilt V11 figures.
- New Tables S18-S20 fit within the text block and retain denominators and NA disclosures.

## Scientific guards

- `scripts/validate_figure1_freeze.py`: PASS.
- Package proposition/property suite: `93 passed, 1 warning` using `pytest -q --basetemp .pytest_tmp_v11_2`; the sole warning was a `Liblinear` convergence warning in a small artifact-export test, with no failure.
- Existing-artifact provenance records `ga_rerun=false`, `rfecv_rerun=false`, `direct_selection_rerun=false`, and `held_out_inputs_used=false`.
- Missing Rush mask-dependent cells are reported unavailable rather than reconstructed.

## Overleaf-package validation

`WrapEvoFS_LaTeX_V11_Overleaf.zip` was extracted into a new directory and rebuilt there with the packaged `.latexmkrc`, LuaLaTeX, and BibTeX. The clean extraction produced 49 pages with zero LaTeX warnings, undefined references, overfull/underfull boxes, float-size warnings, missing characters, or fatal errors. The packaged Figure 1 checksum remained unchanged.
