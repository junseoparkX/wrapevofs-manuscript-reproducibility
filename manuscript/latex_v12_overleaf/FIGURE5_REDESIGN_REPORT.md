# Figure 5 redesign report

## Editorial decision

The complete reviewer-revision report was reread before redesign. Its central Figure 5 concern was that a second workflow/cohort schematic repeated information already carried by Figure 1 while using scarce main-text space that could instead address the scientific question: what does the stochastic GA-and-locking stage add after RFECV?

The redundant schematic was therefore removed. Figure 5 now presents three equal-size quantitative panels in one row at a native width of 170 mm:

1. **a) Compression and held-out AUROC:** Direct and locked-medoid feature counts with the frozen held-out AUROC estimates and confidence intervals. Arrows report the existing 54%--73% feature reductions.
2. **b) Increment beyond RFECV-only:** paired locked-medoid-minus-RFECV-only differences for AUROC, AUPRC, and balanced accuracy. The nine frozen intervals use 2,000 common class-stratified bootstrap resamples with seed 42; every interval includes zero.
3. **c) Five-run agreement:** mean pairwise Jaccard and chance-corrected Nogueira agreement without and with target-size guidance. This panel shows that target-size guidance changed feature-set size but did not uniformly improve agreement.

This layout preserves the positive compression result, exposes uncertainty, and avoids implying that the GA stage or locked medoid is predictively superior to RFECV-only selection. It also keeps seed agreement distinct from participant-resampling stability, biomarker reproducibility, and external validation.

## Presentation specification

- Native figure width: 170 mm.
- Layout: one row, three equal-width panels.
- Background plot grids: disabled.
- Panel labels: bold `a)`, `b)`, and `c)` only, all at the same size.
- Panel titles and all other labels: regular weight.
- Outputs: PDF and SVG vector artwork plus a 600-dpi PNG fallback.
- Main manuscript inclusion: the PDF vector asset at 170 mm.

## Traceability and scientific boundary

The builder reads only manuscript-local aggregate CSVs in `supplementary_data/cgga_figure5/`. Those tables are exact extracts of existing frozen WrapEvoFS outputs; no empirical value was edited. The corresponding source paths and checksums are recorded in `supplementary_data/cgga_figure5/README.md` and `figure5_manifest.json`. Exact plotting-library versions are pinned in the adjacent `requirements.txt` and recorded in the generated manifest.

No GA, RFECV, Direct selection, model fitting, held-out prediction generation, feature selection, or locking was rerun. The bootstrap intervals in panel b were not recomputed: they are existing verified frozen outputs copied into the figure-specific source table. Held-out results were joined only after development-only selection and did not determine a run, a locking rule, or the tolerance.

## Reproducibility and validation

Run from `manuscript/latex_v12_overleaf`:

```sh
python scripts/build_cgga_figure5.py
```

The full-repository provenance audit is independently executable as `python manuscript/latex_v12_overleaf/scripts/validate_cgga_figure5_provenance.py`. It checks the four frozen upstream file hashes and exact panel-column mappings, including the two-source join used for panel c.

The builder validates row completeness, finite values, confidence-interval ordering and point containment, the frozen bootstrap configuration, and the documented fact that all nine paired intervals include zero. Two consecutive builds produced identical PDF, SVG, and PNG hashes:

| Output | SHA-256 |
|---|---|
| `figures/figure_5.pdf` | `a9ee3d8aafd75010ec5271248274bed717a49a4530299f98122a3e764cba6274` |
| `figures/figure_5.svg` | `3b421d840ea949bc10dd0d97f7990b919563aee619df87173de118f44a6c74eb` |
| `figures/figure_5.png` | `1f1b27f5d15b2ba2e10f0955470f909279ecfea8c23f9b4bb03c89227273af2c` |

The revised main manuscript compiled to 14 pages with no warning-pattern, undefined-reference, overfull/underfull, or missing-character matches. Figure 5 and its caption were inspected on the rendered full manuscript page; no overlap, clipping, hidden label, missing axis, or unintended grid was found.
