# Private radiomics upstream provenance mapping

## Source reviewed

- Title: `End-to-End DICOM-to-Radiomics Dataset Report`
- Source PDF SHA-256: `46e141be9c5e711a285d0b4aded3ff2d73a8f92c3c0c504aaa6c03c7fe7040f3`
- Scope: non-identifying technical handoff from the PHI-bearing DICOM source to the paired 1,781- and 1,346-feature supervised matrices.

The report was used as upstream construction provenance. It was not treated as an independent empirical experiment or a peer-reviewed literature reference.

## Manuscript correspondence

- The main Methods now identify the DICOM-to-NIfTI converter, automatic segmentation software, software versions, label-free ordering, cohort accounting, and automatic-region limitation.
- Supplementary Methods record the frozen PyRadiomics preprocessing, image transforms, feature classes, hard-failure/review-flag distinction, and submission-package boundary.
- Supplementary Table S27 consolidates the construction and validation settings without redistributing participant-level imaging, masks, linkage material, or QC records.
- Primary literature citations were added for Raidionics and DICOM-to-NIfTI conversion. Existing citations for PyRadiomics, IBSI definitions, and perturbation robustness were retained.

## Decision on additional analyses and figures

No new performance analysis or figure was added. Supplementary Figure S19a already shows the cohort reduction and paired feature spaces, and Supplementary Figure S19b--d plus Table S18 already report the downstream locking, agreement, and held-out sensitivity results. A second cohort-flow or pipeline figure would duplicate existing displays.

Participant-level acquisition and mask-QC covariates were not included in the manuscript analysis bundle, so scanner-, spacing-, or review-flag-stratified outcome analysis cannot be recomputed responsibly from the supplied submission artifacts. This remains a stated limitation rather than being reconstructed from aggregate counts.
