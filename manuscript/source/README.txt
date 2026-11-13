WrapEvoFS v20, prepared 12 November 2026

Build main.tex and supplementary_information.tex with LuaLaTeX:
  latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex
  latexmk -lualatex -interaction=nonstopmode -halt-on-error supplementary_information.tex
Cover source: submission_documents/latex/Cover_Letter_Nature_Communications.tex
On a restricted Windows workspace set TEXMFVAR and TEXMFCACHE to a writable temporary directory.

Figure data geometry and original table/primary numeric values are preserved from v19; comparator display names are standardized in the corrected v20. Main figures are renumbered by their new narrative order. The v19_work/ directory contains only required preserved supplementary-figure assets from the prior package, not experiment history.
Supplementary Table S31 and supplementary_data/candidate_outer_audit/ add the verified retrospective fixed-bank diagnostic. Participant arrays, prediction records and private models are not included. The source-data workbook is display-indexed for v20 and contains a new TableS31 sheet.
V20_CHANGES_KO.txt describes the targeted scientific edits. documentation/V20_VALIDATION.json records preservation/build/source-link checks.

Corrected v20: see V20_REVIEW_FIXES_KO.txt for reference/order/name fixes, independently reconstructed original agreement summaries, and the delta=0.01 development-score-budget rationale.

Latest v20 calibration update: see V20_CALIBRATION_UPDATE_KO.txt and documentation/V20_CALIBRATION_VALIDATION.json. The fixed 0.01 benchmarks are retained as reference protocols. Supplementary Table S32 and supplementary_data/tolerance_calibration/ report the separate exploratory 240-run calibration study. Its aggregate CSVs are provided separately; the existing source-data workbook is unchanged.


Current review correction: see V20_REVIEW_RESPONSE_KO.txt. S33 restores the protocol-defined four-bank seed comparison; S32 is a separate exploratory calibration of the same240 runs. Detailed provenance and original-result preservation are in documentation/V20_REVIEW_CORRECTIONS_VALIDATION.json.
