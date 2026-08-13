# Regret-constrained medoid locking: definitions, guarantees, and proofs

## Scope and assumptions

Let the retained candidate bank be a finite nonempty multiset of records indexed by (r \in \mathcal R), with (R=|\mathcal R|\). Record (r) contains a nonempty feature set (F_r), a finite locking score (L_r\), and source-run provenance. The scientific candidate content is the pair ((F_r,L_r)); source-run provenance identifies where that content arose, while input-row position has no scientific role.

The following assumptions are required.

1. All candidates use one common ordered canonical universe (U=(u_1,\ldots,u_p)) with unique feature names, and every (F_r\subseteq U).
2. Each (F_r) is encoded as the canonical mask (z_r\in\{0,1\}^p), where (z_{rj}=1\) exactly when (u_j\in F_r). Candidate feature-list order therefore cannot change the mask.
3. The stable identifier is (H_r=\operatorname{SHA256}(\operatorname{uint8}(z_r).\operatorname{tobytes}())), compared lexicographically. SHA-256 collision resistance is an engineering assumption. The implementation also rejects an observed collision between unequal masks.
4. Locking scores are finite and oriented so that larger values are better. The tolerance satisfies \(\delta\geq0\).
5. Jaccard similarity is (J(F_r,F_s)=|F_r\cap F_s|/|F_r\cup F_s|). Nonempty sets make the denominator positive.
6. Duplicate masks from distinct retained runs are not deduplicated: each record remains one voting candidate, so its multiplicity is part of the candidate bank. Provenance is preserved separately from scientific selection.

Define

\[
L_{\mathrm{best}}=\max_{r\in\mathcal R}L_r,
\qquad
R_r=L_{\mathrm{best}}-L_r,
\qquad
E_\delta=\{r\in\mathcal R:R_r\leq\delta\}.
\]

(R_r) is empirical development-CV regret: an observed score gap inside the configured development-CV procedure. It is not expected predictive risk, generalization error, or a statistical uncertainty interval.

For (E=|E_\delta|>1), define

\[
\overline J_r=
\frac{1}{E-1}
\sum_{\substack{s\in E_\delta\\s\ne r}}
J(F_r,F_s),
\qquad r\in E_\delta.
\]

The regret-constrained Jaccard medoid is selected only from (E_\delta). For a nonsingleton pool, candidates are ordered by: (i) larger \(\overline J_r\), (ii) larger \(L_r\), (iii) smaller \(|F_r|\), and (iv) lexicographically smaller \(H_r\). For a singleton pool, the sole candidate is selected and mean Jaccard is undefined. If records remain tied after the hash because they are exact duplicate masks with identical preceding criteria, they represent the same scientific feature set. The package chooses the lowest source run ID only as a deterministic provenance label after the feature set has been selected; run ID is not a scientific tie-break.

## Proposition 1 - Nonempty eligibility

For every finite nonempty candidate bank and every \(\delta\geq0\), (E_\delta\ne\varnothing\).

**Proof.** Finiteness and nonemptiness imply that at least one candidate (r^*\) attains (L_{\mathrm{best}}). Its regret is (R_{r^*}=L_{\mathrm{best}}-L_{r^*}=0\leq\delta\), so (r^*\in E_\delta\). QED.

## Proposition 2 - Strict empirical regret feasibility

The output of regret-constrained medoid locking belongs to (E_\delta) and satisfies (R_{\widehat r}\leq\delta\).

**Proof.** If (E_\delta) is a singleton, the rule selects its sole member, which is eligible by definition. If it is nonsingleton, the medoid optimization and every deterministic tie-breaking stage are restricted to candidates in (E_\delta); none of the mean-Jaccard, score, feature-count, or stable-hash comparisons can introduce a candidate from outside that set. Exact duplicate records remaining after the hash carry the same selected feature set, and the provenance-only record choice is also made within the eligible tied records. Thus every path returns \(\widehat r\in E_\delta\), which is equivalent to (R_{\widehat r}\leq\delta\). QED.

## Proposition 3 - Zero-tolerance behavior

For \(\delta=0\), (E_0=\{r:L_r=L_{\mathrm{best}}\}\). A unique highest-scoring candidate is selected. If several candidates tie at (L_{\mathrm{best}}\), the rule selects the Jaccard medoid of the complete zero-regret tied pool under the canonical deterministic tie-break.

**Proof.** Since (L_{\mathrm{best}}\geq L_r\), every regret is nonnegative. Therefore (R_r\leq0\) holds exactly when (R_r=0\), equivalently (L_r=L_{\mathrm{best}}\). A unique maximizer makes (E_0) a singleton. Multiple maximizers make (E_0) nonsingleton unless they are represented by only one record, and the nonsingleton rule applies. Hence zero tolerance does not generally imply a singleton pool. QED.

## Proposition 4 - All-candidate limit

If \(\delta\geq\max_{r\in\mathcal R}R_r\), every candidate is eligible and the rule is the Jaccard medoid of the full candidate bank under the same deterministic tie-break.

**Proof.** The stated inequality gives (R_r\leq\delta\) for every (r\), so (E_\delta=\mathcal R\). Substitution into the medoid definition yields the full-bank Jaccard medoid. QED.

## Proposition 5 - Determinism

Given identical candidate records (canonical masks, scores, and source provenance), tolerance, larger-is-better orientation, and configuration, the selected feature set and complete canonical audit are deterministic.

**Proof.** The maximum, regret values, exact eligibility comparisons, Jaccard values, and arithmetic means are deterministic functions of the inputs. Canonical masks and their SHA-256 digests are deterministic byte transformations. The ordered tie key is total over distinct scientific masks under the collision-resistance assumption. Exact duplicate records have the same scientific output; their provenance label is normalized deterministically after selection. Candidate and pairwise audit rows are serialized in canonical hash/provenance order, and configuration JSON is key-sorted. Therefore repeated execution produces the same selected feature set and audit. QED.

The cryptographic digest supplies stable ordering only. It is not random evidence, a predictive score, or a measure of biological importance. Collision resistance supports engineering uniqueness but does not create the regret guarantee; Proposition 2 follows from restricting selection to (E_\delta\).

## Proposition 6 - Candidate-order permutation invariance

Permuting the input-row order of candidate records, while preserving record content and source-run provenance, does not alter the selected feature set or canonical audit.

**Proof.** A permutation changes neither the multiset of candidate contents nor its multiplicities. Consequently (L_{\mathrm{best}}\), every regret, and (E_\delta\) are unchanged. Each mean Jaccard is a sum over the same eligible multiset, so it is invariant to summation order. The remaining tie key depends only on score, set cardinality, and canonical mask hash, not input-row position. Exact duplicate records yield the same feature set, and their provenance-only normalization is also independent of input order. Canonical serialization restores the same audit row order. QED.

Candidate content, source-run provenance, and input-row position are distinct: content determines scientific selection; provenance is retained for traceability; row position is discarded. Because duplicate masks are retained, adding or removing a duplicate changes the candidate-bank multiset and may change the medoid. Merely reordering existing duplicates cannot.

## Proposition 7 - Legacy and upgraded rules are distinct

1. **Highest-score rule.** Selecting an element of \(\arg\max_rL_r\) guarantees zero empirical regret. It does not optimize mean Jaccard representativeness unless the chosen maximizer happens also to be a medoid.
2. **Unrestricted all-candidate medoid.** This rule maximizes representativeness within the full bank. With arbitrary finite scores, its selected regret can be as large as \(\max_rR_r\); therefore it has no nontrivial prespecified regret guarantee.
3. **Legacy top-k medoid.** Rank first restricts the pool. Rank is not a metric-scale distance, and the score gap between adjacent ranks can be arbitrarily small or large. Thus a top-k cutoff is not an explicit \(\delta\)-regret constraint.
4. **Regret-constrained medoid.** This rule first enforces (R_r\leq\delta\), then maximizes representativeness only among feasible candidates. It is a lexicographic feasibility-then-representativeness rule.

None of these statements establishes globally optimal feature selection. The candidate bank is already the output of a stochastic and adaptive development-data procedure.

## Claim boundary

The propositions prove only the configured empirical development-CV score-gap constraint and deterministic representative selection from the supplied candidate bank. They do not prove predictive superiority, unbiased generalization performance, external validity, participant-resampling stability, biomarker stability, clinical utility, or calibrated statistical uncertainty.
