# TCGA selector-layer comparator extension

## Purpose

This checksum-frozen retrospective extension tests whether the fully nested
WrapEvoFS result can be interpreted as more than a comparison with RFECV alone.
It reuses the exact 10 existing outer partitions and the 30 verified post-Direct
outer-training universes. It does not rerun or alter Direct screening, RFECV,
GA search, candidate rescoring, or the regret-constrained locks.

## Prespecified comparisons

- Multinomial Elastic Net selected by five-fold inner CV within each frozen
  post-Direct universe. Native nonzero support is primary; a top-ranked set with
  the same cardinality as the locked WrapEvoFS signature is a sensitivity analysis.
- Subsampling stability selection from 50 class-stratified half-samples using
  the chosen Elastic-Net configuration. Frequency at least 0.80 is primary; a
  cardinality-matched ranking is a sensitivity analysis.
- Five independent random five-mask banks per outer condition, with every mask
  matched to the locked WrapEvoFS cardinality and sampled from the same Direct
  universe. Each bank is evaluated and locked with the same five-fold evaluator,
  absolute tolerance 0.01, and canonical tie-breaking rule.

Every selected feature list and content hash is written before outer-test features
or labels are opened. All signatures use the same final 500-tree random forest and
condition-specific common seed. Macro one-vs-rest AUROC is primary; macro AUPRC,
balanced accuracy, macro F1, and accuracy are secondary. Paired intervals use
2,000 participant-clustered class-stratified resamples retaining both repeat
predictions for every sampled participant.

## Frozen identity

- Protocol SHA-256:
  `c9c808d591918779961a7f236f6beb588c640e1b8932a8b030428f3d988a4ff1`
- Existing outer-prediction SHA-256:
  `55db0cd513fb9d0e5ff3dbb5d1e6aaf5fb60f5788b9cca3d051b6944d35ccc47`
- Source matrix SHA-256:
  `cb51b475db9a942353cb838784bc9e57e95584fdd0720b0fcbd66ffc18b3bb56`

The executable protocol and all checkpoints are stored in
`analysis/tcga_matched_comparator_20260813/`.

## Interpretation boundary

Elastic Net and stability selection are selector-layer comparisons conditional
on the same post-Direct universe, not independent full-matrix pipelines. The
random control matches candidate-bank size and locking-evaluation budget, not
the full computational cost of GA search. Results therefore quantify incremental
selector behavior under the frozen nested design and cannot establish standalone
state-of-the-art superiority, external validity, biomarker stability, or compute
equivalence.
