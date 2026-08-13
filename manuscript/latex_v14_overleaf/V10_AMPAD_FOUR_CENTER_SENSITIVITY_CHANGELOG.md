# V10 AMP-AD four-center configuration-comparison changelog

Date: 2026-08-06 (America/Los_Angeles)

## Starting point

V10 was cloned from the authoritative `latex_v9_overleaf` directory. V9 was not edited. Main Figures 1--5, existing held-out results, and automatic figure/table numbering were retained.

## New evidence integrated

- Completed design: 120 newly executed GPU GA runs, five seeds for each of 24 Small/Reference center--branch--cap conditions across Emory, Mayo, Mount Sinai, and Rush.
- Remaining-90 recommended-run bundle SHA-256: `601876c745a00f86039d06c49448b5791053b30a8dc5f9ebfc620aec86f0ce21`.
- Remaining-90 result bundle SHA-256: `89f86d764ed755e55c0626a93d96aa78670ac5481ed0719771b566dacb8599e5`.
- Validation: 90/90 new runs complete, 18/18 new conditions lock-ready, 0 invalid, 0 errors, 0 warnings, and no held-out access detected.
- Combined target fidelity: aggregate locked absolute target deviation 216 under the matched original configuration versus 137 under the updated configuration; 12 of 24 conditions were better under the updated configuration, 6 were unchanged, and 6 were worse.
- Objective-flattening diagnostics: zero run-best values under the zero-truncation diagnostic 4/120 versus 0/120; all-zero-generation diagnostic 673 versus 333; actual updated-mode uniform-sampling fallbacks 0.
- Locking: maximum selected empirical development-CV regret 0.0083473 under the prespecified 0.01 tolerance.
- Runtime: 51.77 aggregate GPU-hours.

## Manuscript integration

- Abstract: concise four-center development-only result and held-out boundary.
- Methods: 24-condition design, untruncated objective, canonical finite-precision reduction order, fixed development-CV re-scoring, and strict regret-constrained lock.
- Results: aggregate and heterogeneous center/branch findings, diagnostics, score-gap summary, runtime, and claim boundary.
- Discussion and conclusion: mechanism interpretation without predictive-superiority or generalization claims.
- Supplementary Figure S18: revised in place to display the complete four-center condition and aggregate results.
- Supplementary Table S16: revised in place with aggregate, complete condition-level, and locking/audit panels.
- `supplementary_data/recommended_mode_120_run/`: compact machine-readable validation and audit bundle.

## Disclosed implementation difference

The older supplied helper used source run ID after its historical floating reduction path. The current package uses the finalized canonical content-derived mask-hash rule. For Mount Sinai/SVM-L1/Reference, runs 3 and 5 have the same exact peer-Jaccard multiset but differ by one IEEE-754 unit in the last place under historical versus canonical reduction order. The authoritative package selects run 5 (17 features; regret 0.0037), while the older helper selected run 3 (17 features; regret 0). Both are eligible and target-count summaries are unchanged. This difference is disclosed in Supplementary Table S16 and the audit bundle; no stable-hash redesign or empirical-result repair was performed.

## Claim boundary

The added evidence is development-only. It supports more informative objective behavior, better aggregate target fidelity under the updated configuration in the tested settings, deterministic strict-regret locking, and the absence of actual sampling fallback. Because both candidate generation and locking differ, the comparison does not isolate the causal effect of either component. It does not establish held-out improvement, predictive superiority, unbiased generalization, external validity, biomarker stability, or global feature-selection optimality. High-cap conditions were not rerun.
