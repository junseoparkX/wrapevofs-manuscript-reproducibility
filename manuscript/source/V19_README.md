# Current public v19 snapshot

Prepared 5 November 2026. Use main.pdf (19 pages) and supplementary_information.pdf (54 pages); the current display inventory is 5 main figures, 2 main tables, 29 supplementary figures and 30 supplementary tables. CURRENT_MANUSCRIPT.json freezes the current sources/artwork. The Source Data workbook indexes all 66 displays.

The version includes completed fixed-bank CV-score reweighting and equal-center weighting sensitivity. Common-RF-seed rescoring is a separate ongoing experiment and contributes no results to this snapshot. No new manuscript edits were made during the submission-collateral refresh.

The historical local-workspace notes below describe prior stages and local ZIP/preview artifacts, which are not necessarily published in this Git tree. They do not replace the current PDFs or display map.

---

# WrapEvoFS v19 integrated revision

The supplementary-only polish is complete: use the current supplementary_information.pdf and WrapEvoFS_v19_supplement_polished_20261105_Overleaf.zip. The main manuscript and its figures are unchanged. The older six-page figure preview retains the earlier S29 design; the current supplement is authoritative for all supplementary figures. Detailed preservation, resolution, wording, and visual checks are in v19_work/supplement_polish_20261105/. To reproduce the latest supplement after the earlier integration script, run scripts/integrate_supplement_polish.py before compiling the supplement.

This is the authorized v19 revision of the preserved v18 manuscript. Start with main.pdf, supplementary_information.pdf, and v19_figure_preview.pdf. The figure preview contains the five main figures and Supplementary Figure S29. The earlier v19_idea.pdf is retained as a historical planning document.

The CV-score sensitivity was completed first, followed by figure revision and minimal manuscript integration. All v18 files, the approved Figure 1 artwork, authorship, formatting, references, and original primary signatures are preserved. The v19 manuscript now references the approved Figma Figure 1 without changing its PDF, SVG, or PNG.

The main text preserves 98.5% of original body words in sequence, excluding figure blocks, with a net increase of 416 words. Changes clarify metric definitions, connect existing controls, and add the new fixed-bank and fixed-center analyses. Repeated qualifications were reduced while the methodological scope remains in Methods and Discussion. Exact changes and preservation checks are under v19_work/revision_20261105/.

## Integrated figures

| Figure | Asset stem | Contribution |
|---|---|---|
| 1 | figures/figure_1_v19_figma | Approved workflow; artwork unchanged |
| 2 | figures/figure_2 | Legacy-zero diagnostic and 2-by-2 cross-lock control |
| 3 | figures/figure_4_strengthened | Candidate geometry, within-pool criterion, and partition sensitivity |
| 4 | figures/figure_3_strengthened | Full pipeline, paired locking controls, matched selectors, feature-count trade-offs |
| 5 | figures/figure_5_strengthened | Center conditions, pooled contrasts, equal-center sensitivity |
| S29 | figures/supp_figure_s29_cv_score_sensitivity | Paired fold-score perturbations for all four locking rules |

Each revised figure has PDF, editable SVG, PNG, source data, and alignment/font/collision QA. Figures contain graphs. Tables S29 and S30 are actual supplementary tables.

## New analyses

The frozen CV protocol uses 54 five-candidate banks, five leave-one-fold-out vectors, and all 126 multinomially weighted bootstrap count vectors. Masks, ordered fold-score arrays, evaluator seeds, and delta=0.01 remain fixed. Fenn10 completed the calculation in 0.817 seconds with no model fits or held-out access. Eight CSV outputs are byte-identical to the independently checked local calculation.

supplementary_data/cv_score_sensitivity/ contains the runnable script, protocol, aggregate inputs, all outputs, checks, and source-integrity manifest. These are fixed-bank sensitivity profiles, not participant-resampling confidence intervals. Both schemes and all four policies are reported.

supplementary_data/ampad_center_sensitivity/ contains the separate reuse of saved predictions: pooled, equal-center, and participant-count-weighted contrasts plus center-specific paired intervals. This post hoc analysis adds no fitting, retains the original pooled results, and exports aggregates only.

## Build and validation

Build main.tex and supplementary_information.tex with LuaLaTeX/latexmk; build v19_figure_preview.tex with XeLaTeX/latexmk. On restricted Windows workspaces, point TEXMFCACHE and TEXMFVAR to v19_work/texcache before LuaLaTeX compilation.

scripts/v19_revision_guard.py validate checks all 456 v18 baseline files, the original and approved Figure 1 files, and the four specifically authorized existing manuscript sources. scripts/integrate_v19_revision.py reproduces the integration from the preserved pre-revision snapshot. scripts/validate_v19_delivery.py belongs to the earlier figure-only stage, which required unchanged v19 prose; use the revision guard for the integrated stage.

The earlier candidate-deletion analysis, literature review, rejected designs, and initial proposal remain under v19_work/ as audit history.
