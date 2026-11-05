# Reviewer code-access checklist

## Frozen software identity

- [x] Repository: `https://github.com/junseoparkX/wrapevofs-package`
- [x] Repository state: public
- [x] Immutable release: `https://github.com/junseoparkX/wrapevofs-package/releases/tag/v0.2.0`
- [x] Release tag: `v0.2.0`
- [x] Package version: `0.2.0`
- [x] License: BSD 3-Clause, copyright 2026 Junseo Park
- [x] PyPI distribution: `https://pypi.org/project/wrapevofs/0.2.0/`
- [x] Manuscript reproducibility repository: `https://github.com/junseoparkX/wrapevofs-manuscript-reproducibility`

## Installation and environment

- [x] Supported Python versions: 3.10, 3.11, and 3.12.
- [x] Release installation is documented: `python -m pip install wrapevofs==0.2.0`.
- [x] Source installation is documented: `python -m pip install -e ".[dev]"`.
- [x] Optional selectors are documented: `python -m pip install -e ".[all]"`.
- [x] CPU CI workflow exists at `.github/workflows/ci.yml`.
- [x] GitHub Actions covers Python 3.10/3.11/3.12 CPU jobs and build/clean-install validation.
- [x] The release-candidate audit records 111/111 tests, Ruff, compileall, metadata validation, wheel/sdist build, and source/wheel/sdist installation as passing on Python 3.12.13.
- [x] The public reviewer demonstration is CPU-only; GPU/cuML hardware is not required.

## Minimal reproducible examples

- [x] `examples/toy_regret_locking.py`: nonbiomedical, fixed-CV candidate-locking demonstration; no GA and no manuscript analysis.
- [x] `examples/quickstart.py`: small Direct/RFECV API quickstart.
- [x] `scripts/run_development_only_smoke.py`: optional synthetic pipeline smoke with a deliberately shortened GA; reviewers need not run it to inspect the locking contract.
- [x] `validate_locking_artifact_directory` checks the toy audit output and schema.

## Central method and configuration files

- [x] Package implementation: `src/wrapevofs/`.
- [x] Recommended configuration: `configs/recommended_regret_constrained.yaml`.
- [x] Locking documentation: `docs/METHOD_AND_METRICS.md`, `docs/CLI_AND_API.md`, and `docs/ARTIFACT_SCHEMA.md`.
- [x] Locking property tests: `tests/test_locking.py` and `tests/test_release_contract.py`.
- [x] All five main and 29 Supplementary figures are mapped to presentation builders or explicitly labeled archived source routes and machine-readable summary inputs in `documentation/FIGURE_SOURCE_DATA_MANIFEST.csv`.

## Data and access boundary

- [x] The package README states that participant-level, provider-controlled, restricted derivatives, figures, and private research archives are not distributed in the software repository.
- [x] The release-candidate security/data-boundary audit recorded a clean credential/path/restricted-data inventory scan.
- [x] Reviewer examples use synthetic or nonbiomedical toy data.
- [x] Both source repositories are publicly accessible without collaborator invitations.
- [x] Package installation and reviewer examples require no restricted data.

## Submission access

Editors and reviewers can inspect the public source repositories, install the immutable `v0.2.0` package release from PyPI, and run the synthetic examples without access to restricted participant-level data.

## v19 analysis additions (5 November 2026)

- Fixed-bank CV-score reweighting: `supplementary_data/cv_score_sensitivity/` includes the two non-participant input CSVs, protocol, executable analysis, aggregate results and integrity checks.
- Equal-center weighting: `supplementary_data/ampad_center_sensitivity/` includes aggregate tables and the analysis script; rerunning intervals requires separately authorized saved predictions.
- Current manuscript: main 19 pages, five figures and two tables; Supplementary Information 55 pages, 29 figures and 30 tables.
- The source-data workbook indexes 66 display items and preserves the original aggregate observations.
- Existing 111-test software release verification above is historical; this submission refresh does not change the package release or claim to rerun its test suite.
