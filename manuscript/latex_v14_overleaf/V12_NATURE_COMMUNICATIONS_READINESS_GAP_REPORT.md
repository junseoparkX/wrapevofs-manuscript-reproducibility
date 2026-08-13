# Internal Nature Communications and machine-learning readiness gap report

Status definitions: **complete** = explicitly reported and supported; **partial** = some information exists but reviewer-facing completion is still needed; **not applicable** = outside the study design; **future work** = evidence was not generated and is not inferred.

| Reporting item | Status | Evidence or gap |
|---|---|---|
| Task definition and estimand | Complete | Feature compression, stochastic agreement, empirical development-CV regret, and secondary held-out differences are separated. |
| Sample sizes and feature dimensions | Complete | Main Methods/Table 3 report ADNI, AMP-AD, and CGGA boundaries. |
| Preprocessing | Partial | Supplied-matrix boundary and development-only fitting are stated; upstream assay processing was not re-audited. |
| Development/held-out separation | Complete | Figure 1 and Methods define the locked-split safeguard. |
| Leakage safeguards | Complete | Held-out access occurs only after feature-set and development procedure locking. |
| Cross-validation | Complete | RFECV/adaptive evaluation and fixed locking rescoring are distinguished. |
| Random seeds | Complete | Five-run design, evaluator seed 42, and audit export are reported. |
| Hyperparameters | Complete | Configuration and machine-readable artifacts retain the operating values; delta and lambda were not tuned here. |
| Metric definitions and rationale | Complete | Larger-is-better locking score, regret, compression, Jaccard, and held-out differences are defined. |
| Comparator/baseline methods | Complete | Direct signatures and archived branches are reported. |
| Simple baseline | Partial | Direct signatures provide a practical baseline; no new trivial predictor was added. |
| Relevant state-of-the-art comparison | Partial | Bayesian/STABL/BLiP interoperability is secondary and not a uniform benchmark. |
| Ablations | Complete | Objective flattening, target guidance, cross-lock, tolerance, and decision-path audits are included where artifacts exist. |
| Independent end-to-end updated validation | Future work | The 120-run updated comparison is development-only; archived held-out results used the original configuration. Dataset 4 was not fabricated. |
| Dataset shift/bias | Partial | AMP-AD leave-one-center-out shift is explicit; broader demographic/bias assessment remains limited. |
| Stochastic variability | Complete | Five-seed Jaccard/Nogueira summaries and their limitations are reported. |
| Hardware | Complete | GPU execution and computational provenance are in the Supplementary Information. |
| Runtime | Complete | Supplementary computational characterization reports stage/total runtime. |
| Memory | Partial | Complexity is reported; a complete empirical peak-memory benchmark is not a central result. |
| Code availability | Partial | v0.2.0 peer-review source/distributions exist locally, but private reviewer/editor access still must be granted and tested. |
| Repository access for reviewers | Partial | Private repository access must be granted through the submission workflow. |
| Install instructions and environment | Complete | Package README, Python 3.10–3.12 target, build/install tests, and configuration examples exist. |
| Reproducible example/test data | Partial | Synthetic/small test material exists; controlled participant-level inputs cannot be redistributed. |
| Restricted-data availability | Complete | Provider access routes and nonredistribution boundary are stated. |

Structural checks: 9-word title; 172-word abstract; Introduction–Results–Discussion–Methods order; separate Data/Code Availability and declarations; five main figures; three main tables; all figure legends below 350 words; full-width placement at 180 mm.
