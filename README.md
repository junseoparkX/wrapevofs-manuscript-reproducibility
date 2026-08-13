# WrapEvoFS manuscript reproducibility

This repository contains the current submission manuscript, Supplementary Information, aggregate source data, deterministic figure builders, formal locking-rule documentation, and validation records for **WrapEvoFS: Auditable Stochastic Feature Compression under Development-CV Regret Constraints**.

The companion Python package is maintained separately at [junseoparkX/wrapevofs-package](https://github.com/junseoparkX/wrapevofs-package).

## Manuscript

- [Main article](manuscript/source/main.pdf) — 19 pages, six main figures, and three main tables.
- [Supplementary Information](manuscript/source/supplementary_information.pdf) — 46 pages, Supplementary Figures S1–S27, and Supplementary Tables S1–S26.
- [LaTeX source](manuscript/source/) — independently compilable main and Supplementary entry points.
- [Validation report](manuscript/source/documentation/validation/VALIDATION_REPORT.md) — build, numerical, citation, and visual-QA checks.
- [Display map](manuscript/source/documentation/DISPLAY_MAP.md) and [figure-source manifest](manuscript/source/documentation/FIGURE_SOURCE_DATA_MANIFEST.csv) — claim-to-display and display-to-source mappings.

## Repository structure

```text
manuscript/source/
├── main.tex, supplementary_information.tex
├── main.pdf, supplementary_information.pdf
├── sections/                 manuscript text
├── figures/                  publication assets
├── tables/                   LaTeX table sources
├── scripts/                  deterministic builders and validators
├── supplementary_data/       non-identifying aggregate source data
├── revision_outputs/         aggregate audit outputs used by displays
├── documentation/            analysis, validation, and submission records
└── regret_locking_formalization/
                              propositions, proofs, complexity, and tests
```

Historical manuscript states are retained in Git history rather than duplicated in the current tree.

## Reproducibility scope

The repository supports independent manuscript compilation, regeneration of figures backed by included aggregate sources, and verification of the locking-rule and presentation audits. Participant-level ADNI, AMP-AD, CGGA, TCGA, and private-radiomics inputs are not redistributed. Raw-to-result reproduction for controlled datasets requires authorized data access and the source-specific preprocessing described in the manuscript.

The formal locking guarantee is limited to the configured empirical development-CV score gap within the supplied candidate bank. It does not establish predictive superiority, unbiased generalization, external validity, biomarker stability, statistical certainty, or clinical utility.

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for build and validation commands and [DATA_BOUNDARIES.md](DATA_BOUNDARIES.md) for the data-access boundary.

## Review status

This repository is maintained for controlled manuscript review. Before journal submission, the authors must complete the private-radiomics ethics wording, ADNI Data and Publications Committee review, and final all-author sign-off documented in the [author-confirmation checklist](manuscript/source/documentation/submission/AUTHOR_CONFIRMATION_REQUIRED.md).

## Citation and licensing

Citation metadata are provided in [CITATION.cff](CITATION.cff). The companion software is distributed under BSD-3-Clause. Manuscript text, figures, tables, and aggregate research artifacts are not covered by the software license; see [LICENSE_STATUS.md](LICENSE_STATUS.md).
