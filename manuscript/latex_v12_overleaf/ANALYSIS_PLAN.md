# V11 existing-artifact analysis plan

## Fixed constraints

- Preserve V10 and freeze Figure 1.
- Use the package-authoritative stable mask hash without redesign.
- Use development-only saved masks, scores, summaries, and audits.
- Do not access held-out inputs or rerun feature selection or model analysis.
- Mark incomplete cells unavailable rather than inferring them.

## Reproducible execution order

1. `scripts/validate_figure1_freeze.py`
2. `scripts/build_v11_existing_artifact_analyses.py`
3. `scripts/build_v11_revision_tables.py`
4. `scripts/build_v11_revision_figures.py`
5. `supplementary_data/recommended_mode_120_run/scripts/build_ampad_four_center_objective_sensitivity_s18.py`
6. `scripts/build_v11_figure3_terminology.py`
7. `scripts/prepare_170mm_figure_assets.py`
8. `scripts/build_figure_style_manifest.py`
9. LuaLaTeX/BibTeX compilation, log audit, and 49-page raster QA.

## Principal inputs

- `supplementary_data/Table_S16_AMPAD_FourCenter_Objective_Sensitivity.csv`
- `supplementary_data/recommended_mode_120_run/authoritative_lock/candidate_locking_audit.csv`
- `supplementary_data/recommended_mode_120_run/authoritative_lock/LOCK_FREEZE_MANIFEST.json`
- completed original candidate banks under `_codex_tmp/ampad_20260731_review/results`
- completed updated non-Rush candidate banks under `analysis/remaining90_completed_20260806/results`
- strict Rush summary audits under `outputs/AMPAD_Rush_6Condition_Strict_Reaggregation_20260803`
- root `locking_rule_sensitivity.csv`, corrected only for singleton presentation.

## Outputs

Machine-readable outputs are under `revision_outputs/`; corrected S16 source is under `supplementary_data/`; native Figure 5 and S16 are in SVG/PDF/PNG; Tables S18-S20 are generated as `tables/table_40.tex` through `table_42.tex`.

The plan excludes new data and simulation. Phase B work begins only after explicit approval of an endpoint, split, evaluation rule, and compute budget.
