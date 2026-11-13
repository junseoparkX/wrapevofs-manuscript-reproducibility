# WrapEvoFS manuscript reproducibility

[![Reproducibility checks](https://github.com/junseoparkX/wrapevofs-manuscript-reproducibility/actions/workflows/reproducibility.yml/badge.svg)](https://github.com/junseoparkX/wrapevofs-manuscript-reproducibility/actions/workflows/reproducibility.yml)
[![Software release](https://img.shields.io/badge/software-v0.3.0-2f6f8f)](https://github.com/junseoparkX/wrapevofs-package/releases/tag/v0.3.0)
[![PyPI](https://img.shields.io/pypi/v/wrapevofs.svg)](https://pypi.org/project/wrapevofs/)

This repository contains the submission manuscript, Supplementary Information,
non-identifying aggregate source data, deterministic figure builders, formal
locking-rule documentation, and validation records for **WrapEvoFS enables
auditable feature compression with regret-constrained representative locking**.

The maintained Python implementation is available from the
[WrapEvoFS software repository](https://github.com/junseoparkX/wrapevofs-package),
[GitHub Release v0.3.0](https://github.com/junseoparkX/wrapevofs-package/releases/tag/v0.3.0),
and [PyPI](https://pypi.org/project/wrapevofs/0.3.0/).

Current manuscript: **v20, 12 November 2026**. The narrative foregrounds the decision problem, compression, and explicit predictive trade-offs. Fixed 0.01 reference benchmarks are retained. A separate exploratory 240-run study evaluates development-only allowance calibration, including complete enumeration of observed score-gap breakpoints. Its fitted overlap gains do not establish predictive superiority or unseen-seed reproducibility. All four policies and paired AUROC contrasts are reported.

The updated main and supplementary PDFs have been rebuilt and visually checked. Supplementary Methods S1.15 and Table S32 document calibration; the original nested benchmark, numerical tables, and source data remain preserved.

## Submission files

- [Main article](manuscript/source/main.pdf): 21 pages, five main figures, and two main tables.
- [Supplementary Information](manuscript/source/supplementary_information.pdf): 60 pages, Supplementary Figures S1--S29, and Supplementary Tables S1--S32.
- [Source Data](manuscript/source/documentation/submission/WrapEvoFS_Source_Data.xlsx): display-indexed reference source data; the new Table S32 data are supplied separately in the calibration CSVs.
- [Calibration inputs, results, and portable script](manuscript/source/supplementary_data/tolerance_calibration/): candidate masks/development scores and all-policy results without participant records.
- [LaTeX source](manuscript/source/): independently compilable main and Supplementary entry points.
- [Current version manifest](manuscript/source/CURRENT_MANUSCRIPT.json): frozen source/artwork hashes and version-specific page/display counts.
- [Display map](manuscript/source/documentation/DISPLAY_MAP.md) and [figure-source manifest](manuscript/source/documentation/FIGURE_SOURCE_DATA_MANIFEST.csv): claim-to-display and display-to-source mappings.

## Repository structure

```text
manuscript/source/
|-- main.tex, supplementary_information.tex
|-- main.pdf, supplementary_information.pdf
|-- sections/                 manuscript text
|-- figures/                  publication assets
|-- tables/                   LaTeX table sources
|-- scripts/                  deterministic builders and validators
|-- supplementary_data/       non-identifying aggregate source data
|-- revision_outputs/         aggregate locking and presentation audits
|-- documentation/            analysis and validation records
`-- regret_locking_formalization/
                               propositions, proofs, complexity, and crosswalks
```

One-time editing utilities and duplicate working CSVs have been removed from
the current tree. Exact historical CSV paths resolve through
[the canonical-source alias map](manuscript/source/documentation/AGGREGATE_PATH_ALIASES.json).
All manuscript PDFs, artwork, canonical results and scientific audit records remain preserved.
Earlier states remain in Git history.

## Reproduce and validate

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for environment setup, manuscript
build commands, deterministic validators, and figure-rebuild entry points.
[DATA_BOUNDARIES.md](DATA_BOUNDARIES.md) defines the included aggregate materials
and the controlled data that are not redistributed.

The repository supports independent manuscript compilation and regeneration of
figures backed by the included aggregate sources. Raw-to-result reproduction for
controlled datasets additionally requires authorized source access and the
source-specific preprocessing described in the manuscript.

The formal locking result concerns empirical score-gap feasibility within a
supplied finite candidate bank; its interpretation is stated in the manuscript.

## Citation and licensing

Citation metadata are provided in [CITATION.cff](CITATION.cff). The companion
software is distributed under the BSD 3-Clause License. Manuscript text,
figures, tables, and aggregate research artifacts are not covered by the
software license; see [LICENSE_STATUS.md](LICENSE_STATUS.md).

The opt-in `calibrate_tolerance` API is available in software v0.3.0. Reference benchmarks retain their recorded v0.2.0 implementation and defaults.
