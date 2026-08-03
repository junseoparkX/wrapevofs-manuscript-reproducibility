# WrapEvoFS manuscript reproducibility

This repository contains the submission-stage WrapEvoFS manuscript, its complete LuaLaTeX/Overleaf source, aggregate audit tables, figure-generation code, formal regret-locking proofs, and revision validation records.

The companion software package is maintained separately at [junseoparkX/wrapevofs-package](https://github.com/junseoparkX/wrapevofs-package). Package-owned software is licensed under BSD-3-Clause. This repository does not duplicate the package source.

## Repository contents

- `manuscript/`: authoritative V9 manuscript source, 5 main figures, 18 supplementary figures, 39 table source files, bibliography, supplementary data, formal locking proofs, and the compiled 43-page PDF.
- `audits/`: frozen aggregate compression, regret, locking, metric-alignment, and penalty-flattening source tables used by the revision.
- `analysis/regret_revision/`: scripts and frozen plot-source CSVs used to produce the revision figures.
- `reports/`: manuscript consistency, figure, methods, and submission-readiness review records.

The authoritative compiled PDF is `manuscript/main.pdf` (SHA-256 `ede82ba2e668f77dcef7bd4c3d052eb06c29d376b5b72514d3ad8e807d288eda`). It identifies WrapEvoFS v0.2.0 as the peer-review submission release.

## Scientific boundary

The formal locking guarantee is limited to the configured empirical development-CV score gap within the supplied candidate bank. It does not establish predictive superiority, unbiased generalization, external validity, biomarker stability, participant-resampling stability, or statistical certainty.

No GA, feature-selection experiment, held-out evaluation, Bayesian analysis, STABL, BLiP, bootstrap analysis, or empirical manuscript analysis was rerun to construct this repository. Existing empirical numerical results were preserved.

## Data boundary

Participant-level ADNI, AMP-AD, and CGGA data and provider-controlled materials are not included. The aggregate CSVs are audit and plot-source tables, not participant-level matrices. See [DATA_BOUNDARIES.md](DATA_BOUNDARIES.md).

## Reproduction

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for manuscript compilation and the distinction between figure regeneration from frozen aggregate tables and analyses that require controlled source inputs.

## License status

The BSD-3-Clause license in the companion package applies only to package-owned software. No separate public license for the manuscript text, figures, tables, or aggregate research artifacts is asserted here; see [LICENSE_STATUS.md](LICENSE_STATUS.md).
