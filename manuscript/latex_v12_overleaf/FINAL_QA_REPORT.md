# Final pre-submission editorial and technical QA report

This QA pass was applied directly to the existing V12 working source. It was editorial and technical only: no GA, RFECV, Direct selection, held-out evaluation, Bayesian analysis, STABL, BLiP, bootstrap analysis, dataset, simulation, or empirical feature-selection experiment was rerun. Frozen numerical and decision-path checks passed.

## Critical errors fixed

- Corrected the main audit-table scope so the 36 archived AMP-AD configurations and the 24 matched original-versus-updated conditions are not conflated; the values 694 and 673 retain their distinct documented scopes.
- Removed unresolved declaration placeholders from the rendered article. Author-dependent statements are now isolated in `AUTHOR_CONFIRMATION_REQUIRED.md` and are not guessed.
- Replaced the generic bibliography style with the Nature style and repaired the supplied reference record structure that produced duplicate or malformed year fields. No unverified bibliographic facts were invented.
- Restored missing implementation-boundary rows to the Supplementary implementation correspondence table.
- Corrected the Supplementary Table S16 wording so two Rush singleton pools are distinguished from the 18 newly completed non-Rush pools.

## Formatting fixes

- Main Table 1 is a single compact three-row table; continuation numbering for the other main tables is dynamic and correct.
- The ADNI subsection heading and its interpretive paragraph now precede Figure 3.
- Main Table 3 uses the consistent ADNI, AMP-AD, CGGA dataset order.
- The duplicate Supplementary Information heading was removed and the complete 23-step algorithm was enlarged while remaining on one readable page.
- Manuscript-facing terminology is consistently Small, Reference, High, and Rush/SVM-L1/Small. Historical machine-readable identifiers were preserved.

## Figure fixes

- Figure 1 uses the author-supplied editable workflow artwork. Its a) and b) labels are now both bold 37.5-px text; this typography-only normalization did not redraw scientific content or alter panel geometry.
- Figure 5 was redesigned in place as a native 170-mm, three-panel quantitative CGGA figure. The redundant workflow schematic was replaced by compression/AUROC, locked-medoid-minus-RFECV-only paired effects, and five-run agreement panels; all panels are equal size, grids are disabled, and only a)--c) are bold.
- Sentence-style text was removed from Figure 4; its archived scientific panels and values were preserved. A deterministic presentation-only cleanup subsequently removed 63 background-grid groups and one empty annotation box.
- Supplementary Figure S9 was rebuilt natively at 170 mm from frozen aggregate values. Its table-like right-side settings block was removed, panel c now uses the full width for feature importance, and the caption was aligned to the simplified display.
- The redundant sentence in Supplementary Figure S16 was removed through its SVG rendering route without masking axes, ticks, or data.
- Supplementary Figures S21--S23 were re-spaced and their long y-axis labels were reduced or wrapped where needed; the native builder now fails if a right-panel y label intrudes into the preceding axes. Supplementary Figures S18--S24 were verified at full-page or full-document contact-sheet resolution: labels, legends, axes, and continued-page captions are unobstructed.
- Supplementary Figure S19 now splits only in the blank band after complete panel b. The first page contains complete panels a--b and the full caption; the continuation page begins with panel c and contains complete panels c--d.
- Main Figures 1--5 passed a within-figure panel-label audit. Figure 1 was the only source mismatch and was normalized as noted above; Figures 2--5 already used one bold label size within each figure.
- A broad palette recoloring was intentionally not performed because color already carries stable branch semantics and marker shape/open-versus-filled encoding provides redundancy. No background plotting grids were reintroduced.

## Supplementary fixes

- The formal propositions, proofs, complexity analysis, duplicate-mask policy, and implementation correspondence remain in Supplementary Methods.
- The complete algorithm is presented as a nested Supplementary Methods subsection rather than as an unsupported formal Supplementary item type.
- Supplementary Figures S1--S24 and Supplementary Tables S1--S25 compile with consistent numbering. The private-radiomics figure and table are S20 and S21, respectively; the additive post-freeze analyses are Figures S21--S23 and Tables S22--S24; the controlled locking simulation is Figure S24 and Table S25.
- `FIGURE_SOURCE_DATA_MANIFEST.csv` maps all five main and 24 Supplementary figures to a source script or archived presentation route, supporting tables/CSVs, output assets, and availability boundaries.

## Nature compatibility fixes

- Article order is Introduction, Results, Discussion, Methods, Data availability, Code availability, and References.
- The final abstract is 194 words; five main figures plus three main tables produce eight main display items; all five legends are below 350 words.
- Main and Supplementary entry points compile independently with the Nature bibliography style.
- Code availability accurately describes a private peer-review repository and does not claim a public release, PyPI publication, tag, or DOI.
- Reviewer code access is operationally separated from public release in `REVIEWER_CODE_ACCESS_CHECKLIST.md`.

## Validation performed

- Final `main.tex`: 16 pages; SHA-256 `021ffb0d9a263116c4653f5994b3ff2dcdb9aff62ac35eebf9bb0ecd6c423671`.
- Final `supplementary_information.tex`: 42 pages; SHA-256 `b9f451183daa1ca309b0e3bb0fdb5bc5ca02386b2a2a4f863590b3dbb3714d25`.
- Final logs contain zero LaTeX/package warning matches, undefined or multiply defined references, overfull/underfull boxes, duplicate destinations, or oversized-float warnings.
- A fresh full-document render audit inspected all 16 main pages and all 42 Supplementary pages after the simulation integration. A focused 180-dpi rerender of Supplementary pages 15, 27, and 28 verified the final S9 and S21--S23 repairs. No clipped content, blank spill page, covered label, or missing axis was found. Supplementary Figure S24 and Table S25 are readable on pages 28 and 41, respectively; page 42 contains the standalone Supplementary bibliography's single cited reference. Main page 3 retains deliberate whitespace because Table 1 is kept intact and Figure 2 is kept at full-width legibility; these are float-layout choices, not missing content.
- Frozen-value and decision-path validation passed. No existing empirical numerical result was modified.
- The Figure 5 provenance validator passed against four checksum-pinned frozen upstream tables; the local panel data are exact mapped extracts, including the documented two-source agreement join.
- The claim-specific citation pass confirmed that Supplementary Figures S1--S24 and Supplementary Tables S1--S25 all remain cited in the main article. ADNI, AMP-AD, CGGA, radiomics, and controlled-simulation citations sit beside the claims they support, and the stale Supplementary Table S23 note points to Supplementary Figure S22c rather than main Figure 5c.
- The submission ZIP was extracted into a new audit directory and independently rebuilt. The clean copy reproduced the 16-page main article and 42-page Supplementary Information with zero warning/error-pattern matches or layout diagnostics. The final 329-file archive additionally retains the Figure 3 editable provenance source so the panel-label validator is self-contained; this non-rendered source addition does not alter either PDF.

## Unresolved author confirmations

- The requested corresponding-author identity, funding statement, acknowledgements, CRediT roles, competing-interests statement, and generative-AI disclosure are now rendered in V12 and require all-author sign-off.
- Private-radiomics REB/IRB identity, approval or waiver number, and consent/waiver basis remain a submission blocker because the complete source report does not contain them.
- The acknowledgements now identify Selina Parmar only as the provider of the CGGA data and Ruihan Xu only as the provider of the ADNI-derived and AMP-AD data, as clarified by Junseo Park.
- The AMP-AD source was resolved to the AMP-AD Diverse Cohorts Study (`syn51732482`; stable study DOI `10.7303/9618093`). The portal acknowledgement, study-specific grant acknowledgement, data-access statement, source-cohort ethics/consent statement, and source descriptor citation were added without changing empirical results.
- ADNI corporate author-line, methods, ethics, and funding acknowledgement text has been added. The official IDA Publication Update route is documented in `ADNI_DPC_SUBMISSION_PACKET.md`; an authorized account holder must still upload the manuscript and obtain DPC review before journal submission.
- Final author/librarian verification of every reference record.
- Granting and testing editor/reviewer access to the private software repository.
- Optional release tag, public repository state, PyPI publication, and archival DOI decisions.

## Intentionally not changed

- No GA, Direct-selection, or RFECV stage was rerun. The later authorized post-freeze addendum used frozen signatures, saved candidate banks, and saved/derived predictions only: one-time AMP-AD held-out evaluation, coherent CGGA benchmark reconstruction, and a saved-bank nested locking sensitivity. The subsequent S24/S25 integration used completed frozen simulation summaries and reran no simulation bank. These results remain supplementary and do not replace main Figures 4 or 5.
- No frozen candidate mask, score, regret tolerance, objective setting, held-out estimate, interval, or feature count was changed.
- The stable-mask-hash rule was not redesigned or replaced.
- Restricted participant-level data were not copied into the submission package.
- A consolidated journal “Source Data” workbook was not fabricated from heterogeneous or restricted inputs. The complete route-level manifest and available machine-readable summaries are provided; the submission system’s preferred source-data packaging should be confirmed by the authors.
- Main figure numbering was not expanded beyond the current five-figure evidence map; no Figure 6 was invented. The authorized additive analyses extend only the Supplementary numbering to Figure S24 and Table S25.
