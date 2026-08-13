# V11 revision audit

> Historical-status note (V12, 2026-08-08): the V11 statements below correctly describe artifact availability at the time of that audit. V12 subsequently recovered all 30 Rush run-best feature lists from the authoritative Google Drive source folder, verified all six Rush banks, and completed the 48-bank cross-lock audit. See `POSTFREEZE_ANALYSIS_REPORT.md`. The reconstructed local ZIP is a provenance archive, not an original source ZIP.

## Authority and preservation

- Authoritative source preserved: `manuscript/latex_v10_overleaf`.
- Authoritative V10 PDF SHA-256: `bfdcfe0fd1c8fd26e99621409da1656cef36ad54375bfe9c0a456b9e78ddb362`.
- V11 working source: `manuscript/latex_v11_overleaf`.
- Frozen Figure 1 SHA-256 in both versions: `3714fd6bfd29dd8f0c3500a0462f483a85881147b27d60d5507fc05b8b70a0bd`.
- `scripts/validate_figure1_freeze.py` passes after manuscript integration.

V10 was copied before revision and was not edited. Figure 1, its placement, caption, and callouts remain unchanged.

## Scope actually executed

All V11 analyses use completed development-only artifacts. The authoritative stable-mask-hash implementation was imported from the current package; the rule was not redesigned. No GA, RFECV, Direct selection, held-out evaluation, Bayesian analysis, STABL, BLiP, bootstrap analysis, empirical feature-selection experiment, new dataset, or simulation was run. No empirical numerical result was modified.

## Artifact availability

| Requested analysis | Availability | V11 treatment |
|---|---|---|
| Robust and stress-excluded S16 summary | Complete, 24 conditions | Recomputed from the authoritative S16 CSV |
| Original-objective bank with both locks | Complete, 24 banks | Both cells reported |
| Updated-objective bank with both locks | Complete for 18 non-Rush banks | Both cells reported for those 18 |
| Updated Rush regret-lock summaries | Summary audit available for 6 | Retained as summary-only |
| Updated Rush original top-three lock | Raw candidate masks absent for 6 | Marked unavailable; not reconstructed |
| Eligible-pool and tie paths | Operational decisions available for all 24 updated conditions | Full decision-stage audit reported |
| Duplicate retained vs deduplicated | Complete for 24 original and 18 updated non-Rush banks | No duplicates and no selection changes observed |
| Updated Rush duplicate/hash sensitivity | Raw masks absent | Marked unavailable |
| S16 singleton mean Jaccard | Source definition known | 65 singleton rows set to NA for presentation only |

## Verified findings

- Target deviation: 216 to 137 overall; 135 to 112 excluding Rush/SVM-L1/Small.
- All-zero generations: 673 to 333 overall; 428 to 267 excluding that stress condition.
- The stress condition explains 70.9% of target-deviation reduction and 52.6% of all-zero-generation reduction.
- Original-objective banks: regret locking changes 10/24 masks and reduces maximum empirical regret from 0.02111 to 0.00729.
- Updated-objective complete banks: regret locking changes 6/18 masks and reduces maximum regret from 0.01142 to 0.00835.
- Updated eligible pools at delta 0.01: 2 singleton, 6 two-candidate, and 16 with at least three candidates.
- Final decision stage: 13 unique Jaccard, 9 higher score, 2 singleton direct, 0 feature-count, and 0 hash decisions.
- No exact duplicate masks occurred in the 42 complete banks.

## Interpretation boundary

The regret rule guarantees only the configured empirical development-CV score gap inside the retained candidate bank. Cross-lock results show that this guarantee does not optimize target fidelity. These analyses do not establish predictive superiority, unbiased generalization, external validity, biomarker stability, clinical utility, or globally optimal feature selection.
