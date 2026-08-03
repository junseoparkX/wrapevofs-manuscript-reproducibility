# V9 AMP-AD Rush objective-sensitivity integration

## Integration decision

The completed six-condition AMP-AD Rush rerun is integrated as a limited, development-only recommended-mode mechanism sensitivity. It is not promoted to a main efficacy result, and Main Figures 1--5 are unchanged.

The latest strict locking rule is authoritative: absolute development-CV regret tolerance 0.01, minimum eligible-pool size 1, singleton pools permitted, and no fallback expansion. The earlier two-candidate fallback aggregate is not used. Consequently, selected mean Jaccard is NA for SVM-L1/Reference-cap and Boruta-RF/Reference-cap.

## Manuscript changes

- Author block: corrected the author name to Leonard J. Foster and added ORCID identifiers for Leonard J. Foster (0000-0001-8551-4817) and Huan Zhong (0000-0002-7294-2254).
- Abstract: added one concise sentence reporting the prospective development-only mechanism evidence and explicit held-out non-access.
- Methods: added `Development-only AMP-AD Rush recommended-mode sensitivity`.
- Results: added `Prospective recommended-mode objective sensitivity in AMP-AD Rush` and updated the A/B/C category statement.
- Discussion: added a focused interpretation of the prospective mechanism evidence.
- Limitations: replaced the outdated statement that all prospective recommended-mode execution remained future work with the narrower need for end-to-end prespecified held-out assessment.
- Conclusion: added the limited prospective development-only finding without making a predictive claim.
- Supplementary Information: added Supplementary Figure S18 and Supplementary Table S16.

## New publication artifacts

- `figures/figure_s18.svg`: editable vector source.
- `figures/figure_s18.pdf`: vector manuscript figure.
- `figures/figure_s18.png`: 170-mm-wide, 600-dpi raster figure.
- `supplementary_data/Table_S16_AMPAD_Rush_Objective_Sensitivity.csv`
- `supplementary_data/Table_S16_AMPAD_Rush_Objective_Sensitivity.md`
- `supplementary_data/Table_S16_AMPAD_Rush_Objective_Sensitivity.tex`
- `supplementary_data/S18_S16_provenance.json`

## Verified reporting values

- Six branch--cap conditions, five seeds each, 30 full GPU GA runs.
- Aggregate absolute target deviation: 110 to 48; mean: 18.3333 to 8.0000.
- Diagnostic zero legacy-truncated run-best values: 4/30 to 0/30.
- Diagnostic all-zero generations: 362 to 133.
- Recommended uniform parent-sampling fallbacks: 0.
- Mean recommended-minus-legacy locking-score difference: -0.001139; range -0.009964 to 0.010040.
- Aggregate runtime: approximately 45,381.90 seconds (12.61 hours).
- Strict singleton selected mean Jaccard: NA for SVM-L1/Reference-cap and Boruta-RF/Reference-cap.

## Claim boundaries retained

- Rush held-out labels, predictions, and outcomes were not accessed or evaluated.
- No claim of improved held-out performance, transportability, external validation, predictive superiority, equivalence, non-inferiority, biomarker stability, or clinical utility was added.
- Historical legacy results, retrospective strict re-locking, and the prospective development-only rerun remain explicitly distinguished.
- Historical ADNI, CGGA, and full AMP-AD results were not relabeled as recommended-mode results.

## Validation

- LuaLaTeX/latexmk build completed successfully: 42 pages.
- Cross-references resolved and no LaTeX errors remained.
- All 42 pages were rendered to PNG for visual inspection; Supplementary Figure S18 and Supplementary Table S16 were additionally inspected at full-page resolution.
- Revision after visual review: moved the S18 panel labels into dedicated whitespace and removed the panel-a in-plot annotation so labels do not obscure marks or axes.
