# Reviewer code-access checklist

## Frozen software identity

- [x] Repository: `https://github.com/junseoparkX/wrapevofs-package`
- [x] Repository state: private during manuscript review
- [x] Reviewed commit: `63a608351abfb9521437c0dceef869b42ddfa292`
- [x] Package version: `0.2.0`
- [x] License: BSD 3-Clause, copyright 2026 Junseo Park
- [x] Local reviewed checkout was clean at the commit above.
- [ ] Immutable release tag or archived reviewer snapshot: not yet created; use the full commit hash until one is created.

## Installation and environment

- [x] Supported Python versions: 3.10, 3.11, and 3.12.
- [x] Source installation is documented: `python -m pip install -e ".[dev]"`.
- [x] Optional selectors are documented: `python -m pip install -e ".[all]"`.
- [x] CPU CI workflow exists at `.github/workflows/ci.yml`.
- [x] The author-provided GitHub Actions record showed Python 3.10/3.11/3.12 CPU jobs and build/clean-install jobs passing after merge.
- [x] The release-candidate audit records 111/111 tests, Ruff, compileall, metadata validation, wheel/sdist build, and source/wheel/sdist installation as passing on Python 3.12.13.
- [ ] Real GPU/cuML execution was not validated for the release candidate and is not required for the CPU reviewer demonstration.

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
- [x] All five main and 19 Supplementary figures are mapped to their presentation builders or archived source routes and machine-readable summary inputs in `FIGURE_SOURCE_DATA_MANIFEST.csv`.

## Data and access boundary

- [x] The package README states that participant-level, provider-controlled, restricted derivatives, figures, and private research archives are not distributed in the software repository.
- [x] The release-candidate security/data-boundary audit recorded a clean credential/path/restricted-data inventory scan.
- [x] Reviewer examples use synthetic or nonbiomedical toy data.
- [ ] Before granting access, recheck the exact remote commit and collaborator list in GitHub.
- [ ] Add the editor/reviewer account through GitHub private-repository access, or provide an editor-approved private archive/link, and test access from a non-owner account.
- [ ] Record the access mechanism and date in the submission system; do not rely only on the phrase “access can be provided.”

## Submission action

The code itself is reviewable at the frozen commit. The remaining operational action is to grant and test private reviewer/editor access before submission. Public release, PyPI publication, DOI creation, and a GitHub Release are separate later decisions.
