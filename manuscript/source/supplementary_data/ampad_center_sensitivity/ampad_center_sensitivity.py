"""Read-only prediction reuse: fixed-center AMP-AD AUROC sensitivity.

No fitting, selection, tuning, figure generation, or manuscript edits. Outputs
are aggregate statistics only. Run with the existing scientific Python runtime.
The bootstrap exactly reproduces the original sorted contrast / seed-42 stream.
"""
from pathlib import Path
import hashlib
import json
import time

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ANALYSIS = ROOT / "analysis/ampad_updated_one_time_heldout_20260808"
ARCHIVE = ROOT / "_codex_tmp/ampad_20260731_review/results/AMPAD_bScore_3class_RFECV_budget_calibration"
CENTERS = ["emory", "mayo", "mount_sinai", "rush"]
BRANCHES = ["boruta_rf", "svm_l1", "xgboost"]
CAPS = ["low", "reference"]
COMPARATORS = ["locked_medoid", "rfecv_only"]
P = ["probability_low", "probability_moderate", "probability_high"]
B = 2000
SEED = 42


def macro_auc(y, prob):
    return float(np.mean([roc_auc_score(y == k, prob[:, k]) for k in range(3)]))


def weighted_auc_draws(y, prob, weights):
    """Exact empirical AUROC with integer bootstrap multiplicities, ties=1/2.

    Computing weighted ordered score groups avoids repeatedly materializing
    resampled predictions; it is algebraically identical to sklearn AUROC.
    """
    out = np.zeros(len(weights), dtype=float)
    for k in range(3):
        order = np.argsort(prob[:, k], kind="stable")
        scores = prob[order, k]
        starts = np.r_[0, np.flatnonzero(np.diff(scores)) + 1]
        positive = (y[order] == k).astype(float)
        ordered_w = weights[:, order]
        p = np.add.reduceat(ordered_w * positive, starts, axis=1)
        n = np.add.reduceat(ordered_w * (1 - positive), starts, axis=1)
        numerator = np.sum(p * (np.cumsum(n, axis=1) - .5 * n), axis=1)
        out += numerator / (p.sum(axis=1) * n.sum(axis=1)) / 3
    return out


def interval(values):
    return [float(v) for v in np.quantile(values, [.025, .975])]


def main():
    started = time.perf_counter()
    rng = np.random.default_rng(SEED)
    center_rows, sensitivity_rows = [], []
    inputs, qa = {}, []
    original = pd.read_csv(ANALYSIS / "paired_condition_contrasts.csv")
    original = original[original.metric.eq("macro_auroc")]
    condition_metrics = pd.read_csv(ANALYSIS / "condition_metrics.csv")
    for branch in BRANCHES:
        for cap in CAPS:
            for comparator in COMPARATORS:
                frames = []
                for center in CENTERS:
                    updated_path = ANALYSIS / "outputs" / f"{center}__{branch}__{cap}__updated_locked_predictions.csv"
                    archived_path = ARCHIVE / branch / center / cap / "evaluation" / f"{comparator}_heldout_predictions.csv"
                    for path in (updated_path, archived_path):
                        inputs[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
                    # The original evaluation used updated probabilities in
                    # memory immediately after writing them. Round-trip parsing
                    # recovers those floats and avoids changing near-tied ranks.
                    left = pd.read_csv(updated_path, dtype={"individualID": str}, float_precision="round_trip")
                    right = pd.read_csv(archived_path, dtype={"individualID": str})
                    assert not left.individualID.duplicated().any()
                    assert not right.individualID.duplicated().any()
                    merged = left.merge(right, on=["individualID", "true_label"], suffixes=("_left", "_right"), validate="one_to_one")
                    assert len(merged) == len(left) == len(right)
                    merged["center"] = center
                    frames.append(merged)
                data = pd.concat(frames, ignore_index=True)
                assert not data.individualID.duplicated().any(), "Participant appears in multiple held-out centers"
                y = data.true_label.to_numpy(int)
                center_labels = data.center.to_numpy(str)
                left = data[[f"{p}_left" for p in P]].to_numpy(float)
                right = data[[f"{p}_right" for p in P]].to_numpy(float)
                assert np.isfinite(left).all() and np.isfinite(right).all()
                assert np.allclose(left.sum(axis=1), 1) and np.allclose(right.sum(axis=1), 1)
                cells = [np.flatnonzero((center_labels == c) & (y == k)) for c in np.unique(center_labels) for k in range(3)]
                assert all(len(ix) > 0 for ix in cells)
                weights = np.zeros((B, len(y)), dtype=np.int16)
                validation_indices = []
                for b in range(B):
                    ix = np.concatenate([rng.choice(cell, size=len(cell), replace=True) for cell in cells])
                    weights[b] = np.bincount(ix, minlength=len(y))
                    if b < 5:
                        validation_indices.append(ix)
                left_draws = weighted_auc_draws(y, left, weights)
                right_draws = weighted_auc_draws(y, right, weights)
                pooled_draws = left_draws - right_draws
                observed_pooled = macro_auc(y, left) - macro_auc(y, right)
                for b, ix in enumerate(validation_indices):
                    assert abs(left_draws[b] - macro_auc(y[ix], left[ix])) < 1e-12
                    assert abs(right_draws[b] - macro_auc(y[ix], right[ix])) < 1e-12
                original_row = original[(original.branch == branch) & (original.cap == cap) & (original.comparator == f"archived_{comparator}")].iloc[0]
                ci_pooled = interval(pooled_draws)
                differences = np.abs(np.array([observed_pooled, *ci_pooled]) - original_row[["updated_minus_comparator", "ci_low", "ci_high"]].to_numpy(float))
                assert np.max(differences) < 1e-12, (branch, cap, comparator, differences)
                center_differences, center_draws, sizes = [], [], []
                for center in CENTERS:
                    ix = np.flatnonzero(center_labels == center)
                    yl, pl, pr, w = y[ix], left[ix], right[ix], weights[:, ix]
                    observed_left, observed_right = macro_auc(yl, pl), macro_auc(yl, pr)
                    dl, dr = weighted_auc_draws(yl, pl, w), weighted_auc_draws(yl, pr, w)
                    delta = observed_left - observed_right
                    ci = interval(dl - dr)
                    for variant, value in [("updated_regret_locked", observed_left), (f"archived_{comparator}", observed_right)]:
                        frozen = condition_metrics[(condition_metrics.center == center) & (condition_metrics.branch == branch) & (condition_metrics.cap == cap) & (condition_metrics.variant == variant)].iloc[0]
                        assert abs(float(frozen.macro_auroc) - value) < 1e-12
                    center_rows.append(dict(center=center, branch=branch, cap=cap, comparator=f"archived_{comparator}", n_heldout=len(ix), updated_auroc=observed_left, updated_ci_low=interval(dl)[0], updated_ci_high=interval(dl)[1], comparator_auroc=observed_right, comparator_ci_low=interval(dr)[0], comparator_ci_high=interval(dr)[1], difference=delta, ci_low=ci[0], ci_high=ci[1], bootstrap_resamples=B))
                    center_differences.append(delta)
                    center_draws.append(dl - dr)
                    sizes.append(len(ix))
                equal_draws = np.mean(center_draws, axis=0)
                weighted_draws = np.average(center_draws, axis=0, weights=sizes)
                eq_ci, w_ci = interval(equal_draws), interval(weighted_draws)
                sensitivity_rows.append(dict(branch=branch, cap=cap, comparator=f"archived_{comparator}", n_participants=len(y), n_fixed_centers=len(CENTERS), pooled_difference=observed_pooled, pooled_ci_low=ci_pooled[0], pooled_ci_high=ci_pooled[1], equal_center_difference=float(np.mean(center_differences)), equal_center_ci_low=eq_ci[0], equal_center_ci_high=eq_ci[1], participant_weighted_center_difference=float(np.average(center_differences, weights=sizes)), participant_weighted_center_ci_low=w_ci[0], participant_weighted_center_ci_high=w_ci[1], positive_centers=int(np.sum(np.array(center_differences) > 0)), bootstrap_resamples=B))
                qa.append(dict(branch=branch, cap=cap, comparator=comparator, max_error_against_saved_pooled_point_and_ci=float(np.max(differences)), n=len(y), sklearn_weighted_auroc_checks=10, all_center_points_match_frozen_aggregate=True))
    pd.DataFrame(center_rows).to_csv(HERE / "ampad_center_paired_auroc_ci.csv", index=False)
    pd.DataFrame(sensitivity_rows).to_csv(HERE / "ampad_center_equal_weight_sensitivity.csv", index=False)
    manifest = dict(analysis="Post hoc fixed-center AUROC estimand sensitivity; no fitting or tuning", seed=SEED, replicates=B, bootstrap_unit="Participant resampled with replacement independently within each fixed held-out-center by true-class stratum; same multiplicities for all methods and within-center AUROC components", pooled_estimand="Macro OVR AUROC after concatenating the predictions of four different held-out-center models", equal_center_estimand="Arithmetic mean of four within-center macro OVR AUROC differences", participant_weighted_center_estimand="Center AUROC differences weighted by fixed center sample counts; not pooled AUROC", confidence_scope="Conditional on the four observed centers, fixed masks and fitted models; not confidence intervals for a population of future centers or full pipeline retraining", multiplicity="Nominal percentile 95% intervals; exploratory and not multiplicity adjusted", no_participant_level_outputs=True, checks=qa, input_sha256=inputs, script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), elapsed_seconds=time.perf_counter()-started)
    (HERE / "ampad_center_sensitivity_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"status": "complete", "center_contrasts": len(center_rows), "sensitivity_contrasts": len(sensitivity_rows), "max_saved_pooled_reproduction_error": max(x["max_error_against_saved_pooled_point_and_ci"] for x in qa), "elapsed_seconds": manifest["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
