# Figure 1 V8 text-fix change log

Source bundle: Figure1_WrapEvoFS_scientific_v8_textfix_bundle.zip

## V14 XGBoost asset replacement

- Superseded the V13 artwork with Figure1_WrapEvoFS_scientific_v14_xgboostfix_bundle.zip.
- Replaced only figures/figure_1.svg and figures/figure_1.png with the supplied V14 files.
- Retained the V13 Boruta-RF correction and applied the supplied XGBoost connection correction.
- Preserved the Figure 1 caption, manuscript text, and every other figure.

## V13 Boruta-RF asset replacement

- Superseded the V8 Figure 1 artwork with the supplied Figure1_WrapEvoFS_scientific_v13_borutafix_bundle.zip.
- Replaced only figures/figure_1.svg and figures/figure_1.png with the supplied V13 files.
- Preserved the existing Figure 1 caption and all manuscript text because the recommended-workflow terminology is unchanged.
- No other main or supplementary figure was modified.

## Figure asset replacement

- Added the supplied editable SVG as figures/figure_1.svg without modifying its content.
- Replaced figures/figure_1.png with the supplied 170-mm-wide, 600-dpi PNG without resizing, recoloring, or redrawing it.
- The supplied preview PNG was used only for visual inspection and was not packaged as a manuscript figure.

## Main manuscript text

- Abstract: added fixed development-CV rescoring, the regret-eligible pool, Jaccard-medoid selection, deterministic tie-breaking, locked output, and one-time held-out evaluation.
- Methods 2.1: stated the full recommended sequence from five run-best candidates through fixed rescoring, empirical regret, the regret-eligible pool, eligible-pool Jaccard, deterministic medoid selection, locking, and held-out evaluation.
- Figure 1 caption: removed minimum-pool-expansion wording and described five run-best candidates, fixed locking scores, the prespecified regret tolerance, eligible-pool Jaccard, Jaccard-medoid selection, deterministic tie-breaking, and locking before held-out evaluation.
- Methods 2.3: standardized the definitions of fixed development-CV locking score, best score, and empirical development-CV regret.
- Methods 2.5: defined the regret-eligible pool explicitly and standardized eligible-pool Jaccard, mean Jaccard, Jaccard medoid, and locked-output terminology.
- Algorithm 1: aligned steps 18-23 with the regret-eligible pool and one-time held-out evaluation after locking.
- Discussion and Conclusion: aligned descriptions of the upgraded workflow with the same terminology without changing empirical claims.

## Legacy labeling retained

- The Introduction still identifies the archived top-three Jaccard-medoid lock as a legacy mode.
- ADNI Results and the Figure 2 caption now say explicitly that the top-three decision is an archived legacy analysis.
- Supplementary legacy-setting and candidate-audit table captions explicitly identify archived legacy top-three locking.
- Numerical results, equations, datasets, tables, figure numbering, retrospective/prospective distinctions, and empirical conclusions were not changed for the Figure 1 update.
