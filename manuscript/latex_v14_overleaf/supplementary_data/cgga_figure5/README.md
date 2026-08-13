# Figure 5 CGGA source data

These three aggregate CSV files reproduce the redesigned V12 main Figure 5. No participant-level matrix, identifier, or prediction row is included.

- `panel_a_compression_auroc.csv` is a column-preserving manuscript-local extract of the Direct and archived locked-medoid rows in `data/plot_data/Figure_5/figure5b_compression_auroc.csv`; the historical `full_medoid` variant label is renamed `locked_medoid` for consistency with the manuscript.
- `panel_b_locked_minus_rfecv.csv` is an exact manuscript-local copy of `data/plot_data/Figure_6/figure6c_paired_bootstrap_differences.csv`, with the difference column renamed for figure clarity. The intervals use 2,000 common class-stratified bootstrap resamples with seed 42 and were computed before this redesign from aligned frozen held-out predictions.
- `panel_c_five_run_agreement.csv` joins run-count means and mean pairwise Jaccard from `data/plot_data/Figure_6/figure6b_jaccard_summary.csv` with chance-corrected Nogueira agreement from the six CGGA branch-by-guidance banks in `analysis/regret_revision/figure2_compression_regret_plot_data.csv`. The latter values are invariant to the downstream locking-rule row.

The redesign does not rerun a GA, refit a model, regenerate a held-out prediction, or alter an empirical value. `scripts/build_cgga_figure5.py` validates the expected rows and generates deterministic SVG, PDF, and PNG assets on a native 170-mm canvas.

For byte-reproducible artwork, use Python 3.12 and install the exact plotting environment recorded in `requirements.txt` before running the builder:

```sh
python -m pip install -r supplementary_data/cgga_figure5/requirements.txt
python scripts/build_cgga_figure5.py
```

From the complete reproducibility repository, the upstream-to-local value mapping and frozen upstream checksums can be verified separately with:

```sh
python manuscript/latex_v12_overleaf/scripts/validate_cgga_figure5_provenance.py
```
