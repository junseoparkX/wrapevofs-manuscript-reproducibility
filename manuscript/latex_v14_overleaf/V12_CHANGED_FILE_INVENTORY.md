# V12 changed-file inventory

This inventory covers the current V12 source and the final in-place QA pass. V11 remains unchanged.

## Entry points and shared formatting

- `main.tex`
- `supplementary_information.tex`
- `manuscript_preamble.tex`
- `references.bib`

## Scientific and editorial text

- `sections/main_text.tex`
- `sections/supplementary.tex`
- `tables/supplementary_algorithm_s1.tex`
- `tables/table_02.tex`, `tables/table_05.tex`, `tables/table_43.tex` (private-radiomics cohort, method boundary, and Supplementary Table S21)

## Main and Supplementary table layout/wording

- `tables/table_02.tex`, `table_03.tex`, `table_04.tex`
- `tables/table_29.tex`, `table_31.tex`, `table_32.tex`, `table_33.tex`, `table_34.tex`
- `tables/table_38.tex`, `table_39.tex`

## Figure assets and deterministic presentation fixes

- `figures/figure_1.pdf`, `figure_1.png`, `figure_1.svg`, `figure_1_editable_source_v2.svg`
- `figures/figure_2.pdf`, `figure_2.png`, `figure_2.svg`
- `figures/figure_3.png`, `figure_3_panel_label_source.svg`, `figure_4.png`, `figure_4.svg`, `figure_4_v11_source.svg`
- `figures/figure_5.pdf`, `figure_5.svg`, `figure_5.png` (native 170-mm CGGA redesign)
- `figures/figure_s9.png`, `figure_s9_prefinalqa_source.png`
- `figures/figure_s16.pdf`, `figure_s16.png`, `figure_s16.svg`, `figure_s16_prefinalqa_source.pdf`
- `scripts/build_v12_main_figure2.py`
- `scripts/build_v11_revision_figures.py`
- `scripts/build_gridfree_figure4_svg.py`, `figure4_render_wrapper.html`, `render_v12_figure4_from_svg.ps1`
- `scripts/figure_s16_render_wrapper.html`, `render_v12_figure_s16_from_svg.ps1`
- `scripts/final_qa_figure_microfixes.py`
- `scripts/normalize_main_panel_labels.py`, `validate_main_panel_labels.py`, `figure_1_render_wrapper.html`, `render_v12_figure1_from_svg.ps1`
- `figures/figure_s19_ab.png`, `figure_s19_cd.png`, `scripts/prepare_170mm_figure_assets.py`
- `revision_outputs/V12_MAIN_FIGURE2_HASHES.json`
- `revision_outputs/FIGURE4_GRID_REMOVAL_PROVENANCE.json`
- `revision_outputs/FINAL_QA_FIGURE_MICROFIX_HASHES.json`
- `figures/figure_s20.pdf`, `figures/figure_s20.svg`, `figures/figure_s20.png`
- `scripts/build_radiomics_s20.py`
- `scripts/build_cgga_figure5.py`
- `scripts/validate_cgga_figure5_provenance.py`
- `figures/figure_s21.pdf`, `figure_s21.svg`, `figure_s21.png`
- `figures/figure_s22.pdf`, `figure_s22.svg`, `figure_s22.png`
- `figures/figure_s23.pdf`, `figure_s23.svg`, `figure_s23.png`
- `scripts/build_postfreeze_results.py`
- `POSTFREEZE_ANALYSIS_FIGURE_MANIFEST.json`

## CGGA Figure 5 redesign

- `supplementary_data/cgga_figure5/` (three aggregate panel CSVs, exact upstream mapping, provenance README, pinned plotting requirements, and generated manifest)
- `FIGURE5_REDESIGN_REPORT.md`
- No GA, model fit, held-out prediction, or participant-level data were generated.

## Private-radiomics aggregate integration

- `supplementary_data/private_radiomics/` (non-identifying aggregate CSV/JSON audits and README only)
- `PRIVATE_RADIOMICS_ANALYSIS_REPORT.md`
- `scripts/validate_radiomics_integration.py`
- Participant matrices, identifiers, DICOM images, masks, prepared joblib files, checkpoints, and held-out prediction rows are not included.

## QA and submission documentation

- `README.md`
- `MAIN_SUPPLEMENTARY_FIGURE_MAP.md`
- `FIGURE_SOURCE_DATA_MANIFEST.csv`
- `FIGURE_180MM_STYLE_SOURCE_MANIFEST.md`
- `V12_PROVENANCE_AND_SCOPE.md`
- `V12_WORD_AND_DISPLAY_COUNTS.md`
- `V12_NATURE_COMMUNICATIONS_READINESS_GAP_REPORT.md`
- `V12_UNRESOLVED_AUTHOR_CONFIRMATIONS.md`
- `V12_CHANGELOG.md`
- `V12_VALIDATION_REPORT.md`
- `AUTHOR_CONFIRMATION_REQUIRED.md`
- `REVIEWER_CODE_ACCESS_CHECKLIST.md`
- `FINAL_QA_REPORT.md`
- `V12_DECLARATIONS_ETHICS_AND_ACKNOWLEDGEMENTS_REPORT.md`
- `PRIVATE_RADIOMICS_ETHICS_EMAIL_TO_MO.md`
- `ADNI_DPC_SUBMISSION_PACKET.md`
- `CHANGELOG.md`
- `MAIN_FIGURE_PANEL_LABEL_AUDIT.md`
- `SUPPLEMENTARY_GRAPHIC_CLEANUP_REPORT.md`

## Final reference, display-citation, and S19 formatting pass

- `sections/main_text.tex` -- adds the targeted literature context, PyRadiomics/IBSI/robustness citations, complete main-text coverage of numbered Supplementary displays, and explicit Supplementary Table S15 citation.
- `references.bib` -- formalizes the existing stability-selection, XGBoost, and Boruta records and adds six primary records for leakage, CV preprocessing bias, ensemble feature selection, perturbation robustness, IBSI, and PyRadiomics.
- `sections/supplementary.tex` -- replaces the split S19 descriptions with one complete caption and one non-caption continuation header.
- `V12_DISPLAY_CITATION_AUDIT.md` -- records one-to-one coverage of main and Supplementary displays.
- `tables/table_45.tex` -- corrects the Supplementary Table S23 note to point to Supplementary Figure S22c rather than main Figure 5c.
- `V12_WORD_AND_DISPLAY_COUNTS.md`, `V12_CHANGELOG.md`, and `V12_VALIDATION_REPORT.md` -- refreshed counts, hashes, build results, and render QA.
- `main.pdf` and `supplementary_information.pdf` -- rebuilt submission-facing outputs.

## QA utilities

- `scripts/count_v12_submission_words.py`
- `scripts/build_pdf_contact_sheets.py`
- `scripts/validate_final_qa_frozen_values.py`
- `scripts/build_v12_submission_archive.ps1`

## Generated outputs

- `main.pdf`
- `supplementary_information.pdf`
- `../WrapEvoFS_LaTeX_V12_Nature_Submission.zip`
- `../V12_SUBMISSION_ARCHIVE_SHA256.txt`

Generated LaTeX intermediates, local TeX caches, and rendered QA contact sheets are excluded from the submission ZIP.

## Post-freeze AMP-AD and CGGA addendum (2026-08-08)

The complete file-level inventory for this addendum and subsequent in-place figure QA is `POSTFREEZE_CHANGED_FILE_INVENTORY.csv` (258 rows; SHA-256 `9d645360c60f4d90a79cb1a5c47fa4a0a46dcdd32c99944b20246c1339212290`). It records relative path, category, public/private scope, byte size, and SHA-256 for:

- the Rush recovery and AMP-AD one-time held-out analysis directory;
- the CGGA coherent benchmark directory;
- the CGGA saved nested-bank re-lock directory;
- the simulation directory, which was excluded at the time of this dated addendum and later supplied the frozen summaries for the separately authorized S24/S25 integration;
- all aggregate manuscript `supplementary_data` copies;
- revised main/Supplementary source; restored main Figures 4 and 5; additive Supplementary Figures S21--S23 in PDF/SVG/PNG; Tables S22--S24; scripts, manifests, and reports;
- the completed 48-bank cross-lock outputs and regenerated Tables S19--S20; and
- local Poppler render-QA images, explicitly marked for exclusion from the submission archive.

Participant-level prediction files remain private analysis artifacts and are not present in manuscript `supplementary_data`.

## Supplementary graphic cleanup (2026-08-09)

- `figures/figure_s9.{pdf,svg,png}` -- native 170-mm rebuild from frozen aggregate values; the redundant right-side settings block was removed and panel c was expanded.
- `figures/figure_s21.{pdf,svg,png}`, `figure_s22.{pdf,svg,png}`, and `figure_s23.{pdf,svg,png}` -- interpanel spacing and long y-axis label placement repaired without changing plotted values.
- `scripts/build_cgga_s9_clean.py` and `supplementary_data/cgga_tuned_rf_s9/` -- deterministic S9 builder, compact frozen source CSVs, and output manifest.
- `scripts/build_postfreeze_results.py` -- automatic failure check for y labels intruding into a preceding axes.
- `sections/supplementary.tex`, figure manifests, QA reports, and `supplementary_information.pdf` -- caption, source routing, hashes, and rendered-page validation updated in place.

## Controlled locking-simulation integration (2026-08-09)

- `sections/main_text.tex`, `sections/supplementary.tex` -- claim-bounded Results, Discussion, main Methods, detailed Supplementary Methods, and S24/S25 citations.
- `figures/figure_s24.pdf`, `figures/figure_s24.svg`, `figures/figure_s24.png` -- deterministic 170-mm, grid-free, three-panel Supplementary Figure S24.
- `tables/table_47.tex` -- Supplementary Table S25 with primary operating characteristics, empirical-regret audit, and deterministic decision paths.
- `supplementary_data/locking_rule_simulation/` -- six compact aggregate source CSVs, extraction provenance, build/render manifests, and integration validation; no participant-level or empirical data.
- `scripts/build_locking_simulation_s24.py`, `scripts/figure_s24_render_wrapper.html`, `scripts/render_locking_simulation_s24.ps1`, `scripts/validate_locking_simulation_s24_integration.py` -- deterministic build, render, and validation route.
- `FIGURE_170MM_STYLE_SOURCE_MANIFEST.csv`, `FIGURE_170MM_STYLE_SOURCE_MANIFEST.md`, `FIGURE_SOURCE_DATA_MANIFEST.csv`, `FIGURE_GRIDFREE_REPRODUCIBILITY_MANIFEST.json`, and `MAIN_SUPPLEMENTARY_FIGURE_MAP.md` -- updated reproducibility and placement records.
- `V12_CHANGELOG.md`, `V12_PROVENANCE_AND_SCOPE.md`, `V12_DISPLAY_CITATION_AUDIT.md`, `V12_VALIDATION_REPORT.md`, and `SIMULATION_SUPPLEMENT_INTEGRATION_REPORT.md` -- current scope and verification records.
- `main.pdf`, `supplementary_information.pdf` -- rebuilt submission-facing outputs.

No simulation bank, GA, classifier, RFECV, Direct selector, held-out analysis, or empirical numerical result was rerun or modified for this integration.
