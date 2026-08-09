# WrapEvoFS manuscript reproducibility

This private peer-review repository contains the submission-stage WrapEvoFS manuscript, complete LuaLaTeX/Overleaf source, aggregate audit tables, figure-generation code, formal regret-locking proofs, and validation records.

The companion software package is maintained separately at [junseoparkX/wrapevofs-package](https://github.com/junseoparkX/wrapevofs-package). Package-owned software is licensed under BSD-3-Clause; this repository does not duplicate the package source.

## Current submission package

- [`manuscript/latex_v12_overleaf/main.pdf`](manuscript/latex_v12_overleaf/main.pdf): 16-page main article.
- [`manuscript/latex_v12_overleaf/supplementary_information.pdf`](manuscript/latex_v12_overleaf/supplementary_information.pdf): 42-page Supplementary Information.
- `manuscript/latex_v12_overleaf/figures/`: five main figures and Supplementary Figures S1--S24, including editable/vector assets where available.
- `manuscript/latex_v12_overleaf/tables/`: main and Supplementary LaTeX table sources through Supplementary Table S25.
- `manuscript/latex_v12_overleaf/regret_locking_formalization/`: propositions, proofs, complexity analysis, implementation crosswalk, and property-test report.
- `manuscript/latex_v12_overleaf/supplementary_data/`: non-identifying aggregate source tables and provenance records used by the current displays.
- `manuscript/latex_v12_overleaf/scripts/`: deterministic presentation, validation, inventory, and submission-archive builders.

The current PDFs are SHA-256 pinned in [`manuscript/latex_v12_overleaf/V12_VALIDATION_REPORT.md`](manuscript/latex_v12_overleaf/V12_VALIDATION_REPORT.md). The final display-citation audit, changed-file inventory, and figure-source manifests are retained beside the manuscript.

## Scientific boundary

The formal locking guarantee is limited to the configured empirical development-CV score gap within the supplied candidate bank. It does not establish predictive superiority, unbiased generalization, external validity, biomarker stability, participant-resampling stability, statistical certainty, or clinical utility.

Repository preparation did not rerun GA, RFECV, Direct selection, Bayesian analysis, STABL, BLiP, or any empirical feature-selection experiment. The current supplementary addenda use the explicitly documented frozen signatures, saved candidate banks, saved aggregate outputs, and authorized post-freeze evaluations described in the validation reports.

## Data boundary

Participant-level ADNI, AMP-AD, CGGA, and private-radiomics data are not redistributed. Provider-controlled files, credentials, raw predictions, model binaries, checkpoints, DICOM images, masks, and private archives are excluded. See [`DATA_BOUNDARIES.md`](DATA_BOUNDARIES.md).

## Reproduction

See [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for independent main/Supplementary builds and the distinction between reproducible aggregate rendering and controlled-input analyses.

## Release status

This repository is intended for controlled manuscript review until the authors approve public release and complete the remaining ethics, declaration, ADNI DPC, and repository-access checks documented in `manuscript/latex_v12_overleaf/AUTHOR_CONFIRMATION_REQUIRED.md` and `manuscript/latex_v12_overleaf/V12_VALIDATION_REPORT.md`.
