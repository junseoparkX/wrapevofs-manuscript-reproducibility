# Computational complexity of regret-constrained locking

## Notation and computational model

- (R): number of retained candidate records.
- (E=|E_\delta|\): number of regret-eligible records, with (1\leq E\leq R\).
- (p): size of the common ordered canonical candidate universe.
- (s): average selected-set size.
- (w): machine-word width for packed masks, normally 64 bits.

The bounds below concern locking after candidate scores already exist. They exclude RFECV, GA search, candidate rescoring, and held-out evaluation.

## Straightforward bounds

| Operation | Time | Additional memory | Notes |
|---|---:|---:|---|
| 1. Find (L_{\mathrm{best}}) and calculate all regrets | (O(R)) | (O(R)) when retained; (O(1)) if streamed | One maximum pass and one subtraction per record. |
| 2. Form (E_\delta) | (O(R)) | (O(E)) | Exact comparison with the configured threshold. |
| 3. Construct dense canonical masks and stable hashes | (O(Rp)) | (O(Rp)) if all masks are retained; (O(p)) scratch plus (O(R)) digests if streamed | The authoritative digest consumes every canonical `uint8` mask byte. With no supplied universe, deriving and sorting the union additionally costs (O(Rs+p\log p)). |
| 4. One dense bit-vector Jaccard calculation | (O(p)) | (O(p)) if temporary Boolean vectors are materialized; (O(1)) counters with a direct scan | Full eligible computation is (O(E^2p)). |
| 5. One sparse-set Jaccard calculation | Expected (O(s)) with hash sets, or (O(|F_r|+|F_s|)) with sorted-index merge | (O(s)) if sets must be built; (O(1)) merge scratch after storage | Full eligible computation is expected (O(E^2s)). Adversarial hash behavior is not used as a scientific assumption. |
| 6. One packed-bit Jaccard calculation | (O(\lceil p/w\rceil)) word operations | (O(1)) counters after packed storage | Uses wordwise AND/OR plus population count; full computation is (O(E^2\lceil p/w\rceil)). Packed mask storage is (O(E\lceil p/w\rceil)). |
| 7. Compute and store the complete ordered (E\times E) matrix | (O(E^2c_J)) | (O(E^2)) Jaccard values plus mask storage | (c_J\) is (p), expected (s), or (\lceil p/w\rceil) for dense, sparse, or packed representations. Computing only the upper triangle changes constants, not order. |
| 8. Stream mean Jaccard without retaining the matrix | (O(E^2c_J)) | (O(E)) accumulators plus mask storage | Visit each unordered pair once and add its value to both candidates. A complete pairwise audit can be streamed to disk, but cannot be recreated later from only the means. |
| 9. Deterministic tie-breaking | (O(E)) with a single best-key scan; (O(E\log E)) with a full sort | (O(1)) for scan; (O(E)) for sort | Stable hashes are assumed precomputed. Canonical candidate-row ordering adds (O(R\log R)). |
| 10. Audit serialization | (O(Rp+E^2)) for the current dense-mask plus pairwise schema | (O(Rp+E^2)) when DataFrames are retained; (O(1)) to (O(E)) beyond stored inputs when streamed | Candidate rows include canonical masks/features; pairwise rows dominate when (E) is large. Output size has the same order. |

Here (E^2) denotes the ordered matrix used by the package, including the diagonal. The number of distinct unordered off-diagonal comparisons is (E(E-1)/2).

## Overall implementations

The current package constructs and hashes dense masks for all (R) candidates, calculates Jaccard with sparse Python sets for eligible pairs, retains an ordered pairwise table, and canonically sorts audit rows. Its straightforward locking bound is

\[
O(Rp + E^2s + R\log R)
\]

time and

\[
O(Rp + E^2)
\]

memory, including the stored canonical mask strings and complete pairwise audit. Python object overhead is substantial relative to the scalar asymptotic terms but does not change the order.

A packed-bit, streaming-mean implementation could reduce the Jaccard component to (O(E^2\lceil p/w\rceil)) time and (O(E\lceil p/w\rceil+E)) working memory, but that is an implementation option, not a property demonstrated by the current five-run experiments.

## Practical interpretation for the manuscript's (R=5)

With five retained runs, (E\leq5). At most 10 distinct unordered off-diagonal Jaccard comparisons, or 25 ordered matrix entries including self-comparisons, are required. Even for a candidate universe containing many thousands of features, canonical mask construction and pairwise locking are small compared with fitting the development-CV random-forest evaluators that produce (L_r). The full pairwise matrix is therefore appropriate for auditability in the present experiments.

This observation does not establish large-bank scalability. If (E) grows, pairwise work and pairwise audit size grow quadratically; if (p) grows, dense canonical hashing and dense Jaccard grow linearly in (p). The five-run use case supplies no empirical evidence about performance for hundreds or thousands of candidates.
