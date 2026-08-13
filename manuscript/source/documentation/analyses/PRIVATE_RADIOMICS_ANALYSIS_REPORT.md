# Private radiomics analysis and integration report

## Decision and importance

Importance: **moderate; supplementary evidence that strengthens modality breadth but does not support a predictive-superiority claim**.

The analysis is valuable because it executes the updated untruncated objective and strict regret-constrained lock end to end in a high-dimensional imaging-derived feature space. It is not promoted to a main figure because the cohort is private, the two feature spaces reuse the same participants and split, automatic tumor-core regions were not manually adjudicated, and every paired held-out 95% interval includes zero.

## Transferred-output audit

- Cohort: 197 uniquely MGMT-linked participants; 117 unmethylated and 80 methylated.
- Fixed stratified split (seed 42): 137 development participants (81/56) and 60 held-out participants (36/24).
- Feature spaces: full 1,781 and label-independent perturbation-filtered 1,346.
- Run matrix: 2 feature spaces × 3 branches × 5 seeds = 30 jobs.
- All 30 jobs completed 50 generations on the GPU.
- Every required run artifact passed the recorded SHA-256 check.
- Saved masks, selected-feature counts, and stable mask hashes were mutually consistent.
- Preparation and GA provenance recorded no held-out access.

The transferred results ZIP ended after preparation and GA. It did not contain the bundle-specified `locking`, `aggregate`, or final figure directories. After reporting that mismatch, the frozen bundle aggregator was used to perform only the six development locks and the single post-lock held-out evaluation sequence. GA, Direct selection, and RFECV were not rerun. A second aggregator invocation verified all final artifact hashes and skipped held-out evaluation.

## Main findings

- All six locked signatures had selected empirical development-CV regret 0 at absolute delta 0.01.
- Five eligible pools were singletons; the full-space Boruta-RF pool contained two candidates. No tolerance-expanding fallback occurred.
- Locked signatures contained 5–50 features. Compression relative to Direct ranged from 10.0% to 81.0%, with median 75.6%.
- Mean five-seed Jaccard ranged from 0.133 to 0.920, whereas Nogueira coefficients ranged from -0.042 to 0.071. The high raw Boruta-RF Jaccard values therefore should not be interpreted as broad chance-corrected stability.
- Exact duplicate masks occurred within both Boruta-RF candidate banks under the package's retained-multiplicity policy. They did not produce a hash-dependent selected feature set.
- Full-versus-filtered locked-set Jaccard was low (0.049–0.273), demonstrating sensitivity of selected identities to the feature-definition space.
- Locked-minus-Direct held-out AUROC differences ranged from -0.007 to 0.069. All 6 intervals included zero.
- Locked-minus-RFECV intervals (6/6) and perturbation-filtered-minus-full locked intervals (3/3) also included zero. All 15 paired intervals therefore included zero.

## Interpretation boundary

The strong result is the auditable, strictly feasible hand-off and compression, not discrimination gain. The analysis does not establish external validation, clinical segmentation accuracy, biomarker stability, non-inferiority, equivalence, or predictive superiority. The perturbation-filtered space is a feature-definition sensitivity analysis on the same participants. Five seeds quantify search agreement on one development sample, not participant resampling.

## Manuscript integration

- Added one concise Results subsection and one Methods description in the main text.
- Added the private cohort as the fourth row of the main dataset table.
- Added Supplementary Methods boundaries.
- Added grid-free 170-mm Supplementary Figure S20 with bold a)–d) panel labels.
- Added Supplementary Table S21 containing locking, agreement, and held-out summaries.
- Added only non-identifying aggregate source tables and locking audits.
- Did not add a main figure or modify any archived ADNI, AMP-AD, or CGGA empirical value.

The original bundle proposed the name “Supplementary Figure S19,” but S19 is assigned to the CGGA mechanism ablation. The radiomics figure was therefore numbered S20 without changing scientific content.
