"""Summarize completed recommended-objective artifacts without model fitting."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


KEYS = ["center", "branch", "cap"]


def parse_count(value: object) -> int:
    return int(str(value).split("/")[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--authoritative-condition-inventory", type=Path, required=True)
    parser.add_argument("--legacy-audit", type=Path, required=True)
    parser.add_argument("--rush-table", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    config = json.loads(args.config.read_text(encoding="utf-8"))
    condition_config = {
        (row["center"], row["branch"], row["cap"]): row
        for row in config["conditions"]
    }

    run_rows: list[dict[str, object]] = []
    for key in sorted(condition_config):
        center, branch, cap = key
        for run_id, seed in enumerate(range(42, 47), start=1):
            run_dir = (
                args.results_root
                / "recommended_untruncated"
                / center
                / branch
                / cap
                / f"seed_{seed}"
            )
            result = json.loads((run_dir / "run_result.json").read_text(encoding="utf-8"))
            history = pd.read_csv(run_dir / "history.csv")
            run_best_legacy_zero = float(result["diagnostic legacy-truncated run-best fitness"]) == 0.0
            run_rows.append(
                {
                    "center": center,
                    "branch": branch,
                    "cap": cap,
                    "run_id": run_id,
                    "seed": seed,
                    "rfecv_target": int(result["RFECV target"]),
                    "run_best_feature_count": int(result["run-best selected feature count"]),
                    "run_best_absolute_target_deviation": int(result["target deviation"]),
                    "base_development_cv_balanced_accuracy": float(
                        result["base development-CV score"]
                    ),
                    "raw_untruncated_objective": float(result["raw untruncated objective"]),
                    "diagnostic_legacy_truncated_run_best_fitness": float(
                        result["diagnostic legacy-truncated run-best fitness"]
                    ),
                    "diagnostic_zero_legacy_run_best": run_best_legacy_zero,
                    "diagnostic_all_zero_legacy_fitness_generations": int(
                        result["diagnostic all-zero-legacy-fitness generations"]
                    ),
                    "actual_uniform_sampling_fallback_generations": int(
                        result["uniform-sampling fallback generations"]
                    ),
                    "mean_population_unique_masks": float(
                        result["population-mask diversity summary"]["mean_unique_masks"]
                    ),
                    "minimum_population_unique_masks": int(
                        result["population-mask diversity summary"]["minimum_unique_masks"]
                    ),
                    "final_population_unique_masks": int(
                        result["population-mask diversity summary"]["final_unique_masks"]
                    ),
                    "stable_feature_set_identifier": result["stable feature-set identifier"],
                    "runtime_seconds": float(result["runtime seconds"]),
                    "history_generations": int(len(history)),
                    "python_version": result["python version"],
                    "numpy_version": result["numpy version"],
                    "pandas_version": result["pandas version"],
                    "scikit_learn_version": result["scikit-learn version"],
                    "backend": result["backend"],
                    "objective_mode": result["objective mode"],
                    "held_out_inputs_used": bool(result["held-out inputs used"]),
                }
            )
    runs = pd.DataFrame(run_rows)
    if len(runs) != 90:
        raise AssertionError(f"Expected 90 runs, found {len(runs)}")
    if set(runs["history_generations"]) != {50}:
        raise AssertionError("Every completed history must contain 50 generations")

    locked = pd.read_csv(args.authoritative_condition_inventory)
    condition_rows: list[dict[str, object]] = []
    for _, lock in locked.iterrows():
        key = (lock["center"], lock["branch"], lock["cap"])
        subset = runs[
            (runs["center"] == key[0])
            & (runs["branch"] == key[1])
            & (runs["cap"] == key[2])
        ]
        selected_run_id = int(lock["selected_run_id"])
        selected_run = subset[subset["run_id"] == selected_run_id].iloc[0]
        condition_rows.append(
            {
                **{column: lock[column] for column in locked.columns},
                "selected_absolute_target_deviation": abs(
                    int(lock["selected_feature_count"]) - int(lock["rfecv_target"])
                ),
                "run_best_absolute_target_deviation_sum": int(
                    subset["run_best_absolute_target_deviation"].sum()
                ),
                "run_best_absolute_target_deviation_mean": float(
                    subset["run_best_absolute_target_deviation"].mean()
                ),
                "exact_target_runs": int(
                    (subset["run_best_absolute_target_deviation"] == 0).sum()
                ),
                "diagnostic_zero_legacy_run_best_count": int(
                    subset["diagnostic_zero_legacy_run_best"].sum()
                ),
                "diagnostic_all_zero_legacy_fitness_generations": int(
                    subset["diagnostic_all_zero_legacy_fitness_generations"].sum()
                ),
                "actual_uniform_sampling_fallback_generations": int(
                    subset["actual_uniform_sampling_fallback_generations"].sum()
                ),
                "unique_run_best_masks": int(subset["stable_feature_set_identifier"].nunique()),
                "condition_runtime_seconds": float(subset["runtime_seconds"].sum()),
                "selected_run_raw_untruncated_objective": float(
                    selected_run["raw_untruncated_objective"]
                ),
            }
        )
    conditions = pd.DataFrame(condition_rows)

    legacy = pd.read_csv(args.legacy_audit)
    legacy = legacy[
        (legacy["dataset"] == "AMP-AD")
        & (legacy["condition"] == "legacy_zero_truncated")
        & (legacy["center"].isin(["emory", "mayo", "mount_sinai"]))
        & (legacy["cap"].isin(["low", "reference"]))
    ].copy()
    if len(legacy) != 18:
        raise AssertionError(f"Expected 18 matched legacy conditions, found {len(legacy)}")
    legacy = legacy.rename(
        columns={
            "target_count": "legacy_target_count",
            "selected_count": "legacy_locked_feature_count",
            "target_deviation": "legacy_absolute_target_deviation",
            "fraction_zero_legacy_fitness": "legacy_zero_run_best_fraction",
            "number_all_zero_generations": "legacy_all_zero_generations",
            "number_uniform_sampling_fallbacks": "legacy_uniform_sampling_fallbacks",
            "final_development_score": "legacy_locking_score",
            "selected_run": "legacy_selected_run_id",
        }
    )
    comparison = conditions.merge(
        legacy[
            KEYS
            + [
                "legacy_target_count",
                "legacy_locked_feature_count",
                "legacy_absolute_target_deviation",
                "legacy_zero_run_best_fraction",
                "legacy_all_zero_generations",
                "legacy_uniform_sampling_fallbacks",
                "legacy_locking_score",
                "legacy_selected_run_id",
            ]
        ],
        on=KEYS,
        how="left",
        validate="one_to_one",
    )
    comparison["legacy_zero_run_best_count"] = (
        comparison["legacy_zero_run_best_fraction"] * 5
    ).round().astype(int)
    comparison["locking_score_difference_recommended_minus_legacy"] = (
        comparison["selected_locking_score"] - comparison["legacy_locking_score"]
    )
    comparison["target_deviation_change_recommended_minus_legacy"] = (
        comparison["selected_absolute_target_deviation"]
        - comparison["legacy_absolute_target_deviation"]
    )

    center_summary = (
        comparison.groupby("center", as_index=False)
        .agg(
            conditions=("cap", "size"),
            legacy_locked_absolute_target_deviation=("legacy_absolute_target_deviation", "sum"),
            recommended_locked_absolute_target_deviation=("selected_absolute_target_deviation", "sum"),
            legacy_zero_run_best_count=("legacy_zero_run_best_count", "sum"),
            recommended_zero_run_best_count=("diagnostic_zero_legacy_run_best_count", "sum"),
            legacy_all_zero_generations=("legacy_all_zero_generations", "sum"),
            recommended_all_zero_generations=(
                "diagnostic_all_zero_legacy_fitness_generations",
                "sum",
            ),
            recommended_actual_uniform_fallbacks=(
                "actual_uniform_sampling_fallback_generations",
                "sum",
            ),
            recommended_runtime_seconds=("condition_runtime_seconds", "sum"),
            mean_locking_score_difference=(
                "locking_score_difference_recommended_minus_legacy",
                "mean",
            ),
        )
    )
    branch_summary = (
        comparison.groupby("branch", as_index=False)
        .agg(
            conditions=("cap", "size"),
            legacy_locked_absolute_target_deviation=("legacy_absolute_target_deviation", "sum"),
            recommended_locked_absolute_target_deviation=("selected_absolute_target_deviation", "sum"),
            legacy_zero_run_best_count=("legacy_zero_run_best_count", "sum"),
            recommended_zero_run_best_count=("diagnostic_zero_legacy_run_best_count", "sum"),
            legacy_all_zero_generations=("legacy_all_zero_generations", "sum"),
            recommended_all_zero_generations=(
                "diagnostic_all_zero_legacy_fitness_generations",
                "sum",
            ),
            recommended_actual_uniform_fallbacks=(
                "actual_uniform_sampling_fallback_generations",
                "sum",
            ),
            mean_locking_score_difference=(
                "locking_score_difference_recommended_minus_legacy",
                "mean",
            ),
        )
    )

    rush = pd.read_csv(args.rush_table)
    proposed_nonrush_table = pd.DataFrame(
        {
            "Center": comparison["center"].replace(
                {"emory": "Emory", "mayo": "Mayo", "mount_sinai": "Mount Sinai"}
            ),
            "Branch": comparison["branch"].replace(
                {"svm_l1": "SVM-L1", "xgboost": "XGBoost", "boruta_rf": "Boruta-RF"}
            ),
            "Cap": comparison["cap"].replace(
                {"low": "Small-cap", "reference": "Reference-cap"}
            ),
            "RFECV target": comparison["rfecv_target"].astype(int),
            "Legacy locked n": comparison["legacy_locked_feature_count"].astype(int),
            "Recommended locked n": comparison["selected_feature_count"].astype(int),
            "Legacy abs. target deviation": comparison[
                "legacy_absolute_target_deviation"
            ].astype(int),
            "Recommended abs. target deviation": comparison[
                "selected_absolute_target_deviation"
            ].astype(int),
            "Legacy zero run-best fitness, n/5": comparison[
                "legacy_zero_run_best_count"
            ].astype(str)
            + "/5",
            "Recommended diagnostic zero legacy fitness, n/5": comparison[
                "diagnostic_zero_legacy_run_best_count"
            ].astype(str)
            + "/5",
            "Legacy all-zero generations": comparison["legacy_all_zero_generations"].astype(int),
            "Recommended diagnostic all-zero generations": comparison[
                "diagnostic_all_zero_legacy_fitness_generations"
            ].astype(int),
            "Legacy lock score": comparison["legacy_locking_score"].astype(float),
            "Recommended lock score": comparison["selected_locking_score"].astype(float),
            "Score difference": comparison[
                "locking_score_difference_recommended_minus_legacy"
            ].astype(float),
            "Recommended eligible pool size": comparison["eligible_pool_size"].astype(int),
            "Recommended selected empirical regret": comparison[
                "selected_absolute_regret"
            ].astype(float),
            "Recommended selected mean Jaccard": comparison[
                "selected_mean_jaccard"
            ].astype(float),
            "Recommended uniform fallbacks": comparison[
                "actual_uniform_sampling_fallback_generations"
            ].astype(int),
            "Held-out inputs used": False,
            "Locking implementation note": "current authoritative stable-mask-hash package rule",
        }
    )
    proposed_rush_table = pd.DataFrame(
        {
            "Center": "Rush",
            "Branch": rush["Branch"],
            "Cap": rush["Cap"],
            "RFECV target": rush["RFECV target"].astype(int),
            "Legacy locked n": rush["Legacy locked n"].astype(int),
            "Recommended locked n": rush["Recommended locked n"].astype(int),
            "Legacy abs. target deviation": rush[
                "Legacy abs. target deviation"
            ].astype(int),
            "Recommended abs. target deviation": rush[
                "Recommended abs. target deviation"
            ].astype(int),
            "Legacy zero run-best fitness, n/5": rush[
                "Legacy zero run-best fitness, n/5"
            ],
            "Recommended diagnostic zero legacy fitness, n/5": rush[
                "Recommended diagnostic zero legacy fitness, n/5"
            ],
            "Legacy all-zero generations": rush["Legacy all-zero generations"].astype(int),
            "Recommended diagnostic all-zero generations": rush[
                "Recommended diagnostic all-zero legacy-fitness generations"
            ].astype(int),
            "Legacy lock score": rush["Legacy lock score"].astype(float),
            "Recommended lock score": rush["Recommended lock score"].astype(float),
            "Score difference": rush["Score difference"].astype(float),
            "Recommended eligible pool size": rush["Strict eligible run IDs"].map(
                lambda value: len(json.loads(str(value)))
            ),
            "Recommended selected empirical regret": rush["Selected empirical regret"].astype(float),
            "Recommended selected mean Jaccard": pd.to_numeric(
                rush["Recommended selected mean Jaccard"], errors="coerce"
            ),
            "Recommended uniform fallbacks": rush["Recommended uniform fallbacks"].astype(int),
            "Held-out inputs used": False,
            "Locking implementation note": (
                "archived report label obsolete; selection did not reach final tie-break"
            ),
        }
    )
    proposed_table_s16 = pd.concat(
        [proposed_nonrush_table, proposed_rush_table], ignore_index=True
    ).sort_values(["Center", "Branch", "Cap"], kind="stable")
    rush_standard = pd.DataFrame(
        {
            "center": "rush",
            "branch": rush["Branch"].str.lower().replace({"svm-l1": "svm_l1", "boruta-rf": "boruta_rf"}),
            "cap": rush["Cap"].replace({"Small-cap": "low", "Reference-cap": "reference"}),
            "legacy_absolute_target_deviation": rush["Legacy abs. target deviation"].astype(int),
            "recommended_absolute_target_deviation": rush[
                "Recommended abs. target deviation"
            ].astype(int),
            "legacy_zero_run_best_count": rush["Legacy zero run-best fitness, n/5"].map(parse_count),
            "recommended_zero_run_best_count": rush[
                "Recommended diagnostic zero legacy fitness, n/5"
            ].map(parse_count),
            "legacy_all_zero_generations": rush["Legacy all-zero generations"].astype(int),
            "recommended_all_zero_generations": rush[
                "Recommended diagnostic all-zero legacy-fitness generations"
            ].astype(int),
            "recommended_actual_uniform_fallbacks": rush[
                "Recommended uniform fallbacks"
            ].astype(int),
            "legacy_locking_score": rush["Legacy lock score"].astype(float),
            "recommended_locking_score": rush["Recommended lock score"].astype(float),
            "locking_score_difference_recommended_minus_legacy": rush["Score difference"].astype(float),
            "recommended_runtime_seconds": rush["Recommended runtime"].astype(float),
            "locking_rule_status": (
                "selection unaffected by final tie-break; archived report label is obsolete"
            ),
        }
    )
    nonrush_standard = pd.DataFrame(
        {
            "center": comparison["center"],
            "branch": comparison["branch"],
            "cap": comparison["cap"],
            "legacy_absolute_target_deviation": comparison[
                "legacy_absolute_target_deviation"
            ].astype(int),
            "recommended_absolute_target_deviation": comparison[
                "selected_absolute_target_deviation"
            ].astype(int),
            "legacy_zero_run_best_count": comparison["legacy_zero_run_best_count"].astype(int),
            "recommended_zero_run_best_count": comparison[
                "diagnostic_zero_legacy_run_best_count"
            ].astype(int),
            "legacy_all_zero_generations": comparison["legacy_all_zero_generations"].astype(int),
            "recommended_all_zero_generations": comparison[
                "diagnostic_all_zero_legacy_fitness_generations"
            ].astype(int),
            "recommended_actual_uniform_fallbacks": comparison[
                "actual_uniform_sampling_fallback_generations"
            ].astype(int),
            "legacy_locking_score": comparison["legacy_locking_score"].astype(float),
            "recommended_locking_score": comparison["selected_locking_score"].astype(float),
            "locking_score_difference_recommended_minus_legacy": comparison[
                "locking_score_difference_recommended_minus_legacy"
            ].astype(float),
            "recommended_runtime_seconds": comparison["condition_runtime_seconds"].astype(float),
            "locking_rule_status": "current authoritative stable-mask-hash rule applied",
        }
    )
    all_centers = pd.concat([nonrush_standard, rush_standard], ignore_index=True)

    overall = {
        "remaining90": {
            "runs_complete": int(len(runs)),
            "conditions": int(len(conditions)),
            "generations": int(runs["history_generations"].sum()),
            "held_out_inputs_used_any": bool(runs["held_out_inputs_used"].any()),
            "run_best_target_deviation_sum": int(
                runs["run_best_absolute_target_deviation"].sum()
            ),
            "run_best_target_deviation_mean": float(
                runs["run_best_absolute_target_deviation"].mean()
            ),
            "run_best_target_deviation_median": float(
                runs["run_best_absolute_target_deviation"].median()
            ),
            "run_best_target_deviation_min": int(
                runs["run_best_absolute_target_deviation"].min()
            ),
            "run_best_target_deviation_max": int(
                runs["run_best_absolute_target_deviation"].max()
            ),
            "exact_target_runs": int((runs["run_best_absolute_target_deviation"] == 0).sum()),
            "within_one_target_runs": int(
                (runs["run_best_absolute_target_deviation"] <= 1).sum()
            ),
            "diagnostic_zero_legacy_run_best_count": int(
                runs["diagnostic_zero_legacy_run_best"].sum()
            ),
            "diagnostic_all_zero_legacy_fitness_generations": int(
                runs["diagnostic_all_zero_legacy_fitness_generations"].sum()
            ),
            "actual_uniform_sampling_fallback_generations": int(
                runs["actual_uniform_sampling_fallback_generations"].sum()
            ),
            "runtime_seconds": float(runs["runtime_seconds"].sum()),
            "runtime_gpu_hours": float(runs["runtime_seconds"].sum() / 3600.0),
            "locked_target_deviation_sum": int(
                conditions["selected_absolute_target_deviation"].sum()
            ),
            "legacy_matched_locked_target_deviation_sum": int(
                comparison["legacy_absolute_target_deviation"].sum()
            ),
            "maximum_selected_empirical_regret": float(
                conditions["selected_absolute_regret"].max()
            ),
            "eligible_pool_size_min": int(conditions["eligible_pool_size"].min()),
            "eligible_pool_size_max": int(conditions["eligible_pool_size"].max()),
            "singleton_eligible_pools": int((conditions["eligible_pool_size"] == 1).sum()),
            "conditions_with_duplicate_run_best_masks": int(
                (conditions["unique_run_best_masks"] < 5).sum()
            ),
            "locking_score_difference_mean": float(
                comparison["locking_score_difference_recommended_minus_legacy"].mean()
            ),
            "locking_score_difference_median": float(
                comparison["locking_score_difference_recommended_minus_legacy"].median()
            ),
            "locking_score_difference_min": float(
                comparison["locking_score_difference_recommended_minus_legacy"].min()
            ),
            "locking_score_difference_max": float(
                comparison["locking_score_difference_recommended_minus_legacy"].max()
            ),
            "target_deviation_improved_conditions": int(
                (comparison["target_deviation_change_recommended_minus_legacy"] < 0).sum()
            ),
            "target_deviation_unchanged_conditions": int(
                (comparison["target_deviation_change_recommended_minus_legacy"] == 0).sum()
            ),
            "target_deviation_worsened_conditions": int(
                (comparison["target_deviation_change_recommended_minus_legacy"] > 0).sum()
            ),
        },
        "all_four_centers_small_reference": {
            "runs": 120,
            "conditions": int(len(all_centers)),
            "legacy_locked_target_deviation_sum": int(
                all_centers["legacy_absolute_target_deviation"].sum()
            ),
            "recommended_locked_target_deviation_sum": int(
                all_centers["recommended_absolute_target_deviation"].sum()
            ),
            "legacy_zero_run_best_count": int(
                all_centers["legacy_zero_run_best_count"].sum()
            ),
            "recommended_zero_run_best_count": int(
                all_centers["recommended_zero_run_best_count"].sum()
            ),
            "legacy_all_zero_generations": int(
                all_centers["legacy_all_zero_generations"].sum()
            ),
            "recommended_all_zero_generations": int(
                all_centers["recommended_all_zero_generations"].sum()
            ),
            "recommended_actual_uniform_fallbacks": int(
                all_centers["recommended_actual_uniform_fallbacks"].sum()
            ),
            "recommended_runtime_gpu_hours": float(
                all_centers["recommended_runtime_seconds"].sum() / 3600.0
            ),
            "locking_score_difference_mean": float(
                all_centers["locking_score_difference_recommended_minus_legacy"].mean()
            ),
            "locking_score_difference_median": float(
                all_centers["locking_score_difference_recommended_minus_legacy"].median()
            ),
            "locking_score_difference_min": float(
                all_centers["locking_score_difference_recommended_minus_legacy"].min()
            ),
            "locking_score_difference_max": float(
                all_centers["locking_score_difference_recommended_minus_legacy"].max()
            ),
        },
    }

    outputs = {
        "remaining90_run_level_summary.csv": runs,
        "remaining90_condition_level_summary.csv": conditions,
        "remaining90_legacy_vs_recommended.csv": comparison,
        "remaining90_center_summary.csv": center_summary,
        "remaining90_branch_summary.csv": branch_summary,
        "all_four_centers_small_reference_comparison.csv": all_centers,
        "proposed_table_s16_24_conditions.csv": proposed_table_s16,
    }
    for filename, frame in outputs.items():
        frame.to_csv(args.output_dir / filename, index=False)
    (args.output_dir / "analysis_summary.json").write_text(
        json.dumps(overall, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(overall, indent=2))


if __name__ == "__main__":
    main()
