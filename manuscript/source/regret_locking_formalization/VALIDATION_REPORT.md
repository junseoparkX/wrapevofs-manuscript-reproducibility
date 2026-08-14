# Regret-constrained locking validation report

Date: 2026-08-03

## Outcome

The absolute regret-constrained medoid is formally specified, proved, documented, implemented with exact eligibility, and tested against the stated assumptions. The authoritative manuscript was updated and recompiled without changing an empirical result or a figure.

## Mathematically proved properties

1. A finite nonempty bank with finite larger-is-better scores and nonnegative tolerance has a nonempty eligible pool.
2. Every singleton, medoid, and deterministic tie path selects inside the eligible pool, so selected empirical development-CV regret is at most the configured tolerance.
3. At zero tolerance the pool is exactly the set of score maximizers; it is a singleton only when the maximizer is unique.
4. At tolerance at least the maximum candidate regret, locking is the full-bank Jaccard medoid.
5. Canonical masks, deterministic arithmetic/ordering, and the stable hash produce a deterministic selected feature set and canonical audit under identical inputs and provenance.
6. Candidate-record permutation does not change the selected feature set or canonical audit when content, provenance, and duplicate multiplicity are fixed.
7. Highest-score, unrestricted medoid, legacy top-k medoid, and regret-constrained medoid rules have distinct feasible sets and guarantees; none proves globally optimal feature selection.

The digest is only a stable canonical ordering device. Collision resistance is an engineering assumption and does not create the regret guarantee.

## Implementation-tested properties

The proposition-focused suite passed 68 cases. Five adjacent artifact/CLI/metric checks also passed. Tested behavior includes all requested invalid-input, boundary, zero-tolerance, all-eligible, duplicate, canonicalization, independent-process, permutation, generated-bank, serialization, reload, and repeated-audit cases. Full command details are in `PROPERTY_TEST_REPORT.md`.

The current implementation uses the completed stable-hash rule without redesign:

```text
SHA256(np.asarray(canonical_mask, dtype=np.uint8).tobytes()).hexdigest()
```

Duplicate masks are retained as multiple voting candidates. Their multiplicity is part of the candidate-bank multiset. When an exact duplicate scientific mask wins, the lowest source run ID is retained only as a deterministic provenance representative after feature-set selection.

## Assumptions not fully machine-testable

- SHA-256 collision resistance; an observed collision is guarded at runtime, but universal collision absence cannot be tested.
- That a supplied locking score is scientifically appropriate and genuinely larger-is-better; the package can enforce only the declared orientation and finite numeric value.
- That caller-supplied provenance is authentic and immutable.
- Hidden candidate-universe inconsistency when every candidate omits `candidate_universe`; the package then derives and records a deterministic sorted union. Explicit supplied universes are validated exactly and are preferred for scientific use.
- Cross-platform identity of upstream floating-point scores; the determinism proposition conditions on identical input values and configuration.
- Expected predictive risk, generalization error, statistical uncertainty, external validity, participant-resampling stability, biomarker stability, and clinical utility.

## Manuscript/package mismatches found and disposition

| Mismatch | Disposition |
|---|---|
| The prior manuscript and Algorithm 1 ended scientific ties with lower run ID. | Reported before behavior changes; replaced by the authoritative canonical stable-mask hash. Run ID is now provenance-only for exact duplicates. |
| The prior locking implementation used `threshold + epsilon`, so it was not literally the stated exact threshold. | Reported before behavior changes; changed to exact `<= threshold` and covered by a boundary regression test. |
| The prior package lacked a validated common universe and canonical locking-mask audit. | Added optional explicit common-universe validation, deterministic union fallback, canonical masks/hashes, and audit fields. |
| Existing empirical `locking_candidate_audit.csv` rows retain the historical `... > lower_run_id` tie-path text. | Deliberately preserved: it is an empirical source artifact. No audited group reached the final run-ID tie, so this historical text did not determine any saved selected feature set. |
| A caller can omit all explicit universes. | The deterministic derived union is recorded, but external common-universe provenance remains a caller responsibility and is disclosed as an assumption. |

No discrepancy was silently repaired. The behavioral mismatches were reported before the package was changed.

## Empirical-artifact preservation

- `locking_candidate_audit.csv`: SHA-256 `C228BF1AC63983EA510DF70F0844FBED5D169E98EEED22E51A59EF72215A36B2`.
- `locking_rule_sensitivity.csv`: SHA-256 `604711208D792A736E440818658D745516E7BB5926651D3D823E4AC6723CCE16`.
- The locking audit has 870 rows in 174 decision groups, exactly one selected row per group, no empty eligible group, and no threshold violation among the 168 complete absolute-tolerance selections.
- None of the 174 groups reached the historical final run-ID tie.
- The sensitivity table has 225 rows; 174 are complete, 36 lack fold vectors, 12 lack masks, and 3 lack both. No unavailable value was imputed.

No GA, RFECV, Direct selection, held-out evaluation, Bayesian analysis, STABL, BLiP, bootstrap analysis, or empirical feature-selection experiment was run.

## Manuscript build and visual validation

- LuaLaTeX/latexmk build completed successfully: 43 pages.
- Final PDF SHA-256: `69BB2476915B5481D2B71406D1504BFF23C95EA5A4EEE9C06F527F217767A6E0`.
- The final log contains no undefined reference, multiply-defined label, or overfull-box warning. The new narrow S17 table has nonfatal underfull-cell warnings only and was visually inspected at full resolution.
- All 43 pages were rendered to PNG and reviewed in contact sheets; Methods/Algorithm 1, proof/complexity pages, the Supplementary Figures transition, and S17 were also inspected individually.
- Main figure/table numbering is unchanged. Supplementary Figures S1--S18 and existing Supplementary Tables S1--S16 retain their numbers; the new implementation correspondence is Supplementary Table S17.
- All 26 files under `figures/` were left untouched. No empirical value in an existing table was changed.

## Claim boundary

The formal result guarantees only the configured empirical development-CV score gap for selection from the supplied retained candidate bank. It does not prove predictive superiority, unbiased generalization performance, external validity, biomarker stability, or globally optimal feature selection.
