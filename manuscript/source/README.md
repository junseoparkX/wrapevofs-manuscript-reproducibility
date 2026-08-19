# Manuscript source

This directory is the authoritative, submission-facing WrapEvoFS manuscript
package.

## Entry points

- `main.tex` and `main.pdf`: main article.
- `supplementary_information.tex` and `supplementary_information.pdf`: independently compilable Supplementary Information.
- `sections/`: main and Supplementary manuscript text.
- `references.bib`: bibliography database.

## Reproducibility assets

- `figures/`: current main and Supplementary publication assets.
- `tables/`: main and Supplementary LaTeX table sources.
- `scripts/`: deterministic figure builders and validators.
- `supplementary_data/`: non-identifying aggregate inputs and provenance records.
- `revision_outputs/`: aggregate audit outputs used by manuscript displays.
- `regret_locking_formalization/`: propositions, proofs, complexity analysis, implementation correspondence, and property-test documentation.
- `documentation/`: analysis reports and validation records separated from the build source.

## Navigation

- `documentation/validation/VALIDATION_REPORT.md`: current build and scientific-integrity checks.
- `documentation/analyses/TCGA_MATCHED_COMPARATOR_RESULTS.md`: checksum-frozen selector-layer benchmark interpretation.
- `documentation/validation/TCGA_SCNV_PROVENANCE_AUDIT.md`: label-blind audit of the supplied 5,000-feature SCNV boundary.
- `documentation/validation/PRIVATE_RADIOMICS_UPSTREAM_PROVENANCE.md`: non-identifying VGH DICOM-to-radiomics construction boundary.
- `documentation/DISPLAY_MAP.md`: roles of the main and Supplementary displays.
- `documentation/FIGURE_SOURCE_DATA_MANIFEST.csv`: figure-to-source mapping.

## Build

```bash
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error main.tex
latexmk -g -lualatex -interaction=nonstopmode -halt-on-error supplementary_information.tex
```

The locking guarantee concerns empirical development-score feasibility within a
supplied finite candidate bank. Full definitions and claim boundaries are given
in the manuscript and Supplementary Methods.
