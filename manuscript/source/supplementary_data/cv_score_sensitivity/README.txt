Fixed-bank paired CV-score sensitivity (v19)

Completed on fenn10 under /data2/junseo/wrapevofs/v19_cv_score_sensitivity_20261105.
Only aggregate candidate masks, feature identities and development fold scores are included.
No participant-level matrices, labels, predictions or held-out outcomes are included.

The protocol was frozen before weighted selection outcomes were computed. Main analysis: 54 banks.
Sensitivity: exclude six Rush banks (48 banks). Fold arrays and fixed candidate-specific estimator seeds are unchanged.
126 bootstrap count vectors are weighted by multinomial multiplicity/3125. They are not126 equally likely samples.
Retention refers to the original mask under the same rule; all54 banks have five unique masks.

Reproduce from this directory without overwriting the archived results:
python run_cv_score_sensitivity.py --tcga inputs/candidate_level_geometry.csv --ampad inputs/ampad_complete_candidate_audit.csv --protocol protocol.json --output reproduction_results --execution-label independent_reproduction
Add --validate-numpy to run the independent NumPy verification if NumPy is installed.

results/group_policy_summary.csv supplies Table S29. bank_policy_summary.csv includes selection entropy and bank ranges.
weighted_case_results.csv contains every paired decision; candidate_selection_probabilities.csv contains exact weighted probabilities.
validation/ documents bitwise NumPy score checks, independent selection checks, archived-policy checks and byte-identical local/remote CSVs.
source_integrity_manifest.json covers only files in this new experiment bundle plus the new table; it makes no assertions about unrelated manuscript files.

Interpretation: sensitivity of fixed saved candidate banks, not new-seed or participant-resampling stability, unbiased generalization, or clinical utility.
