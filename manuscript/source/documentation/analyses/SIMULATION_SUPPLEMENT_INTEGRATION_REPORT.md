# Controlled locking-simulation Supplementary integration report

Date: 2026-08-09

## Outcome

The completed CPU-only candidate-bank locking simulation is integrated as Supplementary Figure S27 and Supplementary Table S22 and is cited in the main Results, Discussion, and Methods. The simulation is kept supplementary because it isolates locking-layer behavior rather than empirical predictive performance.

## Scientific source and execution boundary

- Frozen protocol SHA-256: `6bb91ec337c331aa4b69646f5166831503405d2721a40d16be75718179418d6f`.
- Complete workload: 4,995,000 banks across 513 scenarios; primary equal-scenario design: 1,620,000 banks across 162 scenarios.
- Authoritative summary inputs: `scenario_rule_summary.csv` (Drive ID `1jnE7wWw_8tB34mOxYc1_YHfn098dRL4d`) and `paired_current_minus_comparator.csv` (Drive ID `1HsWi-XYdfPPnDUo2l8eCtUpqk_tXi-0N`).
- No simulation bank, GA, classifier, RFECV, Direct selector, held-out evaluation, bootstrap analysis, or empirical feature-selection experiment was rerun for manuscript integration.
- The $R=100$ sensitivity used an engineering chunk size of 250 although the protocol's listed engineering sizes began at 1,000. Randomness was keyed to scenario and replicate identifiers, all integrity checks passed, and no scientific parameter changed. This is documented rather than concealed.
- Raw checkpoints retain `duplicate_multiplicity`, but the frozen scenario-summary CSV does not aggregate the selected mask's exact multiplicity distribution. The manuscript therefore reports the duplicate-handling policy and duplicate-rate sensitivity design but makes no numerical claim about that unaggregated distribution; no rerun is required for the presented S28/S23 claims.

## Supplementary Figure S27

The deterministic 170-by-67-mm, grid-free figure contains three equal-height panels with bold a)--c) labels:

1. current-minus-highest-score hidden-oracle regret by score-noise ratio and topology;
2. the empirical-regret/representativeness trade-off across absolute tolerances; and
3. current-minus-comparator hidden-oracle regret across candidate-bank sizes.

The output is available as PDF, SVG, and 300-dpi PNG. The figure is generated from three compact frozen aggregate CSVs by `scripts/build_locking_simulation.py`; browser/Poppler rendering is recorded separately. It is placed on Supplementary page 28 and has no clipped axis, legend, label, or caption.

## Supplementary Table S22

The table contains:

- equal-scenario primary operating characteristics for highest score, legacy top-three medoid, unrestricted full-bank medoid, and regret-constrained medoid;
- a primary empirical-regret audit, including zero configured violations for the current rule across all 4,995,000 banks; and
- mutually exclusive current-rule decision paths plus the inclusive hash-stage probability.

Exact duplicate masks retain multiplicity as voting candidates. The stable mask hash is reported only as a deterministic ordering stage. The q95 abbreviation is defined as the within-scenario 95th percentile. The table fits Supplementary page 41 without clipping.

## Main-text integration

- Results reports the primary values, the 91/162 joint representativeness/oracle-regret scenario count, and the conditional effects of noise, topology, tolerance, and bank size.
- Discussion states the balanced interpretation: the current rule always enforced configured empirical feasibility and increased representativeness relative to highest-score selection, but did not achieve uniform hidden-oracle superiority.
- Methods gives the prespecified grid, comparison rules, failure threshold, equal-scenario weighting, and the no-empirical-data boundary.

## Claim boundary

Hidden synthetic utility is not AUROC. The simulation characterizes candidate-bank locking under the specified utility. It does not establish predictive superiority, unbiased generalization, external validity, participant-resampling stability, biomarker stability, clinical utility, or globally optimal feature selection.

## Validation

- Current main PDF after the later panel-label typography QA: 16 pages, SHA-256 `021ffb0d9a263116c4653f5994b3ff2dcdb9aff62ac35eebf9bb0ecd6c423671`.
- Supplementary PDF: 42 pages, SHA-256 `18d0fd213ac6dd27c6efc3d5ccd7c09da1f8c170ac06886a66488d326c5db45e`.
- Both LuaLaTeX/BibTeX builds passed.
- Final logs contain no substantive warning, undefined-reference, multiply-defined-label, overfull/underfull-box, duplicate-destination, or oversized-float match.
- All 58 rendered pages were inspected in contact sheets; no new blank page, clipping, overlap, obstructed label, or missing axis was found.
- `scripts/validate_locking_simulation_integration.py` passed every frozen-value, workload, feasibility, decision-path, hash, style, label, and citation check. Its machine-readable result is `supplementary_data/locking_rule_simulation/INTEGRATION_VALIDATION.json`.

The complete file inventory is `SIMULATION_SUPPLEMENT_CHANGED_FILE_INVENTORY.csv`.
