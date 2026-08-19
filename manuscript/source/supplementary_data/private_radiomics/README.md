# VGH brain-tumour radiomics aggregate source data

This directory contains only non-identifying aggregate artifacts supporting Supplementary Figure S20 and Supplementary Table S21.

Included:

- verified run-level GA summaries for 30 completed jobs;
- six development-only locking audits and eligible-pool Jaccard tables;
- feature-count, seed-agreement, feature-frequency, held-out metric, and paired-effect summaries;
- a derived six-condition summary and figure manifest.

Excluded:

- participant-level feature matrices and identifiers;
- DICOM images, masks, segmentations, and patient-level QC records;
- prepared joblib inputs and GA checkpoints;
- participant-level held-out predictions.

The full 1,781-feature and perturbation-filtered 1,346-feature analyses use the same 197 participants, labels, and fixed split. Their comparison is feature-definition sensitivity, not external validation. Five-seed agreement is not participant-resampling or biomarker stability. Automatic tumor-core regions were not manually adjudicated.

Rebuild the figure from the manuscript source root with:

```sh
python scripts/build_radiomics_s20.py
```

The build script reads only files in this directory and records SHA-256 values in `radiomics_figure_manifest.json`.
