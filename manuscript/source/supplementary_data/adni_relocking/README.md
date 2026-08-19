# ADNI retrospective re-locking source summary

This directory records the branch-level values used to update Supplementary Table S8. The authoritative complete audit is in `analysis/adni_relocking_audit_20260815/`, including candidate-level scores and canonical feature sets, full-bank pairwise Jaccard values, Drive provenance, deterministic validation, and the executable audit script.

- Locking score: archived `cv_balanced_accuracy_mean` (larger is better)
- Absolute tolerance: `0.01`
- Candidate multiplicity: five retained masks per branch; no exact duplicates
- Computation rerun: none (no GA, Direct selection, RFECV, model fit, or held-out evaluation)
- Determinism check: all 120 input-record permutations per branch selected the same feature set
- Decision path: all three eligible pools were singletons, so neither a Jaccard-medoid tie nor stable-hash tie was reached
