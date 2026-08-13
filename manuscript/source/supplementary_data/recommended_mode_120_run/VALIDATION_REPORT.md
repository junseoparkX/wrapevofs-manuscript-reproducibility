# Validation report

## Outcome

PASS, with one disclosed older-helper versus current-package selection discrepancy.

## Completed checks

- Source ZIP hashes and inventories recorded.
- Artifact validator: 90/90 complete, 18/18 lock-ready, 0 invalid, 0 errors, 0 warnings, and no detected held-out access.
- Validator test suite: 5 passed using a workspace-local pytest temporary directory. The initial default-temporary-directory failure was a Windows permissions issue, not a scientific or code failure.
- Frozen five-fold development locking scores were generated once from the 90 supplied run-best feature sets. No GA, RFECV, Direct selection, or held-out evaluation was run.
- Current WrapEvoFS package locking was applied to the frozen scores with absolute tolerance 0.01, larger-is-better orientation, strict eligible-only pools, and the authoritative canonical stable-mask-hash rule.
- Stable-feature-set identifier verification: 90/90 matched canonical-mask hashes.
- Strict regret verification: 18/18 selected regrets were at most 0.01; maximum 0.0083473.
- Held-out flag verification: false for every run and lock artifact.
- Empirical candidate-order permutation verification: all 120 permutations of five input records for each of 18 conditions, 2,160 total; selected feature set, candidate audit, pairwise audit, and metadata were identical in every case.
- Analysis script syntax validation: both scripts compiled successfully.
- Deterministic regeneration: 15 authoritative-lock and summary artifacts were regenerated from the same inputs; 0 SHA-256 hashes changed.
- Final structural assertions: 90 candidate rows, 18 condition rows, 18 permutation-check rows, and 24 proposed combined-table rows.

## Disclosed discrepancy

The older supplied bundle helper and current package select different 17-feature masks for Mount Sinai/SVM-L1/Reference-cap because the two medoid candidates have equal exact peer-similarity multisets but different one-ULP floating reductions under different peer orders. The old helper selects run 3; the canonical current package selects run 5. Both satisfy the regret threshold, and target-count summaries are unchanged. The authoritative-package result is retained; no package or empirical value was silently modified.

## Scope boundary

This validation does not establish held-out performance, predictive superiority, unbiased generalization, external validity, participant-resampling stability, biomarker stability, or clinical utility.
