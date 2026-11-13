Exploratory development-only allowance calibration — v20 update

Inputs: candidate_development_audit.csv contains240 candidate feature masks and development scores on one fixed TCGA392-participant training partition. No participant rows, IDs, labels or prediction arrays are included.
Run calibrate_allowance.py with --input candidate_development_audit.csv --output OUTPUT_DIRECTORY --search breakpoints (or grid). Both scorer choices are reproduced without reading held-out outcomes.
policy_summary.csv and policy_selections.csv compare the full240 fitted breakpoint/grid policies, fixed0.01 and highest score. selected_model_AUROC.csv contains only signature-level aggregate AUROC values, not participant predictions.
paired_AUROC_contrasts.csv uses5000 class-stratified paired99-participant resamples conditional on fixed fitted signatures/deltas;12 primary simultaneous contrasts, secondary nominal intervals. The ensemble AUROC is not reported.
earlier_reserved_seed_* preserve the separate earlier grid rule fitted on120 candidates and applied to120 reserved candidates. These must not be confused with full240 calibration or with validation of the later breakpoint method.
calibration_curve.csv gives every observed score-gap breakpoint. The one-SE-style filter is a development heuristic. Fitted-bank Jaccard is an optimization objective, not independent reproducibility validation.
evaluation_protocol.json and selection_freeze.json record the new retrospective extension and development-only selection. The extension was designed after earlier outcomes were available. It did not use held-out AUROC to select delta, and no result changed the rule. Code and model settings of previous experiments were preserved.

feature_universes.json retains the ordered feature names used to construct the original binary-mask SHA256 identifiers. All240 masks were independently reconstructed. It contains no participant rows.
