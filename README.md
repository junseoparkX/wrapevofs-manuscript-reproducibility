# WrapEvoFS manuscript reproducibility

[![Reproducibility checks](https://github.com/junseoparkX/wrapevofs-manuscript-reproducibility/actions/workflows/reproducibility.yml/badge.svg)](https://github.com/junseoparkX/wrapevofs-manuscript-reproducibility/actions/workflows/reproducibility.yml)
[![Software release](https://img.shields.io/badge/software-v0.2.0-2f6f8f)](https://github.com/junseoparkX/wrapevofs-package/releases/tag/v0.2.0)
[![PyPI](https://img.shields.io/pypi/v/wrapevofs.svg)](https://pypi.org/project/wrapevofs/)

This repository contains the submission manuscript, Supplementary Information,
non-identifying aggregate source data, deterministic figure builders, formal
locking-rule documentation, and validation records for **WrapEvoFS enables
auditable feature compression with regret-constrained representative locking**.

The maintained Python implementation is available from the
[WrapEvoFS software repository](https://github.com/junseoparkX/wrapevofs-package),
[GitHub Release v0.2.0](https://github.com/junseoparkX/wrapevofs-package/releases/tag/v0.2.0),
and [PyPI](https://pypi.org/project/wrapevofs/0.2.0/).

## Submission files

- [Main article](manuscript/source/main.pdf): 18 pages, five main figures, and two main tables.
- [Supplementary Information](manuscript/source/supplementary_information.pdf): 51 pages, Supplementary Figures S1--S28, and Supplementary Tables S1--S28.
- [Source Data](manuscript/source/documentation/submission/WrapEvoFS_Source_Data.xlsx): display-indexed, non-identifying source data for every main and Supplementary figure and table.
- [LaTeX source](manuscript/source/): independently compilable main and Supplementary entry points.
- [Validation report](manuscript/source/documentation/validation/VALIDATION_REPORT.md): build, numerical, citation, and visual-QA checks.
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

Earlier manuscript states are retained in Git history rather than duplicated in
the current tree.

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
