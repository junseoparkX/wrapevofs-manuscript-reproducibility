# Protocol-defined seed-bank reproducibility comparison (Table S33)

This is the original four-bank comparison of the same 240 GA runs subsequently regrouped for exploratory calibration in Table S32. The local protocol was frozen before candidate generation; this is not an external preregistration.

All branches, both scorer schemes, nested prefixes R=5/10/20, and all six pairs of the four banks per condition are retained. `frozen/results/` contains 108 pair rows, 72 selected-bank rows, 18 condition summaries, and 480 candidate/scorer records. The frozen code, local freeze records, resource amendment, and launch receipt are byte-preserved. Frozen remote scripts document the original environment; the independent script below is portable.

From `manuscript/source/` (Python 3.10+, NumPy, pandas):

```sh
python supplementary_data/seed_bank_reproducibility/verify_registered_seed_banks.py --output /tmp/wrapevofs-seed-bank-review
```

The verifier reads released masks and development fold scores in the sibling `tolerance_calibration/` folder. It independently reconstructs all 72 choices and 108 pair values, checks protocol/code/results hashes, and writes all 18 condition summaries and six equal-branch means. No participant arrays, held-out predictions, model fitting, or external access are required.

Primary equal-branch locked-minus-highest-score Jaccard differences are -0.008654, -0.010513, and -0.018120 at R=5/10/20. Exact agreement is zero for both rules in every condition. Secondary common-RF-seed results are retained in full. Pairs share banks; prefixes and scorers reuse candidates, and branches share participants. No CI, p value, or independent-participant inference is made.

Metadata correction: the exported Boruta-RF target_k field was 18; the frozen protocol and executed GA code specify 8. The canonical candidate audit now reports 8. The original export and exact cell-level correction record are retained in `../tolerance_calibration/metadata_history/` and `TARGET_METADATA_CORRECTION.json`. All masks, scores, choices, predictions, and numerical results are unchanged.
