# TCGA cleaned-SCNV provenance audit

## Scope

This read-only audit examined the provider-organized workbook `TCGA_GBMLGG_FINAL_common_multiomics_with_clean_SCNV.xlsx` (SHA-256 `31ad68d866836cc786cc7c6421d28b7e4359c7a2b1959753618f5b469aecfafe`). The controlled workbook is not redistributed with the manuscript package.

## Findings

- The data provider confirmed in writing that the top 5,000 SCNV features were selected using unsupervised variance filtering only, based on each SCNV gene's variance across the common multi-omics participants, without using histological class labels.
- `SCNV_Common` contains 24,776 SCNV features for the same 491 participants used by `SCNV_Common_Clean`.
- `SCNV_Common_Clean` contains 5,000 features and is an exact value-preserving subset of `SCNV_Common`.
- A label-blind ranking by sample variance recovered 4,999 of the 5,000 cleaned features.
- The selected and excluded features at the cutoff had the same sample variance (`0.09732244843849162`), so the only discrepancy was an exact tie at the 5,000-feature boundary.
- No selected feature had variance below the excluded-feature ceiling, and no excluded feature had variance above the selected-feature floor.
- Histological labels were not used in this reconstruction.

## Interpretation

The provider's direct confirmation and the independent workbook reconstruction agree that the supplied cleaned sheet resulted from label-independent variance filtering. The exact tie at the cutoff explains the sole feature-level reconstruction difference and does not indicate outcome-dependent screening. The audit does not claim access to the provider's original cleaning script. The supplied cleaned workbook remains the declared empirical starting boundary, and all subsequent fitted preprocessing and feature selection were performed within the manuscript's documented outer-training partitions.

No GA, RFECV, Direct selection, model fitting, held-out evaluation, or empirical feature-selection result was rerun or changed for this audit.
