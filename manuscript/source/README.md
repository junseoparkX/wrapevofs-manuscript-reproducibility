# Manuscript source

This directory is the authoritative, submission-facing WrapEvoFS manuscript package.

## Entry points

- `main.tex` and `main.pdf`: main article.
- `supplementary_information.tex` and `supplementary_information.pdf`: independently compilable Supplementary Information.
- `sections/`: main and Supplementary manuscript text.
- `references.bib`: bibliography database.

## Reproducibility assets

- `figures/`: current main and Supplementary publication assets.
- `tables/`: main and Supplementary LaTeX table sources.
- `scripts/`: deterministic figure builders, validators, and archive tooling.
- `supplementary_data/`: non-identifying aggregate inputs and provenance records.
- `revision_outputs/`: aggregate audit outputs used by manuscript displays.
- `regret_locking_formalization/`: mathematical propositions, proofs, complexity analysis, implementation correspondence, and property-test documentation.
- `documentation/`: analysis reports, validation records, and submission checklists, separated from the build source.

## Navigation

- `documentation/validation/VALIDATION_REPORT.md`: current build and scientific-integrity checks.
- `documentation/DISPLAY_MAP.md`: main and Supplementary display roles.
- `documentation/FIGURE_SOURCE_DATA_MANIFEST.csv`: figure-to-source mapping.
- `documentation/submission/AUTHOR_CONFIRMATION_REQUIRED.md`: remaining non-computational submission actions.

## Build

```bash
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error main.tex
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error supplementary_information.tex
```

The formal locking guarantee concerns only empirical development-CV score-gap feasibility within a supplied candidate bank. It is not a claim of predictive superiority, external validity, biomarker stability, or unbiased generalization.
