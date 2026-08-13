# V12 validation report

## Build and PDF checks

- `main.tex`: LuaLaTeX/BibTeX build passed; 16 pages; SHA-256 `021ffb0d9a263116c4653f5994b3ff2dcdb9aff62ac35eebf9bb0ecd6c423671`.
- `supplementary_information.tex`: independent LuaLaTeX/BibTeX build passed; 42 pages; SHA-256 `b9f451183daa1ca309b0e3bb0fdb5bc5ca02386b2a2a4f863590b3dbb3714d25`.
- Final logs contain zero matches for LaTeX/package warnings, undefined references, multiply defined labels, overfull/underfull boxes, duplicate destinations, or oversized floats.
- The declarations/ethics, post-freeze, and controlled-simulation updates build with zero final issue matches under the same audit pattern. The main article is 16 pages and Supplementary Information is 42 pages.
- The main and Supplementary title pages visually separate the three named authors from the required ADNI corporate acknowledgement; both first pages were rendered and inspected after the change.
- The changed main Results/Methods pages, restored main Figure 4/5 pages, and Supplementary Figures S20--S23/Tables S21--S24 pages were rendered and visually inspected. A later focused 180-dpi review of Supplementary pages 15, 27, and 28 verified the revised S9 and S21--S23 layouts. No clipping, obstructed axis/label, missing axis, table overflow, or orphan heading was found.
- Supplementary Figure S19 pages 24--25 were rendered at 180 dpi and inspected after the page-split repair. The first page contains complete panels a--b and the single complete a--d caption; the second contains only a continuation header followed by complete panels c--d. Panel b no longer crosses the page boundary, and all axes and labels are unobstructed.
- Main Figure panel labels were checked at source level. Within-figure sizes are Figure 1: 37.5 px for a)--b), Figure 2: 9.0 px for a)--d), Figure 3: 9.0 px for a)--c), Figure 4: 9.0 px for a)--c), and Figure 5: 10.2 px for a)--c). Figure 1 was the only mismatch and was normalized without changing scientific content or geometry.
- A fresh full-document contact-sheet review covered all 16 main pages and all 42 Supplementary pages after the simulation integration. Supplementary Figure S24 shares page 28 with S23 at readable 170-mm width, Supplementary Table S25 fits page 41 without clipping, and page 42 contains the independent Supplementary bibliography's single cited reference. No empty page, clipping, overflow, orphan heading, obstructed label, or missing axis was found.

## Numbering, terminology, and structure

- Main figure order is Figure 1 workflow, Figure 2 updated verification, Figure 3 ADNI, Figure 4 AMP-AD, and Figure 5 CGGA.
- Five main figures and three main tables yield eight main display items.
- The complete 23-step algorithm is in Supplementary Methods and is absent from the main article.
- Supplementary Figures S1--S24 and Supplementary Tables S1--S25 compile in the independent Supplementary PDF.
- Every main Figure 1--5 and Table 1--3, Supplementary Figure S1--S24, and Supplementary Table S1--S25 is cited or explicitly mentioned in the main article. Claim-level references distinguish ADNI, AMP-AD, CGGA, private-radiomics, and controlled locking-simulation displays. Supplementary Figure S24 and Supplementary Table S25 are cited in Results, Discussion, and Methods. The mapping is recorded in `V12_DISPLAY_CITATION_AUDIT.md`.
- Submission-facing text contains no “formerly … Figure” wording and no Figure 6.
- Manuscript-facing cap labels are Small, Reference, and High. Historical machine-readable identifiers were not rewritten.
- Singleton eligible-pool mean Jaccard remains undefined/missing, not one.

## Numerical invariants

- `scripts/validate_final_qa_frozen_values.py` passed.
- `scripts/validate_radiomics_integration.py` passed.
- Figure 2 and its builder use exactly 24 conditions and 120 full GPU GA runs.
- Target-deviation totals remain 216 versus 137; stress-excluded totals remain 135 versus 112.
- All-zero-generation totals remain 673 versus 333; stress-excluded totals remain 428 versus 267.
- Maximum updated selected regret remains 0.00835 and the configured absolute bound remains 0.01.
- The development-only 120-run comparison remains unchanged. V12 now separately reports the prespecified one-time post-freeze held-out evaluation of the 24 frozen AMP-AD signatures; held-out outcomes did not alter any feature set, lock, or parameter.
- The private-radiomics audit verified 30/30 transferred GPU GA jobs, 50/50 generations per job, run-artifact checksums, stable mask hashes, finite scores, and no held-out use during preparation or GA.
- The frozen bundle then completed six development locks before one held-out evaluation sequence. All six selected regrets were 0 at absolute $\delta=0.01$; no tolerance-expanding fallback occurred. A repeat aggregation call verified artifact integrity and did not repeat held-out evaluation.
- All 15 radiomics paired held-out AUROC intervals include zero. Participant-level predictions were excluded from the manuscript package.
- `scripts/validate_locking_simulation_s24_integration.py` passed. It matched all primary S25 values to the frozen summaries, verified the 513-scenario/4,995,000-bank workload and zero configured current-rule regret violations, checked mutually exclusive decision-path probabilities, and validated the S24/S25 manuscript citations and labels.
- The simulation uses hidden synthetic utility rather than AUROC and makes no claim of predictive superiority, unbiased generalization, external validity, participant-resampling stability, biomarker stability, or clinical utility.

## Counts, artwork, and source data

- Title: 9 words.
- Abstract: 194 words.
- Introduction + Results + Discussion: 2,859 words including headings and excluding legends/tables.
- Methods: 2,691 words including headings and excluding table body/legend; this includes the ethics/consent, AMP-AD provenance, concise generative-AI disclosure, post-freeze analysis boundaries, and controlled locking-simulation design.
- Figure legend counts: 87, 116, 54, 43, and 93 words.
- Figures 1--3 retain their approved placements. Main Figure 4 is the approved archived AMP-AD figure at 180 mm, with a deterministic grid-free presentation cleanup; main Figure 5 is the approved 170-mm CGGA figure. Neither was replaced by the post-freeze analyses. Figures 1 and 2 retain PDF/SVG line-art sources; Figure 3 remains honestly documented as an archival raster asset.
- `FIGURE_SOURCE_DATA_MANIFEST.csv` contains 49 panel/item rows covering every main and Supplementary figure and identifies the source route, supporting table/CSV, output asset, and availability boundary.
- Supplementary Figure S9 has deterministic PDF/SVG/PNG outputs from three frozen aggregate CSVs, a 170-mm canvas, no background plot grid, and bold a)--c) panel labels. The redundant selected-settings block was removed without changing any plotted value. Supplementary Figure S20 has deterministic PDF/SVG/PNG outputs, a native 170-mm canvas, no background plot grid, and bold a)–d) panel labels. Two consecutive rebuilds produced identical hashes in all three formats.
- Figure 5 was rebuilt twice from its three manuscript-local aggregate source tables; both builds produced identical PDF/SVG/PNG hashes. The builder verified the frozen bootstrap configuration and that all nine locked-medoid-minus-RFECV-only intervals include zero.
- Supplementary Figure S24 has deterministic PDF/SVG/PNG outputs, a native 170-by-67-mm canvas, no background plot grid, and bold a)--c) panel labels. Its builder validates frozen source values before writing outputs; the integration validator matched the rendered hashes recorded in the build and render manifests.
- `scripts/validate_cgga_figure5_provenance.py` passed, matching panels a and b to their frozen upstream tables and panel c to the exact size/Jaccard plus Nogueira source join under four pinned upstream checksums.
- The main bibliography now contains 29 compiled entries. Final logs contain no undefined citation or reference warning after adding the nine targeted references, including the primary PyRadiomics citation.

## Repository and release-state audit

- The inspected peer-review package clone is commit `63a608351abfb9521437c0dceef869b42ddfa292`, declares version `0.2.0`, and uses the BSD 3-Clause License naming Junseo Park (2026).
- The inspected package clone has no local Git tag. The manuscript therefore does not claim a GitHub Release, PyPI publication, archival DOI, or public repository state.
- Prior release validation recorded 111/111 tests, Ruff, compileall, metadata validation, wheel/sdist build, and source/wheel/sdist installation as passing; the author-provided GitHub Actions record showed the Python 3.10–3.12 and distribution jobs passing.
- The remaining operational requirement is to grant and test private editor/reviewer access before submission.
- AMP-AD attribution is resolved to the AMP-AD Diverse Cohorts Study (`syn51732482`; stable study DOI `10.7303/9618093`) with the portal and study-specific acknowledgement, Data Availability route, source-cohort ethics/consent statement, and Reddy et al. descriptor citation. The remaining explicit pre-submission requirements are the private-radiomics REB/IRB and consent/waiver basis, all-author declaration approval, and ADNI DPC upload/review.

## Preserved provenance

The V11 authoritative PDF remains unchanged at SHA-256 `1329c59ee37242c977e5a1004f012972cb9dc067d8e7eca68ab70098f39d98c7`. No V11 source file was edited. No ADNI, AMP-AD, CGGA, or radiomics GA, Direct, or RFECV analysis was rerun. V12 separately performed the authorized one-time post-freeze AMP-AD held-out evaluation, reconstructed the CGGA coherent benchmark from saved development-derived feature sets, and re-locked saved reduced-budget nested CGGA banks. The later controlled locking-simulation integration used only completed frozen summary outputs and did not rerun any simulation bank or empirical analysis.

## Post-freeze addendum (2026-08-08)

- Rush recovery verified 6/6 banks and 30/30 candidates, with no exact duplicate masks and exact agreement with archived and frozen selection records.
- The AMP-AD protocol completion sentinel records exactly 24 conditions, `ga_rerun=false`, and protocol SHA-256 `7bc7b27e00f7337654b6f81c1448a831ce3979129e68d14666389445d3ec93b5`.
- The CGGA coherent benchmark verified the reconstructed full matrix against the archived compact matrix and used no held-out outcome for feature selection.
- The five-fold saved nested-bank sensitivity accessed only the 214-participant development cohort; it did not access the original 92-participant held-out partition.
- Package locking tests passed 66/66 with a workspace-local pytest temporary directory.
- Two consecutive figure/table rebuilds produced identical SHA-256 values for approved main Figure 5 and every new Supplementary PDF/SVG/PNG figure, table source, and manifest. Two isolated headless renders of main Figure 4 also produced an identical PNG SHA-256.
- Main pages 7--8 and Supplementary pages 26--27 were rendered and inspected after restoring the approved main figures and moving the new analyses to S21--S23. No clipping, missing axes, obstructed labels, duplicate caption, table overflow, or blank page was found.
- Full details are in `POSTFREEZE_ANALYSIS_REPORT.md` and `POSTFREEZE_VALIDATION_REPORT.md`.

## Updated submission archive

- `WrapEvoFS_LaTeX_V12_Nature_Submission.zip` was rebuilt from the clean V12 source tree after the controlled-simulation and final figure-QA integrations; it contains 329 files and no excluded build/cache artifacts. The additional file is the non-rendered Figure 3 editable provenance source required for a self-contained panel-label validation. Final byte size and SHA-256 are recorded only in the external `V12_SUBMISSION_ARCHIVE_SHA256.txt` to avoid a circular self-hash inside the archive.
- A fresh extraction of that archive independently rebuilt `main.tex` to 16 pages and `supplementary_information.tex` to 42 pages. Both clean-extraction logs had zero warning/error-pattern matches, undefined or multiply defined references, overfull/underfull boxes, duplicate destinations, and oversized floats.
- The rebuilt archive includes the preserved main Figures 4 and 5, additive Supplementary Figures S21--S24 in reproducible vector/raster formats, Tables S22--S25, compact aggregate source data, builders, manifests, reports, and both PDFs. Direct archive inspection confirmed the S24 PDF and S25 LaTeX table are present.
- It contains zero LaTeX auxiliary/log files, zero render-QA images, and zero participant-level prediction rows, raw matrices, sample metadata, joblib inputs, split manifests, images, or masks. The filename `PROPERTY_TEST_REPORT.md` is a test report and not a prediction artifact.
