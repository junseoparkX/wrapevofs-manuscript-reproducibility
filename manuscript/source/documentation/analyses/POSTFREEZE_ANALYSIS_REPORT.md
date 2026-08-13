# Post-freeze AMP-AD and CGGA analysis report

Date: 2026-08-08

## Scope and frozen boundaries

This pass completed four analyses authorized after the updated AMP-AD development locks were frozen:

1. recovery and verification of the six Rush updated-objective candidate banks;
2. one-time held-out evaluation of all 24 frozen AMP-AD center--branch--cap signatures;
3. a coherent CGGA benchmark using one fixed split and one fixed final estimator; and
4. post hoc re-locking of five saved reduced-budget CGGA nested candidate banks.

No GA, Direct selection, RFECV, or candidate generation was rerun. At the completion of this dated post-freeze AMP-AD/CGGA pass, the locking-layer simulation was excluded. A later separately authorized integration added its already completed frozen summaries as Supplementary Figure S24 and Supplementary Table S25 without changing this post-freeze analysis.

## Rush recovery

The authoritative source was the Google Drive folder `WrapEvoFS_AMPAD_Rush_Objective_Rerun_results` (folder ID `12PVV-ScxFl1_kDKSfowqMa35-ZZTQX7I`), not a stored ZIP. Thirty run-best feature lists reconstructed all six five-run banks. Verification passed: 6/6 banks and 30/30 candidates were recovered; no exact duplicate masks occurred; every current selection matched both the archived summary and the frozen one-time evaluation; and maximum selected empirical regret was 0. The local `Rush_reconstructed_source_results_20260808.zip` is therefore a reconstructed provenance archive, not the original source ZIP.

With Rush restored, the existing 2-by-2 candidate-bank/locking-rule audit is complete for 48 banks. In the updated-objective banks, moving from the archived top-three lock to the current regret-constrained lock changed 8/24 masks, changed total target deviation from 135 to 137, and reduced mean/maximum selected empirical regret from 0.003513/0.015247 to 0.001083/0.008347. This illustrates the intended claim boundary: the rule enforces the configured score-gap feasibility condition but does not optimize target-size fidelity.

## AMP-AD one-time post-freeze evaluation

The protocol SHA-256 is `7bc7b27e00f7337654b6f81c1448a831ce3979129e68d14666389445d3ec93b5`. A completion sentinel prevents accidental repetition. The 24 frozen signatures were fitted with the prespecified final random forest and evaluated once in their corresponding held-out centers. No result triggered reselection, parameter changes, or refitting of feature selection.

Pooled updated-lock minus RFECV-only macro-AUROC contrasts were:

| Branch/cap | Difference | 95% CI |
|---|---:|---:|
| SVM-L1 Small | -0.0098 | [-0.0350, 0.0142] |
| SVM-L1 Reference | -0.0084 | [-0.0287, 0.0119] |
| XGBoost Small | 0.0480 | [0.0253, 0.0704] |
| XGBoost Reference | -0.0207 | [-0.0436, 0.0013] |
| Boruta-RF Small | -0.0404 | [-0.0621, -0.0195] |
| Boruta-RF Reference | 0.0025 | [-0.0145, 0.0191] |

Four of six intervals include zero, and the two non-zero-crossing intervals point in opposite directions. Updated-lock minus archived-original-lock intervals include zero in five of six conditions; SVM-L1 Small was negative. The result therefore supports outcome-blind, post-freeze cross-center evaluation but not uniform predictive superiority. It is not described as prospective clinical validation or independent external validation.

## CGGA coherent benchmark

Six development-derived signatures per branch were evaluated on the same fixed 214/92 split with the same 500-tree random forest: RFECV-only, size-matched Elastic Net, highest development-CV, legacy top-three medoid, unrestricted full-bank medoid, and current regret medoid. Reconstruction of the full matrix was checked exactly against the archived compact participant IDs, labels, and overlapping values before evaluation.

Current-lock held-out AUROCs were 0.652 (SVM-L1), 0.645 (XGBoost), and 0.694 (Boruta-RF). All 15 paired current-lock-minus-comparator AUROC intervals included zero. The benchmark standardizes the split and final estimator, but it does not establish superiority over the comparators.

## CGGA saved nested-bank re-locking

The current rule was applied to five archived candidate banks from a historically excluded reduced-budget nested sensitivity. No GA was rerun and the original 92-participant held-out partition was not accessed. The selected run changed in all five folds and each current selection had zero empirical regret. OOF AUROC changed from 0.692 for the archived top-three lock to 0.667 for the current rule, with overlapping bootstrap intervals. This adverse sensitivity is retained because it directly demonstrates that empirical regret feasibility is not a guarantee of improved generalization.

## Manuscript placement

- Main Figure 4 remains the approved archived AMP-AD multicenter demonstration.
- Main Figure 5 remains the approved archived CGGA compression, incremental-effect, and seed-agreement figure.
- Supplementary Figure S21: AMP-AD one-time post-freeze performance and paired contrasts.
- Supplementary Figure S22: coherent CGGA same-split, same-estimator benchmark.
- Supplementary Figure S23: CGGA saved-bank nested sensitivity.
- Supplementary Tables S22--S24: detailed AMP-AD, CGGA benchmark, and nested re-locking results.
- Participant-level predictions remain in private analysis directories and are not copied into manuscript `supplementary_data`.

This additive placement supersedes an erroneous intermediate layout that replaced main Figures 4 and 5 with post-freeze analyses. No approved main figure is replaced in the corrected manuscript.
