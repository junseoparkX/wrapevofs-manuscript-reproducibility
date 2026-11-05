# Current manuscript source

Use `main.pdf` (19 pages), `supplementary_information.pdf` (55 pages), and
`documentation/submission/WrapEvoFS_Source_Data.xlsx`. This is v19, prepared
5 November 2026: five main figures, two main tables, 29 supplementary figures
and 30 supplementary tables.

The manuscript sources, tables, figures and result values are frozen in
`CURRENT_MANUSCRIPT.json`. Repository housekeeping does not revise them.

- `sections/`, `tables/`, `references.bib`: manuscript text and references.
- `figures/` and the supplementary figure paths specified by the TeX: publication assets.
- `supplementary_data/`, `revision_outputs/`: aggregate results, protocols and audits.
- `scripts/`: retained analysis/rendering helpers and current validators.
- `regret_locking_formalization/`: final propositions, proofs, complexity and package crosswalks.
- `documentation/DISPLAY_MAP.md`: printed display numbering and roles.
- `documentation/FIGURE_SOURCE_DATA_MANIFEST.csv`: display-to-source mapping.
- `documentation/AGGREGATE_PATH_ALIASES.json`: historical duplicate paths mapped to canonical CSVs.

Build and verification commands are in the repository-root `REPRODUCIBILITY.md`.
Source-data access boundaries are in `DATA_BOUNDARIES.md`. Historical editing
utilities and proposals remain in Git history. Cover letters and publisher forms
are part of the separately prepared coauthor submission ZIP.
