# Proposed Algorithm 1 revision

Replace locking lines 17-22 only:

> 17. Compute \(L_{\mathrm{best}}=\max_rL_r\), absolute empirical regret \(R_r=L_{\mathrm{best}}-L_r\), and any prespecified secondary regret quantity.
>
> 18. Form the strict eligible pool \(E_\delta=\{r:R_r\leq\delta\}\) (or the prespecified relative or best-run-SE-scaled analogue); never add a candidate outside the threshold.
>
> 19. Encode every candidate in the common ordered universe as a canonical `uint8` mask and compute its stable SHA-256 mask digest; retain duplicate masks as separate voting candidates and preserve source-run provenance.
>
> 20. **If** \(E_\delta\) is a singleton, select its sole candidate and record mean Jaccard as undefined.
>
> 21. **Otherwise,** compute eligible-pool pairwise and mean Jaccard values; select the largest-mean-Jaccard medoid, resolving ties by higher \(L_r\), smaller feature count, then lexicographically smaller stable mask digest. Exact duplicate records denote the same feature set; normalize source provenance only after feature-set selection.
>
> 22. Verify that the selected candidate belongs to \(E_\delta\) and satisfies the declared empirical regret threshold; export canonical masks and hashes, scores, fold scores, regrets, eligibility, duplicate multiplicity, Jaccard values, tie path, provenance, version, and configuration hash.
