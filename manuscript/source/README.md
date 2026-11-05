# Manuscript source

This directory is the authoritative, submission-facing WrapEvoFS manuscript package.

This is the current v19 package, prepared on 5 November 2026. The main PDF has 19 pages, five figures and two tables. Supplementary Information has 55 pages, 29 figures and 30 tables. V19 adds fixed-bank CV-score reweighting and equal-center weighting sensitivity, with approved main figures and polished supplementary artwork. Earlier v18 documentation remains historical; see `V19_README.md` for the version history. The latest clarification updates four method/terminology explanations while preserving all results and figure assets; see documentation/validation/V19_MINIMAL_CLARIFICATIONS_20261105.md.

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
- `documentation/analyses/TCGA_MATCHED_COMPARATOR_RESULTS.md`: exact interpretation of the checksum-frozen selector-layer benchmark.
- `documentation/submission/NATURE_COMMUNICATIONS_ALIGNMENT.md`: journal-format alignment summary.
- `documentation/submission/WrapEvoFS_Source_Data.xlsx`: display-indexed, non-identifying source data for all main and Supplementary figures and tables.
- `documentation/submission/`: completed Nature Communications reporting forms and cover letter.
- `documentation/validation/TCGA_SCNV_PROVENANCE_AUDIT.md`: label-blind audit of the supplied 5,000-feature cleaned SCNV boundary.
- `documentation/validation/PRIVATE_RADIOMICS_UPSTREAM_PROVENANCE.md`: mapping from the DICOM-to-radiomics handoff to the manuscript's upstream construction boundary.
- `documentation/DISPLAY_MAP.md`: main and Supplementary display roles.
- `documentation/validation/SUPPLEMENTARY_STRENGTHENED_RENUMBERING.json`: editorial-only first-citation renumbering map.
- `documentation/FIGURE_SOURCE_DATA_MANIFEST.csv`: figure-to-source mapping.

## Build

```bash
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error main.tex
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error supplementary_information.tex
```

The formal locking guarantee concerns empirical development-CV score-gap feasibility within a supplied candidate bank. Scientific interpretation and study-design boundaries are stated in the manuscript.
