# Figure palette and Supplementary-order validation

## Scope

This pass changed presentation and document organization only. It did not rerun a GA, refit an empirical analysis, change a feature set, or alter an empirical result.

## Main-text prose

- The remaining em-dash construction in the main text was recast as a conventional sentence describing 44%--70% feature-count reductions and heterogeneous held-out effects.
- Searches of `main.tex` and `sections/main_text.tex` found no remaining Unicode em dash or LaTeX triple-hyphen em dash.

## Figure palette

- Figure 1 was excluded and remained byte-identical to its frozen assets.
- Figures 2--6 and Supplementary Figures S1--S27 use a muted publication tone.
- Repeated branch semantics are consistent: SVM-L1 `#1F7A8C`, XGBoost `#C78A0A`, and Boruta-RF `#8B5E83`.
- Original or neutral comparisons use gray/slate; exceptional stress-condition highlighting uses muted terracotta.
- Static raster recoloring is reproducible from preserved first-use sources under `supplementary_data/figure_palette_sources/`; the JSON manifest records source hashes, output hashes, and changed-pixel counts.

## Supplementary order

- Figures are printed as S1--S27 in first main-text citation order.
- Tables are printed as S1--S26 in first main-text citation order.
- Continuation pages remain attached to S13 and S16 and do not consume new numbers.
- A previously forced S5 figure placement was normalized so it no longer preceded S1--S4.
- Table floats were made non-floating at their ordered insertion points so they no longer moved behind later `longtable` items.
- `SUPPLEMENTARY_FIRST_CITATION_RENUMBERING.json` is the authoritative old-to-new mapping record.

## Build and render QA

- `main.tex`: PASS under LuaLaTeX, 19 pages.
- `supplementary_information.tex`: PASS under LuaLaTeX, 46 pages.
- Undefined references/citations: none.
- Overfull/underfull boxes: none.
- Every page of both PDFs was rendered to PNG contact sheets and visually inspected. No clipped panel labels, overlapping axes, displaced continuation labels, reversed figure order, reversed table order, or unintended blank pages were observed.

## Frozen and output hashes

- Figure 1 PDF: `eb5b604c5c6aa53f92cab46381edbc408101cc9488afc092bb1cf5daf4c9767c`
- Figure 1 PNG: `db0cfa30cc67377e1fed49d224f2b839eb19900addeeff00dd5945bf9ccc6bb1`
- Figure 1 SVG: `ba6a648daa73675e9f5d7418c81a5fd7a5209d8d7bb77aee7a328a34ebbe35fb`
- Final main PDF: `d89262ba52a55b1a512bd9ef83798e3ea5ef088755f31f4bd2189e5abb56b9f1`
- Final Supplementary PDF: `32117b8ef1f776dad7693b423502046b073308f23a4683db7915b8c466b4af32`

## Claim boundary

These presentation and ordering changes provide no new evidence of predictive superiority, external validity, biomarker stability, equivalence, or unbiased generalization.
