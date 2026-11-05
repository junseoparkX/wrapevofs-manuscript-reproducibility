# Current validation

The authoritative manuscript is v19: 19 main pages and 55 supplementary pages.
`CURRENT_MANUSCRIPT.json` checks the frozen source, figure and secondary-setting
hashes. The repository's GitHub Actions workflow runs the current structural,
numerical, provenance, panel-label and PDF-layout checks.

The cleanup preserves every TeX source, bibliography, PDF, SVG, PNG, result-table
value and canonical analytic CSV. Removed CSV copies have an exact-content alias
in `documentation/AGGREGATE_PATH_ALIASES.json`. All controlled-input and negative-
result records retain their original scientific meaning.

Historical presentation reports and proposal patches can be recovered from
commit `883f5db5310cf265c19b1824622884edac191af6`; they do not describe the current
file inventory. See the repository-root `REPRODUCIBILITY.md` for current commands.
