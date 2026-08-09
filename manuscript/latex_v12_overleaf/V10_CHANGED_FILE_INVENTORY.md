# V10 changed-file inventory

Comparison basis: authoritative `manuscript/latex_v9_overleaf` versus final `manuscript/latex_v10_overleaf`. Transient LaTeX files (`main.aux`, `main.bbl`, `main.blg`, `main.fdb_latexmk`, `main.fls`, `main.log`, and `main.out`) are excluded. Temporary render and cache directories were removed after validation. No V9 file was removed or edited.

## Modified relative to V9

- `manuscript/latex_v10_overleaf/main.tex`
- `manuscript/latex_v10_overleaf/sections/main_text.tex`
- `manuscript/latex_v10_overleaf/sections/supplementary.tex`
- `manuscript/latex_v10_overleaf/tables/table_01.tex`
- `manuscript/latex_v10_overleaf/tables/table_03.tex`
- `manuscript/latex_v10_overleaf/tables/table_04.tex`
- `manuscript/latex_v10_overleaf/tables/table_06.tex`
- `manuscript/latex_v10_overleaf/tables/table_07.tex`
- `manuscript/latex_v10_overleaf/tables/table_21.tex`
- `manuscript/latex_v10_overleaf/tables/table_38.tex`
- `manuscript/latex_v10_overleaf/tables/table_39.tex`
- `manuscript/latex_v10_overleaf/figures/figure_s18.svg`
- `manuscript/latex_v10_overleaf/figures/figure_s18.pdf`
- `manuscript/latex_v10_overleaf/figures/figure_s18.png`
- `manuscript/latex_v10_overleaf/figures/figure_2.png`
- `manuscript/latex_v10_overleaf/figures/figure_3.png`
- `manuscript/latex_v10_overleaf/figures/figure_4.png`
- `manuscript/latex_v10_overleaf/figures/figure_5.png`
- `manuscript/latex_v10_overleaf/figures/figure_s1.png` through `figure_s17.png`
- `manuscript/latex_v10_overleaf/README.md`
- `manuscript/latex_v10_overleaf/main.pdf`

## Added V10 presentation and documentation files

- `manuscript/latex_v10_overleaf/supplementary_data/Table_S16_AMPAD_FourCenter_Objective_Sensitivity.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/Table_S16_AMPAD_FourCenter_Objective_Sensitivity.md`
- `manuscript/latex_v10_overleaf/supplementary_data/S18_S16_FourCenter_provenance.json`
- `manuscript/latex_v10_overleaf/V10_AMPAD_FOUR_CENTER_SENSITIVITY_CHANGELOG.md`
- `manuscript/latex_v10_overleaf/V10_VALIDATION_REPORT.md`
- `manuscript/latex_v10_overleaf/V10_CHANGED_FILE_INVENTORY.md`
- `manuscript/latex_v10_overleaf/V10_TERMINOLOGY_AND_STORY_REVISION_REPORT.md`
- `manuscript/latex_v10_overleaf/FIGURE_GRID_REMOVAL_REPORT.md`
- `manuscript/latex_v10_overleaf/FIGURE_GRIDFREE_REPRODUCIBILITY_MANIFEST.json`

## Added compact 120-run audit bundle

- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/README.md`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/ANALYSIS_REPORT.md`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/VALIDATION_REPORT.md`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/validation/validation_summary.json`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/validation/job_inventory.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/validation/condition_inventory.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/validation/issues.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/authoritative_lock/LOCK_FREEZE_MANIFEST.json`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/authoritative_lock/candidate_locking_audit.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/authoritative_lock/eligible_pairwise_jaccard.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/authoritative_lock/recommended_18_condition_inventory.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/authoritative_lock/bundle_vs_authoritative_selection_comparison.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/authoritative_lock/stable_identifier_verification.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/authoritative_lock/empirical_permutation_invariance.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/summary/analysis_summary.json`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/summary/remaining90_run_level_summary.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/summary/remaining90_condition_level_summary.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/summary/remaining90_legacy_vs_recommended.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/summary/remaining90_center_summary.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/summary/remaining90_branch_summary.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/summary/all_four_centers_small_reference_comparison.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/summary/proposed_table_s16_24_conditions.csv`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/scripts/apply_authoritative_stable_hash_lock.py`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/scripts/summarize_remaining90.py`
- `manuscript/latex_v10_overleaf/supplementary_data/recommended_mode_120_run/scripts/build_ampad_four_center_objective_sensitivity_s18.py`

## Project-level presentation builder

- `analysis/build_ampad_four_center_objective_sensitivity_s18.py`
- `analysis/rebuild_v10_gridfree_figures.py`
- The two synchronized S18 builders were updated to expose the heatmap axes and color scales and to prevent panel-c labels and the legend from obscuring one another or the plotted bars.
- Reader-facing terminology and Results ordering were revised to distinguish the original configuration, updated configuration, and legacy-compatible software modes without renaming frozen source fields or API identifiers.
- Figure presentation settings in the existing source builders under `analysis/` and `outputs/AMPAD_Figure3_publication_assets_20260731/scripts/` were updated to disable plot grids and omit caption-duplicated annotations.
- `manuscript/WrapEvoFS_LaTeX_V10_Overleaf.zip` (clean Overleaf source archive; no transient build files)

## Removed

- None.
