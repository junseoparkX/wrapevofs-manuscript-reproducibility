# Conservative scientific refinement

## Scope

This pass refined interpretation and presentation without adding an analysis, changing a numerical result, or modifying the Supplementary Information. Figure 6 data, geometry, axes, colors, markers, and source files were preserved.

## Exact narrative changes

1. **Abstract, fully nested TCGA sentence.** Replaced the compressed statement that medoid locking “changed 11 selections with positive eligible-pool representativeness gain” with two sentences stating that 11 selections differed from the highest-score candidate and that the positive gain was expected from representative locking. The strict 30-of-30 empirical-regret result and participant-partition sensitivity statement were retained.
2. **Results 2.5, first paragraph.** Split the 11-bank result into a descriptive count followed by: “As expected from the representative-locking rule, all 11 departures from the highest-score candidate produced positive eligible-pool mean-Jaccard gains (median 0.0429; Figure 6a,b).” This prevents an algorithmic consequence of medoid selection from being presented as an independent discovery.
3. **Results 2.5, second paragraph.** Retained the reported within-bank Jaccard (0.115), across-outer-fold Jaccard (0.0357), 42-of-60 cardinality-similarity count, and 33-of-42 low-Jaccard count. Recast their interpretation to state directly that similar signature size across outer partitions did not imply similar feature identity.
4. **Figure 6 caption.** Consolidated the repeated three-part exclusion list into the positive, bounded description that the agreement estimates characterize candidate-search and participant-partition sensitivity within this cohort. The explicit biomarker-stability boundary remains in the adjacent Results paragraph, and the broader external-validity and predictive-claim boundaries remain in the Abstract, Discussion, limitations, and final summary.
5. **Methods 4.9.** Added Ceccarelli et al. (2016) to the sentence defining the four historical histological labels.

## Citation order

- The two original TCGA references remain references 18 and 19.
- Ceccarelli et al. (2016) is reference 20 at its first appearance in Methods 4.9.
- References that first appear afterward shift by one; the two ADNI references are now 21 and 22.
- Figure 6 retains no Ceccarelli citation in its caption.

## Figure 5a legibility refinement

- The three compression annotations retain the same values (54%, 65%, and 73% reductions).
- Labels use a true minus sign, slightly larger bold text, a small opaque white backing, and a higher drawing order so that error bars and connecting arrows no longer obscure the text.
- Plot data, confidence intervals, axes, colors, markers, and panel geometry were not changed.

## Validation

- `main.tex` compiled successfully under LuaLaTeX to 19 pages.
- No undefined citations or references and no overfull or underfull boxes remain in the final log.
- Figure 5a was inspected in the native figure output and on page 8 of the compiled manuscript.
- The revised Abstract, Figure 6 Results text, Figure 6 caption, Methods 4.9 citation, and bibliography were inspected in rendered manuscript pages.
- Figure 1 PDF/PNG/SVG hashes, Figure 6 PDF hash, and the 46-page Supplementary PDF hash remained unchanged.
- No GA, model fitting, held-out evaluation, or empirical feature-selection analysis was rerun.

## Changed-file inventory

- `main.tex`
- `sections/main_text.tex`
- `references.bib`
- `scripts/build_cgga_figure5.py`
- `figures/figure_5.pdf`
- `figures/figure_5.svg`
- `figures/figure_5.png`
- `supplementary_data/cgga_figure5/figure5_manifest.json`
- `main.pdf` and its routine LaTeX build artifacts
- `documentation/validation/VALIDATION_REPORT.md`
- `documentation/validation/SCIENTIFIC_REFINEMENT_REPORT.md`

The submission archive is generated on demand and is not tracked in Git.
