# V14 validation report

## Build

- `main.tex`: PASS under LuaLaTeX; 19 pages.
- `supplementary_information.tex`: PASS under LuaLaTeX; 46 pages.
- Undefined references or citations: none.
- Overfull boxes: none in the final logs.
- Main figures: six, numbered and cross-referenced correctly.
- Supplementary figures: S1--S27, with S13 and S16 continued on a second page without consuming a new figure number.
- Supplementary tables: S1--S26, printed monotonically after first-citation renumbering.

## Figure geometry and visual QA

- Figure 6: 481.89 pt wide, equivalent to 170 mm; one page.
- Figure S16 pages: 481.89 pt wide, equivalent to 170 mm; two standalone one-page PDFs.
- Figures S17 and S18: 481.89 pt wide, equivalent to 170 mm.
- Figure 6 uses one exact 2 by 2 subplot grid. The `a)`/`c)` panels share the left-column x origin and width; the `b)`/`d)` panels share the right-column x origin and width.
- The top margin was expanded and the `a)`/`b)` labels were lowered within that margin.
- Panel labels, axis labels, tick labels, data marks, and legends were inspected at figure resolution and in the compiled manuscript. No overlap or clipping was observed.
- Every page of the 19-page main PDF and 46-page Supplementary PDF was rendered to PNG and inspected as page sheets; figure, continuation, and table-transition pages were additionally inspected at higher resolution.
- An unused two-page S16 assembly remains excluded; the two independently verified standalone page PDFs are the manuscript sources.
- Figure 1 PDF, PNG, and SVG SHA-256 values remain identical to the recorded freeze values.
- Final logs contain no undefined references or citations and no overfull or underfull boxes.

## Numerical and provenance checks

- Candidate banks: 30; saved candidates: 150.
- All selected empirical regrets satisfy `regret <= 0.01`; maximum 0.0097844729101124.
- Current medoid differs from canonical highest score in 11 banks; all 11 have positive eligible-pool mean-Jaccard gain; median gain 0.04285714285714291.
- Mean within-bank candidate Jaccard: 0.1148828264922085.
- Mean across-outer-fold locked-set Jaccard: 0.0356916313322161.
- Forty-two of 60 outer-fold pairs have cardinality similarity at least 0.9; 33 of those also have Jaccard at most 0.05.
- All Figure 6 and S16--S18 PDFs in V14 are byte-identical to their independently audited analysis outputs; only their printed Supplementary numbers changed.
- Source CSVs and the figure-source workbook are included under `supplementary_data/tcga_nested_v1_v2/`; participant-level outer predictions and the provider-organized source matrix are not included.

## Citation and claim audit

- Supplementary Figure S16 is cited with the complete candidate-level locking audit claim.
- Supplementary Figure S17 is cited with conditional candidate agreement and participant-partition sensitivity claims.
- Supplementary Figure S18 is cited with repeated-OOF comparator and compression claims.
- Supplementary figures and tables are numbered by first citation in the main text; items cited only in later secondary-analysis sections follow the primary empirical sequence.
- TCGA citations `ref44`, `ref45`, and `ref46` resolve in the compiled bibliography; Ceccarelli et al. (2016) appears as reference 20 after the two original TCGA studies.
- No statement claims predictive superiority, equivalence, biomarker stability, external validity, or unbiased generalization from the locking guarantee.

## Conservative scientific refinement

- The 11 positive eligible-pool mean-Jaccard gains are explicitly described as expected from the representative-locking rule rather than as an independent discovery.
- The TCGA Results now state directly that similar selected-set sizes did not imply similar feature identity across outer partitions.
- The repeated claim-boundary list in the Figure 6 caption was shortened while the explicit boundaries remain in the adjacent Results text, Abstract, Discussion, limitations, and summary.
- Figure 5a compression labels were visually separated from error bars and arrows without changing any plotted value or geometry.
- Full details are recorded in `V14_CONSERVATIVE_SCIENTIFIC_REFINEMENT_CHANGELOG.md`.

## Remaining submission blocker unrelated to V14

The private radiomics research-ethics-board identifier and consent or waiver wording still require source-institution confirmation before submission, as explicitly marked in the manuscript.

## Clean submission archive

- `manuscript/WrapEvoFS_LaTeX_V14_Submission.zip` was built from the final V14 tree.
- LaTeX caches and auxiliary build artifacts were excluded; both compiled PDFs and all new TCGA figures are present.
- The final archive size, entry count, and SHA-256 are reported externally to avoid a self-referential archive hash.
