# V12 repository update

Date: 2026-08-09

## Repository organization

- Replaced the obsolete flattened V9 manuscript tree with the authoritative `manuscript/latex_v12_overleaf/` submission package.
- Retained the repository-level `analysis/`, `audits/`, and `reports/` directories for historical aggregate provenance.
- Updated the root README, reproducibility guide, citation metadata, and ignore rules for the current private peer-review state.
- Added only the aggregate CGGA plot-source tables required by the Figure 5 provenance validator; participant-level data and raw predictions remain excluded.

## Current outputs

- Main article: 16 pages; SHA-256 `021ffb0d9a263116c4653f5994b3ff2dcdb9aff62ac35eebf9bb0ecd6c423671`.
- Supplementary Information: 42 pages; SHA-256 `b9f451183daa1ca309b0e3bb0fdb5bc5ca02386b2a2a4f863590b3dbb3714d25`.
- Figures: five main figures and Supplementary Figures S1--S24.
- Tables: three main tables and Supplementary Tables S1--S25.

## Validation

The repository checkout passed the frozen-value, main-panel-label, Figure 5 provenance, radiomics integration, and controlled locking-simulation integration validators. The final source package had previously completed independent LuaLaTeX/BibTeX builds of both PDFs with zero warning/error-pattern or layout-diagnostic matches.

No GA, RFECV, Direct selection, feature-selection experiment, or empirical numerical result was rerun or changed for this repository update.
