# Proposed Supplementary Methods insertion

## Formal properties of regret-constrained medoid locking

Let the retained candidate bank be a finite nonempty multiset indexed by \(r\in\mathcal R\). Candidate \(r\) has a nonempty feature set \(F_r\), a finite larger-is-better locking score \(L_r\), and source-run provenance. All candidates use one common ordered canonical universe \(U=(u_1,\ldots,u_p)\) with unique names, and \(F_r\subseteq U\). Define the canonical mask \(z_{rj}=1\) exactly when \(u_j\in F_r\), and the stable identifier \(H_r=\mathrm{SHA256}(\mathrm{uint8}(z_r).\mathrm{tobytes}())\). Assume \(\delta\geq0\), well-defined Jaccard similarity, deterministic canonical encoding, and engineering-level hash collision resistance.

Define

\[
L_{\mathrm{best}}=\max_{r\in\mathcal R}L_r,\quad
R_r=L_{\mathrm{best}}-L_r,\quad
E_\delta=\{r\in\mathcal R:R_r\leq\delta\}.
\]

For \(|E_\delta|>1\), define

\[
\overline J_r=\frac{1}{|E_\delta|-1}
\sum_{\substack{s\in E_\delta\\s\ne r}}
\frac{|F_r\cap F_s|}{|F_r\cup F_s|}.
\]

Selection is restricted to \(E_\delta\). A nonsingleton pool is ordered by larger \(\overline J_r\), larger \(L_r\), smaller \(|F_r|\), and lexicographically smaller \(H_r\). A singleton is selected directly and has undefined mean Jaccard.

### Proposition 1 - Nonempty eligibility

For every finite nonempty candidate bank and \(\delta\geq0\), \(E_\delta\ne\varnothing\).

**Proof.** At least one candidate \(r^*\) attains \(L_{\mathrm{best}}\). Therefore \(R_{r^*}=0\leq\delta\), so \(r^*\in E_\delta\). QED.

### Proposition 2 - Strict empirical regret feasibility

The selected candidate \(\widehat r\) belongs to \(E_\delta\) and satisfies \(R_{\widehat r}\leq\delta\).

**Proof.** For a singleton pool the rule returns its sole eligible record. For a nonsingleton, medoid optimization and every score, feature-count, stable-hash, and exact-duplicate provenance path are restricted to \(E_\delta\). No path can introduce an ineligible record. Hence \(\widehat r\in E_\delta\), equivalent to the stated inequality. QED.

### Proposition 3 - Zero-tolerance behavior

For \(\delta=0\), \(E_0=\{r:L_r=L_{\mathrm{best}}\}\). A unique highest-scoring candidate is selected. If several candidates tie at \(L_{\mathrm{best}}\), the rule selects the Jaccard medoid of the complete zero-regret tied pool under the canonical tie-break.

**Proof.** Every regret is nonnegative, so \(R_r\leq0\) exactly when \(R_r=0\), equivalently \(L_r=L_{\mathrm{best}}\). The unique or tied conclusion follows. Thus \(\delta=0\) does not generally imply a singleton. QED.

### Proposition 4 - All-candidate limit

If \(\delta\geq\max_rR_r\), every candidate is eligible and the method is the full-bank Jaccard medoid under the same tie-break.

**Proof.** The condition gives \(R_r\leq\delta\) for all \(r\), so \(E_\delta=\mathcal R\). Substitution into the medoid definition gives the result. QED.

### Proposition 5 - Determinism

Given identical canonical masks, scores, source provenance, tolerance, larger-is-better orientation, and configuration, the selected feature set and complete canonical audit are deterministic.

**Proof.** Maxima, regrets, exact eligibility, Jaccard values, and arithmetic means are deterministic functions of the inputs. Canonical masks and SHA-256 digests are deterministic byte transformations. The tie key totally orders distinct masks under the collision-resistance assumption. Exact duplicate records have the same scientific output and a deterministic provenance label after feature-set selection. Candidate rows, pairwise rows, and configuration fields are canonically serialized. QED.

SHA-256 is a stable ordering device, not a probabilistic scientific score. Collision resistance is an engineering assumption and not the source of Proposition 2; feasibility follows from restricting selection to \(E_\delta\).

### Proposition 6 - Candidate-order permutation invariance

Permuting input records while preserving content, source provenance, and multiplicity does not alter the selected feature set or canonical audit.

**Proof.** A record permutation preserves the score multiset, \(L_{\mathrm{best}}\), every regret, and \(E_\delta\). Every mean Jaccard is a sum over the same eligible multiset. The remaining tie key is content-derived and contains no row position. Exact duplicate records yield the same feature set, provenance normalization is input-order independent, and canonical serialization restores the same audit order. QED.

Candidate content determines scientific selection; source-run provenance is retained for traceability; input-row order is discarded. Duplicate masks are retained as multiple votes, so multiplicity is part of the candidate-bank multiset. Adding or removing a duplicate can change the medoid, while merely permuting existing duplicates cannot.

### Proposition 7 - Distinction among rules

The highest-score rule guarantees zero empirical regret but does not optimize representativeness. The unrestricted full-bank medoid optimizes mean Jaccard but can incur regret as large as \(\max_rR_r\). The legacy top-\(k\) medoid uses a rank cutoff; because rank is not a metric-scale distance, it imposes no explicit \(\delta\)-regret constraint. Regret-constrained locking first enforces \(R_r\leq\delta\), then optimizes eligible-pool representativeness. None of these candidate-bank statements proves globally optimal feature selection.

## Detailed complexity

Let \(R\) be the retained-candidate count, \(E\) the eligible count, \(p\) the canonical-universe size, \(s\) the average selected-set size, and \(w\) the packed machine-word width.

1. Finding \(L_{\mathrm{best}}\) and all regrets costs \(O(R)\) time and \(O(R)\) retained memory, or \(O(1)\) streaming memory.
2. Forming \(E_\delta\) costs \(O(R)\) time and \(O(E)\) memory.
3. Dense canonical mask construction and the authoritative SHA-256 hash cost \(O(Rp)\) time. Retaining all masks costs \(O(Rp)\) memory; streaming requires \(O(p)\) scratch and \(O(R)\) digests. Deriving a sorted union when no universe is supplied adds \(O(Rs+p\log p)\).
4. A dense bit-vector Jaccard costs \(O(p)\) time, so all eligible pairs cost \(O(E^2p)\).
5. Sparse hash-set Jaccard costs expected \(O(s)\) per typical pair, or sorted-index merging costs \(O(|F_r|+|F_s|)\), giving expected \(O(E^2s)\) overall.
6. Packed-bit Jaccard costs \(O(\lceil p/w\rceil)\) word operations per pair and \(O(E\lceil p/w\rceil)\) mask storage.
7. Retaining the ordered \(E\times E\) matrix costs \(O(E^2c_J)\) time and \(O(E^2)\) similarity memory, where \(c_J\) is the representation-specific pair cost.
8. Streaming unordered pairs into \(E\) running sums has the same \(O(E^2c_J)\) time but only \(O(E)\) accumulator memory beyond masks. A complete pairwise audit must then be streamed to storage or omitted.
9. Tie-breaking costs \(O(E)\) with a best-key scan or \(O(E\log E)\) with sorting after hashes exist. Canonical audit-row ordering costs \(O(R\log R)\).
10. The current dense-mask plus complete-pairwise audit has \(O(Rp+E^2)\) serialization time, output size, and in-memory DataFrame storage; streaming can reduce additional working memory.

The current package therefore has straightforward expected locking cost \(O(Rp+E^2s+R\log R)\) time and \(O(Rp+E^2)\) memory. With \(R=5\), there are at most 10 distinct off-diagonal comparisons or 25 ordered matrix entries including the diagonal, which is small relative to candidate rescoring. This five-run design does not demonstrate scalability to large candidate banks.

## Duplicate-mask policy

Independent runs that return the same mask remain distinct candidate records and contribute separately to every eligible-pool mean. Audit columns record the stable mask hash and duplicate multiplicity. If exact duplicate records share the winning scientific key, every such record is marked as carrying the selected feature set, while one lowest source run ID is stored only as a provenance representative after feature-set selection. No run ID or input-row position chooses among distinct scientific masks.

## Implementation correspondence

| Property | Package mechanism | Test evidence |
|---|---|---|
| Nonempty bank and feature sets | Candidate validation and empty-pool guard | `test_empty_candidate_bank_is_rejected`; `test_empty_feature_masks_are_rejected` |
| Finite larger-is-better scores | Finite-score validation and explicit orientation | `test_nonfinite_scores_are_rejected`; `test_lower_is_better_orientation_is_rejected` |
| Strict feasibility | Exact threshold comparison and postcondition | `test_absolute_pool_does_not_apply_hidden_epsilon_relaxation`; generated-bank feasibility property test |
| Zero and all-candidate limits | Direct construction of \(E_\delta\) | unique/tied zero-tolerance and all-eligible tests |
| Canonical mask and hash | Common-universe mask plus authoritative SHA-256 helper | feature-order and cross-process tests |
| Duplicate multiplicity | No deduplication; multiplicity audit | duplicate and identical-mask tests |
| Permutation invariance | Content-derived tie key and canonical serialization | exhaustive three-record permutations and generated-bank permutations |
| Deterministic serialization | Canonical rows and key-sorted metadata | save/reload and repeated-audit tests |

## Claim boundary

Empirical development-CV regret is an observed adaptive internal score gap. It is distinct from expected predictive risk, generalization error, and statistical uncertainty. The propositions guarantee only the configured empirical gap and deterministic representative selection from the supplied bank. They do not establish predictive superiority, unbiased generalization, external validity, participant-resampling or biomarker stability, or clinical utility.
