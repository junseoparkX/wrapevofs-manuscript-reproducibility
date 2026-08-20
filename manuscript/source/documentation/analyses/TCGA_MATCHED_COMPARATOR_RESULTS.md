# TCGA matched selector-layer results

## Decision

The checksum-frozen comparator extension is informative enough for the main manuscript because it answers a reviewer-relevant question under the completed fully nested design: whether the compact WrapEvoFS signatures occupy a useful performance and compression trade-off relative to conventional selector layers and equally sized random candidate banks. The result is branch dependent and is reported as a trade-off.

## Integrity boundary

- Frozen protocol SHA-256: `c9c808d591918779961a7f236f6beb588c640e1b8932a8b030428f3d988a4ff1`.
- Verified conditions: 30 of 30; validation errors: 0.
- The exact two repeated five-fold outer-CV partitions, 491 participants, post-Direct outer-training universes, and common-seed WrapEvoFS predictions were reused.
- Direct, RFECV, GA search, candidate rescoring, and locking were not rerun or changed.
- Comparator feature sets and hashes were serialized before outer-test values or outcomes were opened.
- Elastic Net and stability selection were nested within each outer-training partition. Five random banks per condition matched candidate-bank size, mask size, and locking-evaluation budget, not total GA compute.
- Because the parent TCGA outcomes had already been analyzed, this is a checksum-frozen retrospective selector-layer sensitivity, not prospective validation or a standalone state-of-the-art pipeline benchmark.

## Primary repeated-OOF macro one-vs-rest AUROC

| Branch | WrapEvoFS | RFECV-only | Elastic Net native | Elastic Net matched | Stability native | Stability matched |
|---|---:|---:|---:|---:|---:|---:|
| SVM-L1 | 0.8265 | 0.8373 | 0.8411 | 0.8089 | 0.8401 | 0.8004 |
| XGBoost | 0.8270 | 0.8258 | 0.8341 | 0.8287 | 0.8263 | 0.8285 |
| Boruta-RF | 0.8277 | 0.8223 | 0.8385 | 0.8386 | 0.8343 | 0.8405 |

Mean WrapEvoFS feature counts were 14.6, 20.0, and 18.0 in the SVM-L1, XGBoost, and Boruta-RF branches. Native Elastic-Net supports contained 73.7, 77.0, and 60.4 features; native stability supports contained 58.0, 38.2, and 30.6.

## Matched-cardinality paired effects

WrapEvoFS minus matched Elastic Net was:

- SVM-L1: +0.0176, 95% CI +0.0008 to +0.0341;
- XGBoost: -0.0017, 95% CI -0.0146 to +0.0111;
- Boruta-RF: -0.0109, 95% CI -0.0236 to +0.0024.

WrapEvoFS minus matched stability selection was:

- SVM-L1: +0.0261, 95% CI +0.0082 to +0.0434;
- XGBoost: -0.0015, 95% CI -0.0136 to +0.0105;
- Boruta-RF: -0.0128, 95% CI -0.0260 to +0.0012.

Thus, the compact WrapEvoFS signature had higher primary-metric estimates in the SVM-L1 branch, similar estimates in the XGBoost branch, and lower Boruta-RF point estimates whose matched-selector intervals included zero. CI overlap is not interpreted as equivalence.

## Random-bank sensitivity

Mean WrapEvoFS-minus-random-bank AUROC differences across five prespecified banks were -0.0018, +0.0102, and -0.0043 for SVM-L1, XGBoost, and Boruta-RF. The full replicate ranges were -0.0076 to +0.0040, +0.0015 to +0.0196, and -0.0109 to -0.0005. XGBoost WrapEvoFS exceeded all five random-bank point estimates; the other branches did not. This does not establish that GA candidates are uniformly better than random candidates.

## Manuscript interpretation

The supported conclusion is that no tested selector dominated every branch on both macro one-vs-rest AUROC and feature count. WrapEvoFS contributes a compact, deterministic, regret-feasible representative hand-off from a stochastic candidate bank. The experiment does not establish external validity, predictive equivalence, universal GA benefit, compute superiority, biomarker stability, causal biology, or global feature-selection optimality.

## Source files

Exact metrics, paired intervals, random-bank summaries, selected counts, fit counts, and checksum manifests are under `supplementary_data/tcga_matched_comparator/`. The main benchmark uses Figure 3; secondary AUPRC, balanced-accuracy, and count results use Supplementary Figure S8 and Supplementary Table S6.
