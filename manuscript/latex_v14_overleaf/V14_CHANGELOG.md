# V14 fully nested TCGA integration

V14 preserves V13 and integrates the completed two-repeat, five-fold fully nested TCGA GBM/LGG experiment. No archived empirical value, feature set, figure, or conclusion was overwritten.

## Main manuscript

- Added a sixth main figure at a native width of 170 mm.
- Positioned the top-row `a)` and `b)` labels below a deliberate blank top margin; the left-column `a)`/`c)` and right-column `b)`/`d)` axes use identical subplot geometry.
- Used one muted, color-blind-distinguishable palette throughout the new TCGA figure family: deep teal, muted ochre, and muted mauve.
- Added a Results subsection reporting strict empirical-regret feasibility, eligible-pool representativeness, cross-partition feature-identity sensitivity, compression, and repeated internal OOF results.
- Added a complete fully nested Methods subsection and qualified the Discussion boundary that archived analyses were not fully nested.
- Added TCGA to the empirical-design table, Ethics and consent, Data availability, and the abstract.
- Added primary TCGA GBM and lower-grade-glioma references.
- Added Cecilia Liang to Acknowledgements for identifying, organizing, and sharing the processed TCGA GBM/LGG multi-omics dataset.

## Supplementary Information

- Added Supplementary Figure S16 as two readable 170-mm pages containing all 30 candidate banks.
- Added Supplementary Figure S17 for conditional candidate agreement, participant-partition sensitivity, and signature composition.
- Added Supplementary Figure S18 for the six-method repeated-OOF comparator and compression audit.
- Added full TCGA protocol, provenance, duplicate-policy, stability-definition, common-seed evaluation, and claim-boundary documentation.
- Cited S16, S17, and S18 separately in the main Results at the claims each figure supports.

## Submission palette and order pass

- Preserved Figure 1 byte-for-byte and excluded it from all palette transformations.
- Harmonized Figures 2--6 and the Supplementary figure set with a muted publication palette. SVM-L1, XGBoost, and Boruta-RF are encoded consistently as teal, ochre, and plum wherever branch identity is shown.
- Removed the remaining em-dash construction from the main prose by recasting the compression claim as a conventional sentence.
- Renumbered Supplementary Figures S1--S27 and Supplementary Tables S1--S26 by first citation order in the main text.
- Removed the isolated forced-float exception and normalized table placement so the compiled Supplementary PDF prints the numbered items monotonically, including the S13 and S16 continuation pages.

## Scientific boundary

The TCGA experiment estimates repeated internal out-of-fold performance and participant-partition sensitivity in one TCGA-derived cohort. It does not establish external validity, current WHO diagnostic validity, biomarker stability, causal biology, clinical utility, equivalence, or global predictive superiority.
