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
- `CHANGELOG.md`: submission-facing scientific and editorial decisions.
- `documentation/analyses/TCGA_MATCHED_COMPARATOR_RESULTS.md`: exact interpretation of the checksum-frozen selector-layer benchmark.
- `documentation/submission/NATURE_COMMUNICATIONS_ALIGNMENT.md`: journal-format alignment and outstanding submission actions.
- `documentation/validation/TCGA_SCNV_PROVENANCE_AUDIT.md`: label-blind audit of the supplied 5,000-feature cleaned SCNV boundary.
- `documentation/validation/PRIVATE_RADIOMICS_UPSTREAM_PROVENANCE.md`: mapping from the DICOM-to-radiomics handoff to the manuscript's upstream construction boundary.
- `documentation/DISPLAY_MAP.md`: main and Supplementary display roles.
- `documentation/validation/SUPPLEMENTARY_STRENGTHENED_RENUMBERING.json`: editorial-only first-citation renumbering map.
- `documentation/FIGURE_SOURCE_DATA_MANIFEST.csv`: figure-to-source mapping.
- `documentation/submission/AUTHOR_CONFIRMATION_REQUIRED.md`: remaining non-computational submission actions.

## Build

```bash
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error main.tex
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error supplementary_information.tex
```

The formal locking guarantee concerns only empirical development-CV score-gap feasibility within a supplied candidate bank. It is not a claim of predictive superiority, external validity, biomarker stability, or unbiased generalization.
