# V13 methods-specification and author-affiliation revision

V13 refines the V12 Methods and corrects the title-page affiliation metadata. No empirical analysis, feature set, selected run, lock, figure, result table, uncertainty interval, or scientific conclusion was changed.

## Author affiliations

- Identified Junseo Park with affiliation 1: Department of Computer Science, University of British Columbia, Vancouver, BC, Canada.
- Identified Leonard J. Foster and Huan Zhong with affiliation 2: Department of Biochemistry & Molecular Biology, Michael Smith Laboratories, Life Sciences Institute, University of British Columbia, Vancouver, BC, Canada.
- Applied the same affiliation numbering to the main and Supplementary title pages while preserving author order, ORCID identifiers, email addresses, CRediT roles, and Huan Zhong's corresponding-author designation.

## Main Methods

- Replaced the compact RFECV target notation with an explicitly parenthesized smallest-argmax definition.
- Defined the fixed fold-averaged locking score and distinguished the search metric from the common locking metric.
- Defined the fold-averaged GA base score with its stochastic evaluator seed.
- Replaced dense fitted-estimator subscripts and superscripts in the two fold-average equations with simple per-fold score symbols; the exact evaluator, feature-set, fold, and seed definitions remain stated in the adjacent prose.
- Extended the shifted-weight definition to nonfinite objectives and added normalized parent-sampling probabilities plus the uniform fallback.
- Expressed regret-constrained medoid selection as a plain four-step ordering followed by the short identity \(F^{\mathrm{lock}}=F_{\widehat r}\), preserving the same deterministic selection rule.

## Supplementary Methods

- Expanded Supplementary Algorithm S1 from workflow-level pseudocode to executable operator-level pseudocode.
- Added the exact initial-mask construction, 50-by-50-by-5 budget, two-elite replacement, with-replacement parent sampling, one-point crossover, per-bit mutation, empty-mask repair, RF evaluation schedule, and fixed locking rescoring.
- Added Supplementary Table S26 consolidating Direct-selector, RFECV, GA, random-forest, objective-mode, locking, seed, audit, and held-out-boundary settings.

## Packaging

- Added V13-specific word-count and deterministic submission-archive scripts.
- Retained the V12 reports and changelogs as immutable revision history.
