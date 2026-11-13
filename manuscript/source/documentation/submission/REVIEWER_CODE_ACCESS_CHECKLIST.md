# Reviewer code-access checklist

## Software identity and installation

- [x] Public package repository: https://github.com/junseoparkX/wrapevofs-package
- [x] Frozen reference analysis release: [v0.2.0](https://github.com/junseoparkX/wrapevofs-package/releases/tag/v0.2.0).
- [x] Opt-in tolerance-calibration API: [v0.3.0](https://github.com/junseoparkX/wrapevofs-package/releases/tag/v0.3.0), [PyPI](https://pypi.org/project/wrapevofs/0.3.0/).
- [x] License: BSD 3-Clause, copyright 2026 Junseo Park.
- [x] Python 3.10/3.11/3.12 CI, distribution build, clean installation, API and CLI checks passed for v0.3.0; 157 tests passed, including 44 calibration tests.
- [x] Install calibration release with `python -m pip install wrapevofs==0.3.0`; retain `wrapevofs==0.2.0` for the recorded reference environment. Source and optional-selector installations are documented in the package README.
- [x] Current changes do not alter reference configuration, GA, or single-bank locking behavior. No new package release is required for this manuscript correction.

## Reviewer examples and method documentation

- [x] `examples/toy_regret_locking.py`: fixed-CV candidate-locking demonstration.
- [x] `examples/toy_tolerance_calibration.py`: synthetic development-only calibration.
- [x] `examples/quickstart.py`: Direct/RFECV API example.
- [x] `scripts/run_development_only_smoke.py`: optional shortened synthetic GA smoke check.
- [x] `docs/TOLERANCE_CALIBRATION.md`, `docs/METHOD_AND_METRICS.md`, `docs/CLI_AND_API.md`, and `docs/ARTIFACT_SCHEMA.md` describe the APIs and boundary.
- [x] `calibrate_tolerance(..., delta_grid=[0, .0025, .005, .0075, .01, .015, .02])` reproduces the grid example; omitting `delta_grid` reproduces observed-breakpoint sensitivity.
- [x] Software examples are CPU-only and require no restricted data or GPU/cuML hardware.

## Data and access boundary

- [x] The package README states that participant-level, provider-controlled, restricted derivatives, figures, and private research archives are not distributed in the software repository.
- [x] The release-candidate security/data-boundary audit recorded a clean credential/path/restricted-data inventory scan.
- [x] Reviewer examples use synthetic or nonbiomedical toy data.
- [x] Both source repositories are publicly accessible without collaborator invitations.
- [x] Package installation and reviewer examples require no restricted data.

## Manuscript analyses and source files

- [x] Public reproducibility repository: https://github.com/junseoparkX/wrapevofs-manuscript-reproducibility
- [x] Five main figures and 29 Supplementary Figures are mapped in `documentation/FIGURE_SOURCE_DATA_MANIFEST.csv`.
- [x] Table S31: all-candidate nested-TCGA diagnostic, `supplementary_data/candidate_outer_audit/`.
- [x] Table S32 / Methods S1.15: exploratory calibration, conditional AUROC contrasts, separate reserved-seed check, and breakpoint sensitivity in `supplementary_data/tolerance_calibration/`. All-240 fitted overlap is not independent validation.
- [x] Table S33 / Methods S1.16: the original protocol-defined four-bank R=5/10/20 comparison of those same 240 GA runs. All 108 pairs, 72 selections, both scorers, frozen protocol/code, and independent verification script are in `supplementary_data/seed_bank_reproducibility/`.
- [x] The Boruta-RF exported target metadata correction (18 to 8) retains the original CSV and an exact provenance record. Every mask, score, selected signature, and outcome is unchanged.
- [x] The original Source Data workbook remains unchanged; new S32 and S33 observations are in their separate CSV folders.
- [x] Current PDF counts and validation status are reported in `NATURE_COMMUNICATIONS_ALIGNMENT.md` and `documentation/V20_REVIEW_CORRECTIONS_VALIDATION.json`.

## Submission access

Editors and reviewers can inspect both public repositories, install the tagged releases, and run synthetic examples and the mask/score-only S32 and S33 reconstructions without participant-level access. Recomputing models and participant-bootstrap intervals requires the data access described in the manuscript.
