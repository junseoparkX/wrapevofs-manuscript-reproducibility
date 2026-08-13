# AMP-AD remaining-90 updated-configuration post-run analysis

Date: 2026-08-06 (America/Los_Angeles)

## Bottom line

The supplied Emory, Mayo, and Mount Sinai updated-configuration run bank is complete and internally consistent: 90/90 runs and 18/18 branch--cap conditions passed the artifact validator with no errors or warnings, no held-out access was detected, and every history contains all 50 generations. No GA, RFECV, Direct selection, held-out evaluation, bootstrap analysis, or other empirical feature-selection experiment was rerun during this analysis.

The new 90-run bank strengthens the mechanism evidence, but the result is heterogeneous rather than uniformly favorable. Aggregate locked absolute target deviation was 106 under the matched original configuration and 89 under the updated configuration across the 18 new conditions. The updated value was lower in eight conditions, unchanged in five, and higher in five. The development-CV locking-score difference was small on average but mixed in direction (mean +0.00168; median +0.00152; range -0.01319 to +0.02389). Because both candidate generation and locking differ, the result is a configuration-level target-fidelity and objective-flattening comparison, not an isolated causal effect, universal condition-level improvement, or predictive superiority.

Combined with the already reported 30 Rush runs, the complete Small/Reference-cap updated-configuration comparison comprises 120 runs and 24 conditions across all four center-specific development partitions. Aggregate locked absolute target deviation was 216 under the original configuration and 137 under the updated configuration, diagnostic zero-truncated run-best values were 4/120 and 0/120, and the zero-truncation all-zero-generation diagnostic was 673 and 333. The actual shifted-weight searches recorded zero uniform-sampling fallbacks. No held-out outcome was accessed in the updated-configuration runs or in the development lock-freeze.

## Source integrity and scope

- Remaining-90 bundle ZIP: SHA-256 `601876c745a00f86039d06c49448b5791053b30a8dc5f9ebfc620aec86f0ce21`.
- Remaining-90 result ZIP: SHA-256 `89f86d764ed755e55c0626a93d96aa78670ac5481ed0719771b566dacb8599e5`.
- Jobs expected / complete / invalid: 90 / 90 / 0.
- Conditions expected / ready for lock-freeze: 18 / 18.
- Validation errors / warnings: 0 / 0.
- Held-out access detected: no.
- Completed GA generations represented in the supplied histories: 4,500.
- Analysis operations performed here: artifact validation, reuse of the already completed development-fold locking scores, application of the current package locking function, deterministic permutation checks, and descriptive aggregation.

## Remaining 90 runs

### Run-level diagnostics

| Quantity | Result |
|---|---:|
| Completed runs | 90/90 |
| Completed generations | 4,500/4,500 |
| Sum of run-best absolute target deviations | 384 |
| Mean / median run-best absolute target deviation | 4.27 / 2 |
| Range of run-best absolute target deviation | 0--18 |
| Exact-target run-best subsets | 36/90 |
| Within-one-feature run-best subsets | 44/90 |
| Diagnostic zero-truncated run-best values | 0/90 |
| Diagnostic all-zero zero-truncation generations | 200 |
| Actual uniform-sampling fallback generations | 0 |
| Aggregate GPU runtime | 39.17 h |

The 200 all-zero counts are counterfactual diagnostics obtained by applying the archived zero-truncation view to the updated search histories. They are not actual updated-mode sampling failures; shifted sampling recorded zero fallbacks.

### Authoritative condition locks

- All 18 selections used the package's authoritative `regret_constrained_medoid` rule with larger-is-better macro OvR AUROC, absolute tolerance 0.01, strict eligible-only pools, and the canonical stable-mask-hash path.
- Eligible-pool sizes ranged from 2 to 5 (mean 3.0); there were no singleton pools in these 18 conditions.
- Selected empirical regret ranged from 0 to 0.0083473 (median 0), so all 18 selections satisfied the declared 0.01 bound.
- All 90 archived stable feature-set identifiers matched hashes recomputed from the common canonical candidate universes.
- Every condition had five distinct run-best masks; duplicate-mask multiplicity therefore did not affect these 18 selections.
- All 120 input-record permutations per condition were tested: 2,160/2,160 produced the identical selected feature set, candidate audit, pairwise audit, and metadata.

## Matched original-configuration comparison for the new 18 conditions

| Group | Original locked absolute deviation | Updated locked absolute deviation | Original all-zero generations | Updated diagnostic all-zero generations |
|---|---:|---:|---:|---:|
| Emory | 22 | 15 | 78 | 44 |
| Mayo | 40 | 40 | 132 | 91 |
| Mount Sinai | 44 | 34 | 101 | 65 |
| **Total** | **106** | **89** | **311** | **200** |

| Branch | Original locked absolute deviation | Updated locked absolute deviation | Interpretation |
|---|---:|---:|---|
| Boruta-RF | 39 | 13 | Large aggregate improvement |
| SVM-L1 | 26 | 29 | Slight aggregate worsening |
| XGBoost | 41 | 47 | Aggregate worsening |

The aggregate target-fidelity improvement is therefore not branch-uniform. The report should state the condition counts (8 improved, 5 unchanged, 5 worsened) and retain the complete condition table.

## Combined four-center result for manuscript use

The already reported Rush 30-run analysis and the new 90-run bank use the same Small/Reference-cap updated-configuration design. Their combined descriptive summary is:

| Quantity | Original | Updated |
|---|---:|---:|
| Runs | 120 matched run positions | 120 newly executed runs |
| Conditions | 24 | 24 |
| Aggregate locked absolute target deviation | 216 | 137 |
| Mean locked absolute target deviation | 9.00 | 5.71 |
| Zero-truncation diagnostic run-best values | 4/120 | 0/120 |
| All-zero-generation diagnostic | 673 | 333 |
| Actual updated-mode uniform fallbacks | not applicable/inferred in original | 0 |

Across the 24 conditions, the updated target deviation was lower in 12, unchanged in 6, and higher in 6. The updated-minus-original locking-score difference averaged +0.00098 (median +0.00096; range -0.01319 to +0.02389). Aggregate updated-configuration runtime was 51.77 GPU-hours. The maximum selected empirical regret was 0.0083473. These values support preservation of the configured development-score gap, not equality, non-inferiority, unbiased generalization, or improved held-out prediction.

## Discrepancy requiring explicit treatment

The supplied remaining-90 bundle contains an older helper whose documented final scientific tie-break is lower source run ID. The current package instead uses the completed authoritative rule: higher computed mean eligible-pool Jaccard, higher locking score, smaller feature count, then lexicographically smaller stable canonical-mask hash; source run ID is provenance-only after scientific feature-set selection.

Seventeen of 18 condition selections were scientifically identical under the two implementations. The exception is Mount Sinai / SVM-L1 / Reference-cap:

- old bundle helper: run 3, locking score 0.8957268, regret 0;
- current package: run 5, locking score 0.8920246, regret 0.0037022;
- both masks contain 17 features, so all target-count and target-deviation summaries are unchanged;
- the two candidates have the same exact multiset of four peer Jaccard values, but IEEE-754 reduction in different peer orders differs by one unit in the last place (approximately `5.6e-17`); the canonical package ordering is deterministic and selected run 5;
- both selections satisfy the 0.01 empirical regret constraint.

This discrepancy was not silently repaired. The analysis tables use the current package output because the completed stable-hash implementation was designated authoritative. Before manuscript integration, the finite-precision behavior should be stated in the supplementary implementation note: eligible-pool means are evaluated in canonical mask-hash order. The obsolete lower-run-ID bundle label should not appear as the scientific rule.

## Claim boundary

The new results establish only properties of the completed development-only updated-configuration searches and the supplied candidate banks. Because the original and updated configurations differ in both candidate generation and locking, they do not isolate the causal contribution of either change. They do not establish improved held-out performance, predictive superiority, external validity, unbiased generalization, participant-resampling stability, biomarker stability, clinical utility, or global feature-selection optimality. The RFECV target remains a soft search target, and five seeds remain a sparse stochastic-agreement sample.

## Primary artifacts

- `validation/validation_summary.json`: source artifact validation.
- `development_freeze_bundle_rule_diagnostic/`: diagnostic output from the supplied older helper.
- `development_freeze_authoritative/LOCK_FREEZE_MANIFEST.json`: package-authoritative re-lock manifest.
- `development_freeze_authoritative/candidate_locking_audit.csv`: complete 90-candidate authoritative audit.
- `development_freeze_authoritative/empirical_permutation_invariance.csv`: exhaustive five-record permutation verification for all 18 conditions.
- `summary/analysis_summary.json`: headline descriptive results.
- `summary/remaining90_legacy_vs_recommended.csv`: matched 18-condition comparison.
- `summary/proposed_table_s16_24_conditions.csv`: proposed expanded Supplementary Table S16 source.
