# Development-only 120-run updated-configuration audit bundle

This directory contains the compact machine-readable audit supporting the revised Supplementary Figure S18 and Supplementary Table S16. It combines the previously completed 30 Rush searches with the newly completed 90 Emory, Mayo, and Mount Sinai searches: 120 full GPU GA runs, five seeds in each of 24 Small/Reference center--branch--cap conditions.

No GA, RFECV, Direct selection, held-out evaluation, Bayesian analysis, STABL, BLiP, bootstrap analysis, or other empirical feature-selection experiment was rerun to create this manuscript bundle. The analysis reused completed development-only histories and frozen development-CV locking scores. Held-out outcomes were not accessed.

## Contents

- `ANALYSIS_REPORT.md` and `VALIDATION_REPORT.md`: human-readable interpretation and validation scope.
- `validation/`: source-artifact completeness, job/condition inventories, and issue report.
- `authoritative_lock/`: package-authoritative stable-mask-hash locking manifest, candidate and pairwise audits, stable-identifier checks, and exhaustive five-record permutation checks for the 18 newly completed conditions.
- `summary/`: run-, condition-, center-, branch-, and complete 24-condition publication sources.
- `scripts/`: the analysis, authoritative re-lock, and S18/S16 presentation builders used for this revision.

## Interpretation boundary

The audit supports statements about completed development-only search mechanics, target fidelity, objective flattening, deterministic locking, and the configured empirical development-CV regret bound. In reader-facing material, `original configuration` denotes the archived zero-truncated searches with top-three locking and `updated configuration` denotes the untruncated searches with regret-constrained locking. Frozen filenames and source-field names retain `legacy` and `recommended` where needed for provenance. The comparison does not isolate the causal effect of either changed component and does not establish predictive superiority, unbiased generalization, external validity, biomarker stability, clinical utility, or globally optimal feature selection.

## Finite-precision disclosure

For Mount Sinai/SVM-L1/Reference, the older supplied helper and current authoritative package select different 17-feature masks. Runs 3 and 5 have the same exact peer-Jaccard multiset, but historical and canonical peer-reduction orders differ by one IEEE-754 unit in the last place. The package-authoritative canonical mask-hash ordering selects run 5 (regret 0.0037); the older helper selected run 3 (regret 0). Both are eligible and the target-count summaries are unchanged. The package rule was not redesigned for this revision.
