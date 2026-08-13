# WrapEvoFS manuscript V13 validation report

Validation date: 2026-08-10 (America/Los_Angeles)

## Revision boundary

V13 revises the V12 Methods and title-page affiliation metadata. It adds explicit mathematical definitions, executable pseudocode, and consolidated implementation settings, and it identifies Junseo Park with the UBC Department of Computer Science and Leonard J. Foster and Huan Zhong with the UBC Department of Biochemistry & Molecular Biology, Michael Smith Laboratories, and Life Sciences Institute. No empirical analysis was rerun, and no reported result, feature set, lock, figure, result table, or statistical conclusion was changed.

For readability, the displayed GA and locking averages use simple per-fold score symbols. The adjacent prose still specifies the evaluator, feature set, fold role, metric, and seed, so this notation-only simplification does not alter either computation. The medoid tie rule is likewise written as an ordered list of the same four criteria rather than a dense lexicographic arg-min expression.

## Implementation correspondence

The added specifications were checked against the packaged WrapEvoFS v0.2.0 source under `release_candidate_20260803_105542/publish_clone/src/wrapevofs`, including the Direct selectors, RFECV target selector, genetic search, pipeline seed mapping, and fixed locking evaluator. The check covered:

- Direct-selector models, preprocessing, grids, thresholds, score resolution, and feature caps;
- RFECV estimator, folds, step size, cap handling, score resolution, and smallest-maximizer rule;
- GA population and generation budget, initialization, objective, ranking, elitism, parent probabilities, sampling with replacement, crossover, per-bit mutation, empty-mask repair, and CPU/GPU evaluator settings;
- zero-based evaluator seed schedule `base + 10000*r + 100*g + 1009*i + fold` and run-specific locking seeds;
- common fixed-fold candidate rescoring, strict regret eligibility, Jaccard-medoid selection, deterministic tie-breaking, duplicate-mask multiplicity, and held-out-data boundary.

The package test suite completed with `112 passed`.

## Source and result preservation

SHA-256 comparison of 228 files under the V12 and V13 `figures`, `supplementary_data`, `revision_outputs`, and pre-existing result-table paths found zero differences. The only scientific-source changes are the intended Methods text, Supplementary Algorithm S1, the Supplementary Methods cross-reference, and new Supplementary Table S26.

## PDF build and reference checks

- `main.pdf`: 17 pages, LuaLaTeX/latexmk build successful.
- `supplementary_information.pdf`: 42 pages, LuaLaTeX/latexmk build successful.
- Final LaTeX logs contain no overfull/underfull boxes, undefined references or citations, multiply-defined labels, or LaTeX/package warnings.
- Extracted PDF text contains no unresolved `??` reference markers.
- Supplementary Table S26 is physically placed after Tables S16--S25 and is referenced from both the main Methods and Supplementary Methods.

## Visual inspection

Rendered-page inspection covered both revised title pages, the modified main Methods pages, both pages of Supplementary Algorithm S1, and the final Supplementary tail containing Tables S17--S26. Following the author's numbering instruction, the title pages consistently map affiliation 1 to Junseo Park and affiliation 2 to Leonard J. Foster and Huan Zhong; the long affiliation 2 was manually line-broken and is legible and unclipped. Equations, algorithm lines, table rules, captions, page order, and margins were also legible and unclipped. Supplementary Table S26 fits on one page without collision with the References heading.

## Distribution artifact

The clean V13 submission ZIP is built by `scripts/build_v13_submission_archive.ps1`. Two consecutive builds from the same source produced an identical SHA-256 digest. The archive contains 332 entries, contains none of the excluded cache, QA-render, or LaTeX-intermediate patterns, and its two PDF entries are byte-identical to the validated source PDFs. Its final SHA-256 digest is stored beside the ZIP in `V13_SUBMISSION_ARCHIVE_SHA256.txt`; the digest is intentionally external to the hashed archive.
