"""Build development-only compression/regret and audit outputs.

The script never reads held-out outcomes until all selection rows have been
fixed. Held-out point estimates are joined afterward as secondary annotations.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score


ROOT = Path(__file__).resolve().parents[2]
GBM_ROOT = ROOT.parent / "gbm_package"
AUDIT_DIR = ROOT / "audits"
sys.path.insert(0, str(GBM_ROOT / "src"))

from wrapevofs.config import LockingConfig  # noqa: E402
from wrapevofs.locking import (  # noqa: E402
    LockingCandidate,
    jaccard,
    lock_representative_run,
)


CGGA = GBM_ROOT / "analysis" / "figure5_figure6_cgga_package"
AMPAD = (
    ROOT
    / "_codex_tmp"
    / "ampad_20260731_review"
    / "results"
    / "AMPAD_bScore_3class_RFECV_budget_calibration"
)
ADNI = ROOT / "data" / "plot_data" / "Figure_2"
TOLERANCES = (0.0, 0.005, 0.01, 0.02)
EPSILON = 1e-12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def feature_list(value: object) -> list[str]:
    if pd.isna(value):
        return []
    return [item for item in str(value).split("|") if item]


def pairwise_mean(feature_sets: dict[int, list[str]]) -> float:
    ids = sorted(feature_sets)
    values = [
        jaccard(feature_sets[left], feature_sets[right])
        for pos, left in enumerate(ids)
        for right in ids[pos + 1 :]
    ]
    return float(np.mean(values)) if values else np.nan


def selected_mean_jaccard(run_id: int, feature_sets: dict[int, list[str]]) -> float:
    peers = [
        jaccard(feature_sets[run_id], feature_sets[other])
        for other in feature_sets
        if other != run_id
    ]
    return float(np.mean(peers)) if peers else 1.0


def nogueira_coefficient(feature_sets: dict[int, list[str]]) -> float:
    """Nogueira agreement for a valid run-by-feature selection matrix."""

    universe = sorted({feature for values in feature_sets.values() for feature in values})
    matrix = np.asarray(
        [[feature in set(feature_sets[run]) for feature in universe] for run in sorted(feature_sets)],
        dtype=float,
    )
    if matrix.shape[0] < 2 or matrix.shape[1] == 0:
        return np.nan
    mean_k = float(matrix.sum(axis=1).mean())
    p = matrix.shape[1]
    expected = (mean_k / p) * (1.0 - mean_k / p)
    if expected <= EPSILON:
        return np.nan
    variances = matrix.var(axis=0, ddof=1)
    return float(1.0 - variances.mean() / expected)


def legacy_lock(candidates: list[LockingCandidate]):
    return lock_representative_run(
        candidates,
        LockingConfig(
            enabled=True,
            strategy="top_k_jaccard_medoid",
            top_k=3,
            minimum_pool_size=1,
            locking_metric="roc_auc",
        ),
        software_version="0.1.0",
    )


def regret_lock(
    candidates: list[LockingCandidate],
    *,
    tolerance_mode: str,
    tolerance: float,
    locking_metric: str,
):
    return lock_representative_run(
        candidates,
        LockingConfig(
            enabled=True,
            strategy="regret_constrained_medoid",
            tolerance_mode=tolerance_mode,
            regret_tolerance=tolerance,
            minimum_pool_size=1,
            fallback_rule="strict_eligible_only",
            locking_metric=locking_metric,
            cv_folds=5,
            random_state=42,
        ),
        software_version="0.1.0",
        seeds={"locking_cv_seed": 42, "candidate_run_seed_rule": "42 + run_id"},
    )


def score_cgga_features(
    X: pd.DataFrame,
    y: pd.Series,
    features: list[str],
    seed: int,
) -> tuple[float, tuple[float, ...]]:
    missing = sorted(set(features) - set(X.columns))
    if missing:
        raise KeyError(f"CGGA feature set contains missing columns: {missing[:5]}")
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_leaf=2,
        bootstrap=True,
        random_state=seed,
        n_jobs=1,
    )
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(
        model,
        X.loc[:, features],
        y,
        cv=folds,
        scoring="roc_auc",
        n_jobs=1,
    )
    return float(scores.mean()), tuple(float(value) for value in scores)


def compression_row(
    *,
    dataset: str,
    branch: str,
    center: str,
    cap: str,
    condition: str,
    rule: str,
    selected_run: int | None,
    selected_count: int | None,
    direct_count: int,
    selected_score: float | None,
    best_score: float | None,
    metric: str,
    mean_pairwise_jaccard: float | None,
    selected_medoid_mean_jaccard: float | None,
    nogueira: float | None,
    status: str = "complete",
    note: str = "",
) -> dict[str, object]:
    return {
        "dataset": dataset,
        "branch": branch,
        "center": center,
        "cap": cap,
        "condition": condition,
        "selection_rule": rule,
        "selected_run": selected_run,
        "selected_feature_count": selected_count,
        "direct_feature_count": direct_count,
        "compression_ratio": (
            1.0 - selected_count / direct_count
            if selected_count is not None and direct_count > 0
            else np.nan
        ),
        "development_locking_metric": metric,
        "best_saved_run_score": best_score,
        "selected_development_score": selected_score,
        "development_cv_regret": (
            best_score - selected_score
            if best_score is not None and selected_score is not None
            else np.nan
        ),
        "mean_pairwise_jaccard": mean_pairwise_jaccard,
        "selected_medoid_mean_jaccard": selected_medoid_mean_jaccard,
        "nogueira_seed_agreement": nogueira,
        "heldout_metric": "",
        "heldout_estimate": np.nan,
        "heldout_direct_estimate": np.nan,
        "heldout_delta": np.nan,
        "heldout_source": "",
        "selection_used_heldout": False,
        "status": status,
        "note": note,
    }


def append_sensitivity(
    rows: list[dict[str, object]],
    audits: list[pd.DataFrame],
    *,
    dataset: str,
    branch: str,
    center: str,
    cap: str,
    condition: str,
    mode: str,
    tolerance: float | str,
    result=None,
    status: str = "complete",
    note: str = "",
) -> None:
    if result is None:
        rows.append(
            {
                "dataset": dataset,
                "branch": branch,
                "center": center,
                "cap": cap,
                "condition": condition,
                "tolerance_mode": mode,
                "regret_tolerance": tolerance,
                "eligible_pool_size": np.nan,
                "selected_run": np.nan,
                "selected_feature_count": np.nan,
                "selected_score": np.nan,
                "absolute_regret": np.nan,
                "selected_mean_jaccard": np.nan,
                "fallback_expansion": np.nan,
                "selection_used_heldout": False,
                "status": status,
                "note": note,
            }
        )
        return
    selected = result.candidate_audit.loc[result.candidate_audit["selected"]].iloc[0]
    rows.append(
        {
            "dataset": dataset,
            "branch": branch,
            "center": center,
            "cap": cap,
            "condition": condition,
            "tolerance_mode": mode,
            "regret_tolerance": tolerance,
            "eligible_pool_size": len(result.metadata["eligible_run_ids"]),
            "selected_run": result.selected_run_id,
            "selected_feature_count": len(result.selected_features),
            "selected_score": selected["locking_score"],
            "absolute_regret": selected["absolute_regret"],
            "selected_mean_jaccard": selected["mean_jaccard"],
            "fallback_expansion": result.metadata["fallback_expansion_occurred"],
            "selection_used_heldout": False,
            "status": status,
            "note": note,
        }
    )
    audit = result.candidate_audit.copy()
    audit.insert(0, "dataset", dataset)
    audit.insert(1, "branch", branch)
    audit.insert(2, "center", center)
    audit.insert(3, "cap", cap)
    audit.insert(4, "condition", condition)
    audit.insert(5, "sensitivity_tolerance_mode", mode)
    audit.insert(6, "sensitivity_regret_tolerance", tolerance)
    audits.append(audit)


def build_cgga(
    compression: list[dict[str, object]],
    sensitivity: list[dict[str, object]],
    candidate_audits: list[pd.DataFrame],
    penalty: list[dict[str, object]],
    metrics: list[dict[str, object]],
    source_paths: set[Path],
) -> None:
    tables = CGGA / "inputs" / "tables"
    X_path = CGGA / "inputs" / "data" / "X_train_selected_union.csv"
    y_path = CGGA / "inputs" / "data" / "y_train.csv"
    candidates_path = tables / "ga_candidate_feature_sets.csv"
    summary_path = tables / "ga_run_artifact_summary.csv"
    direct_path = tables / "direct_feature_sets.csv"
    rfecv_path = tables / "rfecv_feature_sets.csv"
    heldout_path = (
        CGGA
        / "final_manuscript_outputs"
        / "tables"
        / "supplementary"
        / "Table_S19_component_ablation_results.csv"
    )
    source_paths.update(
        {X_path, y_path, candidates_path, summary_path, direct_path, rfecv_path, heldout_path}
    )
    X = pd.read_csv(X_path)
    y_frame = pd.read_csv(y_path)
    y = y_frame["MGMT_label"] if "MGMT_label" in y_frame else y_frame.iloc[:, 0]
    candidate_table = pd.read_csv(candidates_path)
    run_summary = pd.read_csv(summary_path)
    direct_table = pd.read_csv(direct_path)
    rfecv_table = pd.read_csv(rfecv_path)
    heldout = pd.read_csv(heldout_path)
    direct_heldout = (
        heldout[(heldout["variant"] == "direct")]
        .set_index("method")["roc_auc"]
        .to_dict()
    )

    for (branch, condition), group in run_summary.groupby(["method", "condition"]):
        feature_sets = {
            int(run_id): values["feature"].astype(str).tolist()
            for run_id, values in candidate_table[
                (candidate_table["method"] == branch)
                & (candidate_table["condition"] == condition)
            ].groupby("run_id")
        }
        scored: list[LockingCandidate] = []
        for run_id in sorted(feature_sets):
            score, folds = score_cgga_features(X, y, feature_sets[run_id], 42 + run_id)
            scored.append(
                LockingCandidate(run_id, feature_sets[run_id], score, folds, 42 + run_id)
            )
        score_map = {item.run_id: item.locking_score for item in scored}
        best_run = min(score_map, key=lambda run: (-score_map[run], run))
        fixed_run = 1
        legacy = legacy_lock(scored)
        all_run = regret_lock(
            scored,
            tolerance_mode="absolute",
            tolerance=1.0,
            locking_metric="roc_auc",
        )
        preferred = regret_lock(
            scored,
            tolerance_mode="absolute",
            tolerance=0.01,
            locking_metric="roc_auc",
        )
        best_score = score_map[best_run]
        direct_features = direct_table.loc[
            direct_table["method"] == branch, "feature"
        ].astype(str).tolist()
        direct_count = len(direct_features)
        rfecv_features = rfecv_table.loc[
            (rfecv_table["method"] == branch)
            & (rfecv_table["condition"] == condition)
            & (rfecv_table["variant"] == "rfecv_target"),
            "feature",
        ].astype(str).tolist()
        mean_pair = pairwise_mean(feature_sets)
        nogueira = nogueira_coefficient(feature_sets)

        selections = [
            ("highest_development_cv_run", best_run),
            ("fixed_run_1", fixed_run),
            ("legacy_top_three_medoid", legacy.selected_run_id),
            ("all_run_medoid", all_run.selected_run_id),
            ("regret_constrained_medoid_abs_0.01", preferred.selected_run_id),
        ]
        for rule, run_id in selections:
            compression.append(
                compression_row(
                    dataset="CGGA",
                    branch=branch,
                    center="CGGA fixed development/held-out split",
                    cap="not_applicable",
                    condition=condition,
                    rule=rule,
                    selected_run=run_id,
                    selected_count=len(feature_sets[run_id]),
                    direct_count=direct_count,
                    selected_score=score_map[run_id],
                    best_score=best_score,
                    metric="ROC AUROC",
                    mean_pairwise_jaccard=mean_pair,
                    selected_medoid_mean_jaccard=selected_mean_jaccard(run_id, feature_sets),
                    nogueira=nogueira,
                )
            )
        for rule, features in (("Direct", direct_features), ("RFECV-only", rfecv_features)):
            score, _ = score_cgga_features(X, y, features, 42)
            compression.append(
                compression_row(
                    dataset="CGGA",
                    branch=branch,
                    center="CGGA fixed development/held-out split",
                    cap="not_applicable",
                    condition=condition,
                    rule=rule,
                    selected_run=None,
                    selected_count=len(features),
                    direct_count=direct_count,
                    selected_score=score,
                    best_score=best_score,
                    metric="ROC AUROC",
                    mean_pairwise_jaccard=None,
                    selected_medoid_mean_jaccard=None,
                    nogueira=None,
                    note="Comparator rescored with the same development-only CV design.",
                )
            )

        for tolerance in TOLERANCES:
            result = regret_lock(
                scored,
                tolerance_mode="absolute",
                tolerance=tolerance,
                locking_metric="roc_auc",
            )
            append_sensitivity(
                sensitivity,
                candidate_audits,
                dataset="CGGA",
                branch=branch,
                center="CGGA fixed development/held-out split",
                cap="not_applicable",
                condition=condition,
                mode="absolute",
                tolerance=tolerance,
                result=result,
            )
        best_run_se_scaled = regret_lock(
            scored,
            tolerance_mode="best_run_se_scaled",
            tolerance=0.0,
            locking_metric="roc_auc",
        )
        append_sensitivity(
            sensitivity,
            candidate_audits,
            dataset="CGGA",
            branch=branch,
            center="CGGA fixed development/held-out split",
            cap="not_applicable",
            condition=condition,
            mode="best_run_se_scaled",
            tolerance="best_run_score_se",
            result=best_run_se_scaled,
        )

        config_path = CGGA / "inputs" / "runs" / branch / condition / "experiment_config_snapshot.json"
        history_path = CGGA / "inputs" / "runs" / branch / condition / "ga" / branch / "history.csv"
        top_path = CGGA / "inputs" / "runs" / branch / condition / "ga" / branch / "top_solutions.csv"
        source_paths.update({config_path, history_path, top_path})
        config = json.loads(config_path.read_text(encoding="utf-8"))
        history = pd.read_csv(history_path)
        top = pd.read_csv(top_path)
        zero_fraction = float(np.mean(np.isclose(top["score"], 0.0)))
        all_zero_generations = int(np.isclose(history["best_score"], 0.0).sum())
        selected_run_zero_based = legacy.selected_run_id - 1
        selected_summary = group.loc[group["run_id"] == legacy.selected_run_id].iloc[0]
        warning = []
        if zero_fraction > 0.5:
            warning.append("more_than_half_run_best_legacy_fitness_zero")
        if all_zero_generations:
            warning.append("all_zero_generation_detected")
        penalty.append(
            {
                "dataset": "CGGA",
                "branch": branch,
                "center": "CGGA fixed split",
                "cap": "not_applicable",
                "condition": condition,
                "target_count": int(selected_summary["rfecv_target_k"]),
                "selected_count": len(legacy.selected_features),
                "target_deviation": abs(
                    len(legacy.selected_features) - int(selected_summary["rfecv_target_k"])
                ),
                "fraction_zero_legacy_fitness": zero_fraction,
                "zero_fraction_denominator": "five retained run-best candidates",
                "number_all_zero_generations": all_zero_generations,
                "number_uniform_sampling_fallbacks": all_zero_generations,
                "uniform_fallback_basis": "inferred: legacy generation best=0 implies all weights=0",
                "final_development_score": score_map[legacy.selected_run_id],
                "selected_run": legacy.selected_run_id,
                "archived_run_id_zero_based": selected_run_zero_based,
                "warning_status": "|".join(warning) if warning else "none",
                "known_failure_mode": False,
            }
        )
        metrics.append(
            {
                "dataset": "CGGA",
                "branch": branch,
                "center": "CGGA fixed split",
                "cap": "not_applicable",
                "condition": condition,
                "rfecv_metric": config["rfecv"]["scoring"],
                "ga_base_score_metric": config["ga"]["fitness_metric"],
                "locking_metric": "roc_auc",
                "heldout_evaluation_metrics": "roc_auc|auprc|balanced_accuracy",
                "development_metrics_aligned": len(
                    {
                        config["rfecv"]["scoring"],
                        config["ga"]["fitness_metric"],
                        "roc_auc",
                    }
                )
                == 1,
                "warning": "" if config["ga"]["fitness_metric"] == "roc_auc" else "staged_heuristic_mixed_development_metrics",
                "legacy_configuration": True,
            }
        )

    # Held-out values are joined only after all CGGA selection rows are fixed.
    for row in compression:
        if row["dataset"] != "CGGA":
            continue
        branch = row["branch"]
        direct_auc = direct_heldout.get(branch, np.nan)
        variant = None
        if row["selection_rule"] == "Direct":
            variant = "direct"
        elif row["selection_rule"] == "RFECV-only" and row["condition"] == "penalty":
            variant = "rfecv_only"
        elif row["condition"] == "penalty":
            run_matches = heldout[
                (heldout["method"] == branch)
                & (heldout["run_id"] == row["selected_run"])
                & (heldout["variant"].isin(["single_run", "best_cv", "full_medoid"]))
            ]
            if not run_matches.empty:
                variant = str(run_matches.iloc[0]["variant"])
        elif row["selection_rule"] == "legacy_top_three_medoid":
            variant = "no_penalty_medoid"
        match = heldout[(heldout["method"] == branch) & (heldout["variant"] == variant)]
        if variant is not None and not match.empty:
            estimate = float(match.iloc[0]["roc_auc"])
            row.update(
                {
                    "heldout_metric": "ROC AUROC",
                    "heldout_estimate": estimate,
                    "heldout_direct_estimate": direct_auc,
                    "heldout_delta": estimate - direct_auc,
                    "heldout_source": f"archived Table_S19 variant={variant}; joined after locking",
                }
            )


def build_ampad(
    compression: list[dict[str, object]],
    sensitivity: list[dict[str, object]],
    candidate_audits: list[pd.DataFrame],
    penalty: list[dict[str, object]],
    metrics: list[dict[str, object]],
    source_paths: set[Path],
) -> None:
    for ga_dir in sorted(AMPAD.glob("*/*/*/ga")):
        branch, center, cap = ga_dir.relative_to(AMPAD).parts[:3]
        base = ga_dir.parent
        audit_path = ga_dir / "medoid_locking_audit.csv"
        top_path = ga_dir / "top_solutions.csv"
        history_path = ga_dir / "history.csv"
        checkpoint_sets_path = base / "checkpoints" / "top_feature_sets_live.npy"
        checkpoint_rows_path = base / "checkpoints" / "top_solutions_live.csv"
        budget_path = base / "budget_summary.json"
        config_path = base / "config_resolved.yaml"
        source_paths.update(
            {
                audit_path,
                top_path,
                history_path,
                checkpoint_sets_path,
                checkpoint_rows_path,
                budget_path,
                config_path,
            }
        )
        audit = pd.read_csv(audit_path)
        top = pd.read_csv(top_path)
        history = pd.read_csv(history_path)
        budget = json.loads(budget_path.read_text(encoding="utf-8"))
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        checkpoint_sets = np.load(checkpoint_sets_path, allow_pickle=True)
        checkpoint_rows = pd.read_csv(checkpoint_rows_path)
        if len(checkpoint_sets) != len(checkpoint_rows):
            raise ValueError(f"Checkpoint feature-set mapping mismatch in {base}")
        feature_sets = {
            int(checkpoint_rows.iloc[index]["run_id"]) + 1: [
                str(feature) for feature in checkpoint_sets[index]
            ]
            for index in range(len(checkpoint_rows))
        }
        scored = [
            LockingCandidate(
                int(row.run_id),
                feature_sets[int(row.run_id)],
                float(row.dev_cv_macro_auroc_mean),
                None,
                42 + int(row.run_id),
            )
            for row in audit.itertuples(index=False)
        ]
        score_map = {item.run_id: item.locking_score for item in scored}
        best_run = min(score_map, key=lambda run: (-score_map[run], run))
        legacy_run = int(audit.loc[audit["is_locked_medoid"], "run_id"].iloc[0])
        legacy = legacy_lock(scored)
        if legacy.selected_run_id != legacy_run:
            raise AssertionError(f"Legacy locking mismatch for {branch}/{center}/{cap}")
        all_run = regret_lock(
            scored,
            tolerance_mode="absolute",
            tolerance=1.0,
            locking_metric="macro_ovr_auroc",
        )
        preferred = regret_lock(
            scored,
            tolerance_mode="absolute",
            tolerance=0.01,
            locking_metric="macro_ovr_auroc",
        )
        direct_count = int(budget["direct"]["n_features"])
        best_score = score_map[best_run]
        mean_pair = pairwise_mean(feature_sets)
        nogueira = nogueira_coefficient(feature_sets)
        for rule, run_id in [
            ("highest_development_cv_run", best_run),
            ("fixed_run_1", 1),
            ("legacy_top_three_medoid", legacy_run),
            ("all_run_medoid", all_run.selected_run_id),
            ("regret_constrained_medoid_abs_0.01", preferred.selected_run_id),
        ]:
            compression.append(
                compression_row(
                    dataset="AMP-AD",
                    branch=branch,
                    center=center,
                    cap=cap,
                    condition="legacy_zero_truncated",
                    rule=rule,
                    selected_run=run_id,
                    selected_count=len(feature_sets[run_id]),
                    direct_count=direct_count,
                    selected_score=score_map[run_id],
                    best_score=best_score,
                    metric="macro OvR AUROC",
                    mean_pairwise_jaccard=mean_pair,
                    selected_medoid_mean_jaccard=selected_mean_jaccard(run_id, feature_sets),
                    nogueira=nogueira,
                )
            )
        for rule, variant in (("Direct", "direct"), ("RFECV-only", "rfecv_only")):
            compression.append(
                compression_row(
                    dataset="AMP-AD",
                    branch=branch,
                    center=center,
                    cap=cap,
                    condition="legacy_zero_truncated",
                    rule=rule,
                    selected_run=None,
                    selected_count=int(budget[variant]["n_features"]),
                    direct_count=direct_count,
                    selected_score=None,
                    best_score=best_score,
                    metric="macro OvR AUROC",
                    mean_pairwise_jaccard=None,
                    selected_medoid_mean_jaccard=None,
                    nogueira=None,
                    note="Comparable development locking score was not saved for this comparator.",
                )
            )
        for tolerance in TOLERANCES:
            result = regret_lock(
                scored,
                tolerance_mode="absolute",
                tolerance=tolerance,
                locking_metric="macro_ovr_auroc",
            )
            append_sensitivity(
                sensitivity,
                candidate_audits,
                dataset="AMP-AD",
                branch=branch,
                center=center,
                cap=cap,
                condition="legacy_zero_truncated",
                mode="absolute",
                tolerance=tolerance,
                result=result,
            )
        append_sensitivity(
            sensitivity,
            candidate_audits,
            dataset="AMP-AD",
            branch=branch,
            center=center,
            cap=cap,
            condition="legacy_zero_truncated",
            mode="best_run_se_scaled",
            tolerance="best_run_score_se",
            status="unavailable_missing_fold_scores",
            note="Only development-CV means and SDs were archived; fold vectors were not saved.",
        )

        zero_fraction = float(np.mean(np.isclose(top["penalized_score"], 0.0)))
        all_zero_generations = int(np.isclose(history["best_score"], 0.0).sum())
        target_count = int(budget["rfecv_target_k"])
        selected_count = len(feature_sets[legacy_run])
        known_failure = branch == "svm_l1" and center == "rush" and cap == "low"
        warning = []
        if zero_fraction > 0.5:
            warning.append("more_than_half_run_best_legacy_fitness_zero")
        if all_zero_generations:
            warning.append("all_zero_generation_detected")
        if known_failure:
            warning.append("documented_ampad_svm_l1_rush_small_cap_failure_mode")
        penalty.append(
            {
                "dataset": "AMP-AD",
                "branch": branch,
                "center": center,
                "cap": cap,
                "condition": "legacy_zero_truncated",
                "target_count": target_count,
                "selected_count": selected_count,
                "target_deviation": abs(selected_count - target_count),
                "fraction_zero_legacy_fitness": zero_fraction,
                "zero_fraction_denominator": "five retained run-best candidates",
                "number_all_zero_generations": all_zero_generations,
                "number_uniform_sampling_fallbacks": all_zero_generations,
                "uniform_fallback_basis": "inferred: legacy generation best=0 implies all weights=0",
                "final_development_score": score_map[legacy_run],
                "selected_run": legacy_run,
                "archived_run_id_zero_based": legacy_run - 1,
                "warning_status": "|".join(warning) if warning else "none",
                "known_failure_mode": known_failure,
            }
        )
        development_metrics = {
            config["rfecv"]["scoring"],
            config["ga"]["fitness_metric"],
            "macro_ovr_auroc",
        }
        metrics.append(
            {
                "dataset": "AMP-AD",
                "branch": branch,
                "center": center,
                "cap": cap,
                "condition": "legacy_zero_truncated",
                "rfecv_metric": config["rfecv"]["scoring"],
                "ga_base_score_metric": config["ga"]["fitness_metric"],
                "locking_metric": "macro_ovr_auroc",
                "heldout_evaluation_metrics": "macro_auroc|weighted_auroc|macro_auprc|weighted_auprc|balanced_accuracy|macro_f1|accuracy",
                "development_metrics_aligned": len(development_metrics) == 1,
                "warning": "" if len(development_metrics) == 1 else "staged_heuristic_mixed_development_metrics",
                "legacy_configuration": True,
            }
        )

        # Secondary held-out join after the selection rules above are fixed.
        direct_auc = float(budget["direct"]["macro_auroc"])
        for row in compression:
            if not (
                row["dataset"] == "AMP-AD"
                and row["branch"] == branch
                and row["center"] == center
                and row["cap"] == cap
            ):
                continue
            variant = None
            if row["selection_rule"] == "Direct":
                variant = "direct"
            elif row["selection_rule"] == "RFECV-only":
                variant = "rfecv_only"
            elif row["selected_run"] == legacy_run:
                variant = "locked_medoid"
            if variant is not None:
                estimate = float(budget[variant]["macro_auroc"])
                row.update(
                    {
                        "heldout_metric": "macro OvR AUROC",
                        "heldout_estimate": estimate,
                        "heldout_direct_estimate": direct_auc,
                        "heldout_delta": estimate - direct_auc,
                        "heldout_source": f"archived budget_summary.json variant={variant}; joined after locking",
                    }
                )


def build_adni(
    compression: list[dict[str, object]],
    sensitivity: list[dict[str, object]],
    metrics: list[dict[str, object]],
    source_paths: set[Path],
) -> None:
    diagnostics_path = ADNI / "source_table_s2_ga_lock_diagnostics.csv"
    performance_path = ADNI / "source_table_s1_all_performance_metrics.csv"
    params_path = ADNI / "source_corrected_methods_hyperparameters.csv"
    source_paths.update({diagnostics_path, performance_path, params_path})
    diagnostics = pd.read_csv(diagnostics_path)
    performance = pd.read_csv(performance_path)
    params = pd.read_csv(params_path)
    label_to_branch = {"SVM-L1": "svm_l1", "XGBoost": "xgboost", "Boruta-RF": "boruta_rf"}
    for method_label, branch in label_to_branch.items():
        group = diagnostics[diagnostics["selector"] == branch].copy()
        direct = performance[
            (performance["selector"] == branch) & (performance["variant"] == "First stage")
        ].iloc[0]
        locked = performance[
            (performance["selector"] == branch) & (performance["variant"] == "RFECV+GA")
        ].iloc[0]
        score_map = group.set_index("candidate_set_id")["cv_balanced_accuracy_mean"].to_dict()
        count_map = group.set_index("candidate_set_id")["n_features"].to_dict()
        best_run = min(score_map, key=lambda run: (-score_map[run], run))
        locked_run = int(group.loc[group["is_locked_run"], "candidate_set_id"].iloc[0])
        best_score = float(score_map[best_run])
        for rule, run_id in (
            ("highest_development_cv_run", best_run),
            ("fixed_run_1", 1),
            ("legacy_top_three_medoid", locked_run),
        ):
            compression.append(
                compression_row(
                    dataset="ADNI",
                    branch=branch,
                    center="ADNI fixed split",
                    cap="not_applicable",
                    condition="legacy_archived",
                    rule=rule,
                    selected_run=run_id,
                    selected_count=int(count_map[run_id]),
                    direct_count=int(direct["n_features"]),
                    selected_score=float(score_map[run_id]),
                    best_score=best_score,
                    metric="balanced accuracy",
                    mean_pairwise_jaccard=None,
                    selected_medoid_mean_jaccard=(
                        float(group.loc[group["candidate_set_id"] == run_id, "mean_jaccard_with_top"].iloc[0])
                        if pd.notna(group.loc[group["candidate_set_id"] == run_id, "mean_jaccard_with_top"].iloc[0])
                        else None
                    ),
                    nogueira=None,
                    note="All nonlocked candidate masks were unavailable; full seed-agreement statistics could not be reconstructed.",
                )
            )
        compression.append(
            compression_row(
                dataset="ADNI",
                branch=branch,
                center="ADNI fixed split",
                cap="not_applicable",
                condition="legacy_archived",
                rule="Direct",
                selected_run=None,
                selected_count=int(direct["n_features"]),
                direct_count=int(direct["n_features"]),
                selected_score=float(direct["train_cv_balanced_accuracy_mean"]),
                best_score=best_score,
                metric="balanced accuracy",
                mean_pairwise_jaccard=None,
                selected_medoid_mean_jaccard=None,
                nogueira=None,
            )
        )
        for missing_rule in ("all_run_medoid", "regret_constrained_medoid_abs_0.01", "RFECV-only"):
            compression.append(
                compression_row(
                    dataset="ADNI",
                    branch=branch,
                    center="ADNI fixed split",
                    cap="not_applicable",
                    condition="legacy_archived",
                    rule=missing_rule,
                    selected_run=None,
                    selected_count=None,
                    direct_count=int(direct["n_features"]),
                    selected_score=None,
                    best_score=best_score,
                    metric="balanced accuracy",
                    mean_pairwise_jaccard=None,
                    selected_medoid_mean_jaccard=None,
                    nogueira=None,
                    status="unavailable_missing_candidate_masks",
                    note="The archived table contains scores/counts but not all five feature masks.",
                )
            )
        for tolerance in TOLERANCES:
            append_sensitivity(
                sensitivity,
                [],
                dataset="ADNI",
                branch=branch,
                center="ADNI fixed split",
                cap="not_applicable",
                condition="legacy_archived",
                mode="absolute",
                tolerance=tolerance,
                status="unavailable_missing_candidate_masks",
                note="Medoid selection requires all five feature masks; only the locked mask was archived.",
            )
        append_sensitivity(
            sensitivity,
            [],
            dataset="ADNI",
            branch=branch,
            center="ADNI fixed split",
            cap="not_applicable",
            condition="legacy_archived",
            mode="best_run_se_scaled",
            tolerance="best_run_score_se",
            status="unavailable_missing_fold_scores_and_candidate_masks",
            note="Fold vectors and all five candidate masks were not archived.",
        )
        direct_auc = float(direct["test_auroc_macro"])
        locked_auc = float(locked["test_auroc_macro"])
        for row in compression:
            if row["dataset"] == "ADNI" and row["branch"] == branch:
                if row["selection_rule"] == "Direct":
                    estimate = direct_auc
                    source = "archived source_table_s1 First stage"
                elif row["selected_run"] == locked_run:
                    estimate = locked_auc
                    source = "archived source_table_s1 RFECV+GA; same locked run"
                else:
                    continue
                row.update(
                    {
                        "heldout_metric": "macro OvR AUROC",
                        "heldout_estimate": estimate,
                        "heldout_direct_estimate": direct_auc,
                        "heldout_delta": estimate - direct_auc,
                        "heldout_source": source + "; joined after locking",
                    }
                )
        method_rows = params[params["method"] == method_label]
        rfecv_metric = method_rows.loc[
            (method_rows["stage"] == "RFECV") & (method_rows["parameter"] == "scoring"),
            "resolved_value",
        ].iloc[0]
        ga_metric = method_rows.loc[
            (method_rows["stage"] == "GA-RF") & (method_rows["parameter"] == "fitness_metric"),
            "resolved_value",
        ].iloc[0]
        metrics.append(
            {
                "dataset": "ADNI",
                "branch": branch,
                "center": "ADNI fixed split",
                "cap": "not_applicable",
                "condition": "legacy_archived",
                "rfecv_metric": rfecv_metric,
                "ga_base_score_metric": ga_metric,
                "locking_metric": "balanced_accuracy",
                "heldout_evaluation_metrics": "balanced_accuracy|macro_f1|accuracy|weighted_auroc|macro_auroc",
                "development_metrics_aligned": len({rfecv_metric, ga_metric, "balanced_accuracy"}) == 1,
                "warning": "staged_heuristic_mixed_development_metrics",
                "legacy_configuration": True,
            }
        )


def main() -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    compression: list[dict[str, object]] = []
    sensitivity: list[dict[str, object]] = []
    candidate_audits: list[pd.DataFrame] = []
    penalty: list[dict[str, object]] = []
    metrics: list[dict[str, object]] = []
    source_paths: set[Path] = set()

    build_cgga(compression, sensitivity, candidate_audits, penalty, metrics, source_paths)
    build_ampad(compression, sensitivity, candidate_audits, penalty, metrics, source_paths)
    build_adni(compression, sensitivity, metrics, source_paths)

    outputs = {
        "compression_regret_summary.csv": pd.DataFrame(compression),
        "locking_rule_sensitivity.csv": pd.DataFrame(sensitivity),
        "locking_candidate_audit.csv": pd.concat(candidate_audits, ignore_index=True),
        "penalty_flattening_audit.csv": pd.DataFrame(penalty),
        "metric_alignment_audit.csv": pd.DataFrame(metrics),
    }
    for name, frame in outputs.items():
        frame.to_csv(AUDIT_DIR / name, index=False)

    provenance = {
        "analysis_name": "development-only compression-regret revision",
        "selection_boundary": "No held-out outcome was read before each selection rule was fixed.",
        "preferred_tolerance_rationale": (
            "Absolute tolerance 0.01 is a prespecified conservative development-scale rule; "
            "held-out results were not used to choose it."
        ),
        "software_repo": str(GBM_ROOT),
        "software_version": "0.1.0 working tree",
        "locking_configuration": asdict(
            LockingConfig(
                enabled=True,
                strategy="regret_constrained_medoid",
                tolerance_mode="absolute",
                regret_tolerance=0.01,
                minimum_pool_size=1,
                fallback_rule="strict_eligible_only",
            )
        ),
        "inputs": [
            {"path": str(path), "sha256": sha256(path)}
            for path in sorted(source_paths)
            if path.exists()
        ],
        "missing_inputs": [
            {
                "dataset": "AMP-AD",
                "item": "development-fold score vectors",
                "impact": "best-run-SE-scaled sensitivity not computed",
            },
            {
                "dataset": "ADNI",
                "item": "all five candidate feature masks and fold score vectors",
                "impact": "all-run/regret medoids, Nogueira agreement, and best-run-SE-scaled sensitivity not computed",
            },
        ],
        "outputs": [],
    }
    for name in outputs:
        path = AUDIT_DIR / name
        provenance["outputs"].append(
            {"path": str(path), "rows": len(outputs[name]), "sha256": sha256(path)}
        )
    (AUDIT_DIR / "analysis_provenance.json").write_text(
        json.dumps(provenance, indent=2), encoding="utf-8"
    )
    print(json.dumps({name: len(frame) for name, frame in outputs.items()}, indent=2))


if __name__ == "__main__":
    main()
