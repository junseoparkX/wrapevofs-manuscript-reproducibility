from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
V11 = HERE.parent
ROOT = V11.parents[1]
GBM = ROOT.parent / "gbm_package"
sys.path.insert(0, str(GBM / "src"))

from wrapevofs.selectors.genetic_rf import _stable_mask_hash  # noqa: E402


OUT = V11 / "revision_outputs"
SUPPLEMENTARY_DATA = V11 / "supplementary_data"
TABLE_S16 = SUPPLEMENTARY_DATA / "Table_S16_AMPAD_FourCenter_Objective_Sensitivity.csv"
ORIGINAL_ROOT = (
    ROOT
    / "_codex_tmp"
    / "ampad_20260731_review"
    / "results"
    / "AMPAD_bScore_3class_RFECV_budget_calibration"
)
UPDATED_AUDIT = (
    SUPPLEMENTARY_DATA
    / "recommended_mode_120_run"
    / "authoritative_lock"
    / "candidate_locking_audit.csv"
)
UPDATED_RAW = (
    ROOT
    / "analysis"
    / "remaining90_completed_20260806"
    / "results"
    / "WrapEvoFS_AMPAD_Remaining_90_results"
    / "recommended_untruncated"
)
RUSH_STRICT = ROOT / "outputs" / "AMPAD_Rush_6Condition_Strict_Reaggregation_20260803"
RUSH_RECOVERY = ROOT / "analysis" / "ampad_updated_one_time_heldout_20260808" / "rush_recovery"
SENSITIVITY_SOURCE = ROOT / "locking_rule_sensitivity.csv"
EPSILON = 1e-12


@dataclass(frozen=True)
class Candidate:
    run_id: int
    features: tuple[str, ...]
    score: float
    mask: np.ndarray
    stable_hash: str
    source_run_ids: tuple[int, ...]

    @property
    def count(self) -> int:
        return len(self.features)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cap_key(value: str) -> str:
    value = value.lower()
    if value.startswith("small") or value == "low":
        return "low"
    if value.startswith("reference"):
        return "reference"
    if value.startswith("high"):
        return "high"
    raise ValueError(f"Unknown cap: {value}")


def branch_key(value: str) -> str:
    return value.lower().replace("-", "_")


def center_key(value: str) -> str:
    return value.lower().replace(" ", "_")


def condition_key(center: str, branch: str, cap: str) -> str:
    return f"{center_key(center)}|{branch_key(branch)}|{cap_key(cap)}"


def parse_table_s16() -> pd.DataFrame:
    table = pd.read_csv(TABLE_S16)
    if len(table) != 24:
        raise ValueError(f"Expected 24 Table S16 rows; observed {len(table)}")
    if table["Held-out inputs used"].astype(str).str.lower().ne("false").any():
        raise ValueError("Table S16 unexpectedly reports held-out input use")
    table = table.rename(
        columns={
            "RFECV target": "target",
            "Legacy locked n": "original_count",
            "Recommended locked n": "updated_count",
            "Legacy abs. target deviation": "original_target_deviation",
            "Recommended abs. target deviation": "updated_target_deviation",
            "Legacy all-zero generations": "original_all_zero_generations",
            "Recommended diagnostic all-zero generations": "updated_all_zero_generations",
            "Legacy lock score": "original_lock_score",
            "Recommended lock score": "updated_lock_score",
            "Score difference": "score_difference",
            "Recommended eligible pool size": "updated_pool_size",
            "Recommended selected empirical regret": "updated_regret",
            "Recommended selected mean Jaccard": "updated_mean_jaccard",
        }
    )
    table["center_key"] = table["Center"].map(center_key)
    table["branch_key"] = table["Branch"].map(branch_key)
    table["cap_key"] = table["Cap"].map(cap_key)
    table["condition"] = table.apply(
        lambda row: condition_key(row["Center"], row["Branch"], row["Cap"]), axis=1
    )
    numeric = [
        "target",
        "original_count",
        "updated_count",
        "original_target_deviation",
        "updated_target_deviation",
        "original_all_zero_generations",
        "updated_all_zero_generations",
        "original_lock_score",
        "updated_lock_score",
        "score_difference",
        "updated_pool_size",
        "updated_regret",
        "updated_mean_jaccard",
    ]
    table[numeric] = table[numeric].apply(pd.to_numeric)
    return table


def build_robust_summaries(table: pd.DataFrame) -> None:
    condition_rows = table[
        [
            "condition",
            "Center",
            "Branch",
            "Cap",
            "target",
            "original_count",
            "updated_count",
            "original_target_deviation",
            "updated_target_deviation",
            "original_all_zero_generations",
            "updated_all_zero_generations",
            "original_lock_score",
            "updated_lock_score",
            "score_difference",
            "updated_pool_size",
            "updated_regret",
            "updated_mean_jaccard",
        ]
    ].copy()
    condition_rows["target_deviation_improvement"] = (
        condition_rows["original_target_deviation"]
        - condition_rows["updated_target_deviation"]
    )
    condition_rows["all_zero_improvement"] = (
        condition_rows["original_all_zero_generations"]
        - condition_rows["updated_all_zero_generations"]
    )
    condition_rows["stress_condition"] = condition_rows["condition"].eq(
        "rush|svm_l1|low"
    )
    condition_rows.to_csv(OUT / "S16_CONDITION_LEVEL_PAIRED.csv", index=False)

    rows: list[dict[str, object]] = []
    for scope, subset in (
        ("all_24_conditions", condition_rows),
        ("excluding_rush_svm_l1_small", condition_rows.loc[~condition_rows["stress_condition"]]),
    ):
        for metric, original, updated in (
            (
                "absolute_target_deviation",
                "original_target_deviation",
                "updated_target_deviation",
            ),
            (
                "all_zero_generations",
                "original_all_zero_generations",
                "updated_all_zero_generations",
            ),
        ):
            original_total = float(subset[original].sum())
            updated_total = float(subset[updated].sum())
            improvements = subset[original] - subset[updated]
            rows.append(
                {
                    "scope": scope,
                    "metric": metric,
                    "conditions": len(subset),
                    "original_total": original_total,
                    "updated_total": updated_total,
                    "absolute_reduction": original_total - updated_total,
                    "percent_reduction": (
                        100.0 * (original_total - updated_total) / original_total
                        if original_total
                        else np.nan
                    ),
                    "median_condition_improvement": float(np.median(improvements)),
                    "updated_better": int((subset[updated] < subset[original]).sum()),
                    "unchanged": int((subset[updated] == subset[original]).sum()),
                    "updated_worse": int((subset[updated] > subset[original]).sum()),
                }
            )
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "S16_ROBUST_STRESS_EXCLUDED_SUMMARY.csv", index=False)

    expected = {
        ("all_24_conditions", "absolute_target_deviation"): (216, 137),
        ("excluding_rush_svm_l1_small", "absolute_target_deviation"): (135, 112),
        ("all_24_conditions", "all_zero_generations"): (673, 333),
        ("excluding_rush_svm_l1_small", "all_zero_generations"): (428, 267),
    }
    indexed = summary.set_index(["scope", "metric"])
    for key, totals in expected.items():
        observed = tuple(indexed.loc[key, ["original_total", "updated_total"]].astype(int))
        if observed != totals:
            raise ValueError(f"Robust-summary mismatch for {key}: {observed} != {totals}")


def jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    left_set, right_set = set(left), set(right)
    union = left_set | right_set
    return len(left_set & right_set) / len(union) if union else 1.0


def canonical_means(pool: list[Candidate]) -> dict[int, float]:
    ordered = sorted(pool, key=lambda item: (item.stable_hash, item.run_id))
    means: dict[int, float] = {}
    for candidate in ordered:
        values = [
            jaccard(candidate.features, peer.features)
            for peer in ordered
            if peer.run_id != candidate.run_id
        ]
        means[candidate.run_id] = float(np.mean(values)) if values else np.nan
    return means


def decision_stage(pool: list[Candidate], means: dict[int, float]) -> str:
    if len(pool) == 1:
        return "singleton_direct"
    max_mean = max(means[candidate.run_id] for candidate in pool)
    tied = [candidate for candidate in pool if means[candidate.run_id] == max_mean]
    if len(tied) == 1:
        return "unique_jaccard"
    max_score = max(candidate.score for candidate in tied)
    tied = [candidate for candidate in tied if candidate.score == max_score]
    if len(tied) == 1:
        return "higher_score"
    min_count = min(candidate.count for candidate in tied)
    tied = [candidate for candidate in tied if candidate.count == min_count]
    if len(tied) == 1:
        return "smaller_feature_count"
    min_hash = min(candidate.stable_hash for candidate in tied)
    tied = [candidate for candidate in tied if candidate.stable_hash == min_hash]
    if len(tied) == 1:
        return "stable_mask_hash"
    return "duplicate_provenance_only"


def select(candidates: list[Candidate], rule: str) -> dict[str, object]:
    if not candidates:
        raise ValueError("Candidate bank cannot be empty")
    by_score = sorted(candidates, key=lambda item: (-item.score, item.stable_hash, item.run_id))
    best_score = max(candidate.score for candidate in candidates)
    if rule == "original_top_three":
        pool = by_score[: min(3, len(by_score))]
    elif rule == "regret_constrained":
        pool = [candidate for candidate in candidates if best_score - candidate.score <= 0.01]
    else:
        raise ValueError(rule)
    pool = sorted(pool, key=lambda item: (item.stable_hash, item.run_id))
    means = canonical_means(pool)
    stage = decision_stage(pool, means)
    if len(pool) == 1:
        selected = pool[0]
    elif rule == "original_top_three":
        selected = min(
            pool,
            key=lambda item: (-means[item.run_id], -item.score, item.run_id),
        )
    else:
        order = sorted(
            pool,
            key=lambda item: (
                -means[item.run_id],
                -item.score,
                item.count,
                item.stable_hash,
            ),
        )
        best = order[0]
        scientific_key = (-means[best.run_id], -best.score, best.count, best.stable_hash)
        equivalent = [
            item
            for item in order
            if (-means[item.run_id], -item.score, item.count, item.stable_hash)
            == scientific_key
        ]
        selected = min(equivalent, key=lambda item: item.run_id)
    return {
        "selected": selected,
        "pool": pool,
        "means": means,
        "decision_stage": stage,
        "selected_mean_jaccard": means[selected.run_id],
        "selected_regret": best_score - selected.score,
        "best_score": best_score,
    }


def deduplicate(candidates: list[Candidate]) -> tuple[list[Candidate], float]:
    groups: dict[str, list[Candidate]] = {}
    for candidate in candidates:
        groups.setdefault(candidate.stable_hash, []).append(candidate)
    deduplicated: list[Candidate] = []
    max_score_range = 0.0
    for mask_hash, group in groups.items():
        mask_bytes = {np.asarray(item.mask, dtype=np.uint8).tobytes() for item in group}
        if len(mask_bytes) != 1:
            raise RuntimeError(f"Stable-mask collision in deduplication: {mask_hash}")
        scores = [item.score for item in group]
        max_score_range = max(max_score_range, max(scores) - min(scores))
        representative = min(group, key=lambda item: (-item.score, item.run_id))
        deduplicated.append(
            replace(
                representative,
                source_run_ids=tuple(sorted(item.run_id for item in group)),
            )
        )
    return deduplicated, max_score_range


def load_original_bank(row: pd.Series) -> tuple[list[Candidate], int]:
    directory = (
        ORIGINAL_ROOT
        / row["branch_key"]
        / row["center_key"]
        / row["cap_key"]
        / "ga"
    )
    audit = pd.read_csv(directory / "medoid_locking_audit.csv")
    result = joblib.load(directory / "completed_ga_result.joblib")
    solutions = {int(solution.run_id) + 1: solution for solution in result.top_solutions}
    if set(solutions) != set(audit["run_id"].astype(int)):
        raise ValueError(f"Original run-id mismatch: {directory}")
    candidates: list[Candidate] = []
    for audit_row in audit.itertuples(index=False):
        run_id = int(audit_row.run_id)
        solution = solutions[run_id]
        mask = np.asarray(solution.mask, dtype=np.uint8)
        features = tuple(str(value) for value in solution.selected_features)
        if len(features) != int(audit_row.n_features) or int(mask.sum()) != len(features):
            raise ValueError(f"Original feature-count mismatch: {directory}, run {run_id}")
        candidates.append(
            Candidate(
                run_id=run_id,
                features=features,
                score=float(audit_row.dev_cv_macro_auroc_mean),
                mask=mask,
                stable_hash=_stable_mask_hash(mask),
                source_run_ids=(run_id,),
            )
        )
    historical = int(audit.loc[audit["is_locked_medoid"], "run_id"].iloc[0])
    return candidates, historical


def load_updated_banks() -> dict[str, tuple[list[Candidate], int]]:
    audit = pd.read_csv(UPDATED_AUDIT)
    banks: dict[str, tuple[list[Candidate], int]] = {}
    for keys, group in audit.groupby(["center", "branch", "cap"], sort=True):
        center, branch, cap = (str(value) for value in keys)
        candidates: list[Candidate] = []
        for row in group.itertuples(index=False):
            run_id = int(row.run_id)
            seed = 41 + run_id
            mask_path = UPDATED_RAW / center / branch / cap / f"seed_{seed}" / "run_best_mask.npy"
            mask = np.asarray(np.load(mask_path), dtype=np.uint8)
            observed_hash = _stable_mask_hash(mask)
            if observed_hash != str(row.stable_mask_hash):
                raise ValueError(f"Updated stable-hash mismatch: {mask_path}")
            features = tuple(json.loads(row.canonical_features))
            if int(mask.sum()) != len(features):
                raise ValueError(f"Updated feature-count mismatch: {mask_path}")
            candidates.append(
                Candidate(
                    run_id=run_id,
                    features=features,
                    score=float(row.locking_score),
                    mask=mask,
                    stable_hash=observed_hash,
                    source_run_ids=(run_id,),
                )
            )
        selected = int(group.loc[group["selected"].astype(str).str.lower().eq("true"), "run_id"].iloc[0])
        banks[condition_key(center, branch, cap)] = (candidates, selected)
    rush_summary = pd.read_csv(RUSH_RECOVERY / "recommended_locking_summary.csv")
    for row in rush_summary.itertuples(index=False):
        branch = str(row.branch)
        cap = str(row.cap)
        scores = {int(key): float(value) for key, value in json.loads(row.fixed_development_CV_locking_scores).items()}
        feature_sets = []
        for run_id, seed in enumerate(range(42, 47), start=1):
            path = RUSH_RECOVERY / "all_run_features" / f"{branch}_{cap}_seed{seed}.csv"
            feature_sets.append((run_id, tuple(pd.read_csv(path)["feature"].astype(str))))
        universe = tuple(sorted({feature for _, features in feature_sets for feature in features}))
        candidates = []
        for run_id, features in feature_sets:
            feature_set = set(features)
            mask = np.asarray([feature in feature_set for feature in universe], dtype=np.uint8)
            candidates.append(
                Candidate(
                    run_id=run_id,
                    features=features,
                    score=scores[run_id],
                    mask=mask,
                    stable_hash=_stable_mask_hash(mask),
                    source_run_ids=(run_id,),
                )
            )
        banks[condition_key("Rush", branch, cap)] = (candidates, int(row.selected_run))
    if len(banks) != 24:
        raise ValueError(f"Expected 24 complete updated banks after Rush recovery; observed {len(banks)}")
    return banks


def cross_lock_and_duplicate_audits(table: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    updated_banks = load_updated_banks()
    cross_rows: list[dict[str, object]] = []
    duplicate_rows: list[dict[str, object]] = []
    for _, row in table.iterrows():
        condition = row["condition"]
        original_bank, original_historical = load_original_bank(row)
        for bank_name, candidates, existing_run in (
            ("original_objective", original_bank, original_historical),
            (
                "updated_objective",
                updated_banks.get(condition, (None, None))[0],
                updated_banks.get(condition, (None, None))[1],
            ),
        ):
            for rule in ("original_top_three", "regret_constrained"):
                base = {
                    "condition": condition,
                    "Center": row["Center"],
                    "Branch": row["Branch"],
                    "Cap": row["Cap"],
                    "candidate_bank": bank_name,
                    "locking_rule": rule,
                    "held_out_inputs_used": False,
                }
                if candidates is None:
                    if bank_name == "updated_objective" and rule == "regret_constrained":
                        cross_rows.append(
                            {
                                **base,
                                "status": "summary_only_missing_candidate_masks",
                                "selected_run": np.nan,
                                "selected_feature_count": row["updated_count"],
                                "target_deviation": row["updated_target_deviation"],
                                "locking_score": row["updated_lock_score"],
                                "selected_regret": row["updated_regret"],
                                "eligible_pool_size": row["updated_pool_size"],
                                "selected_mean_jaccard": row["updated_mean_jaccard"],
                                "selected_stable_mask_hash": "",
                                "decision_stage": "unavailable_without_masks",
                                "agrees_with_existing": np.nan,
                            }
                        )
                    else:
                        cross_rows.append(
                            {
                                **base,
                                "status": "unavailable_missing_candidate_masks",
                                "selected_run": np.nan,
                                "selected_feature_count": np.nan,
                                "target_deviation": np.nan,
                                "locking_score": np.nan,
                                "selected_regret": np.nan,
                                "eligible_pool_size": np.nan,
                                "selected_mean_jaccard": np.nan,
                                "selected_stable_mask_hash": "",
                                "decision_stage": "unavailable_without_masks",
                                "agrees_with_existing": np.nan,
                            }
                        )
                    continue
                if not candidates:
                    raise ValueError(f"Empty candidate bank: {condition}, {bank_name}")
                result = select(candidates, rule)
                selected: Candidate = result["selected"]
                expected = (
                    existing_run
                    if (bank_name, rule)
                    in {
                        ("original_objective", "original_top_three"),
                        ("updated_objective", "regret_constrained"),
                    }
                    else None
                )
                cross_rows.append(
                    {
                        **base,
                        "status": "complete_from_saved_candidates",
                        "selected_run": selected.run_id,
                        "selected_feature_count": selected.count,
                        "target_deviation": abs(selected.count - int(row["target"])),
                        "locking_score": selected.score,
                        "selected_regret": result["selected_regret"],
                        "eligible_pool_size": len(result["pool"]),
                        "selected_mean_jaccard": result["selected_mean_jaccard"],
                        "selected_stable_mask_hash": selected.stable_hash,
                        "decision_stage": result["decision_stage"],
                        "agrees_with_existing": (
                            selected.run_id == expected if expected is not None else np.nan
                        ),
                    }
                )

            if candidates is None:
                continue
            primary = select(candidates, "regret_constrained")
            deduplicated, max_score_range = deduplicate(candidates)
            sensitivity = select(deduplicated, "regret_constrained")
            primary_selected: Candidate = primary["selected"]
            sensitivity_selected: Candidate = sensitivity["selected"]
            duplicate_rows.append(
                {
                    "condition": condition,
                    "Center": row["Center"],
                    "Branch": row["Branch"],
                    "Cap": row["Cap"],
                    "candidate_bank": bank_name,
                    "status": "complete_from_saved_candidates",
                    "retained_records": len(candidates),
                    "unique_masks": len(deduplicated),
                    "duplicate_records": len(candidates) - len(deduplicated),
                    "maximum_within_duplicate_score_range": max_score_range,
                    "primary_selected_hash": primary_selected.stable_hash,
                    "deduplicated_selected_hash": sensitivity_selected.stable_hash,
                    "selected_mask_changed": primary_selected.stable_hash
                    != sensitivity_selected.stable_hash,
                    "held_out_inputs_used": False,
                }
            )
        if condition not in updated_banks:
            duplicate_rows.append(
                {
                    "condition": condition,
                    "Center": row["Center"],
                    "Branch": row["Branch"],
                    "Cap": row["Cap"],
                    "candidate_bank": "updated_objective",
                    "status": "unavailable_missing_candidate_masks",
                    "retained_records": np.nan,
                    "unique_masks": np.nan,
                    "duplicate_records": np.nan,
                    "maximum_within_duplicate_score_range": np.nan,
                    "primary_selected_hash": "",
                    "deduplicated_selected_hash": "",
                    "selected_mask_changed": np.nan,
                    "held_out_inputs_used": False,
                }
            )

    cross = pd.DataFrame(cross_rows)
    duplicates = pd.DataFrame(duplicate_rows)
    cross.to_csv(OUT / "CROSS_LOCK_2X2_24_CONDITIONS.csv", index=False)
    duplicates.to_csv(OUT / "DUPLICATE_RETAINED_VS_DEDUPLICATED_SENSITIVITY.csv", index=False)
    if len(cross) != 96:
        raise ValueError(f"Expected 96 cross-lock cells; observed {len(cross)}")
    if int(cross["status"].eq("complete_from_saved_candidates").sum()) != 96:
        raise ValueError("Unexpected number of complete cross-lock cells")
    complete_existing = cross["agrees_with_existing"].notna()
    if not cross.loc[complete_existing, "agrees_with_existing"].astype(bool).all():
        failures = cross.loc[complete_existing & ~cross["agrees_with_existing"].astype(bool)]
        raise ValueError(f"Cross-lock reproduction mismatch:\n{failures}")
    return cross, duplicates


def partial_rush_tie_audit(row: pd.Series) -> dict[str, object]:
    path = RUSH_STRICT / f"locking_audit_{row['branch_key']}_{row['cap_key']}_strict.csv"
    audit = pd.read_csv(path)
    eligible = audit.loc[audit["eligible"].astype(str).str.lower().eq("true")].copy()
    pool_size = len(eligible)
    if pool_size == 1:
        stage = "singleton_direct"
    else:
        max_mean = eligible["mean_jaccard"].max()
        tied = eligible.loc[eligible["mean_jaccard"].eq(max_mean)]
        if len(tied) == 1:
            stage = "unique_jaccard"
        else:
            max_score = tied["locking_score"].max()
            tied = tied.loc[tied["locking_score"].eq(max_score)]
            if len(tied) == 1:
                stage = "higher_score"
            else:
                min_count = tied["feature_count"].min()
                tied = tied.loc[tied["feature_count"].eq(min_count)]
                stage = "smaller_feature_count" if len(tied) == 1 else "unresolved_without_hashes"
    selected = audit.loc[audit["selected"].astype(str).str.lower().eq("true")].iloc[0]
    return {
        "condition": row["condition"],
        "Center": row["Center"],
        "Branch": row["Branch"],
        "Cap": row["Cap"],
        "pool_size": pool_size,
        "pool_category": "1" if pool_size == 1 else ("2" if pool_size == 2 else "3+"),
        "decision_stage": stage,
        "selected_run": int(selected["run_id"]),
        "selected_feature_count": int(selected["feature_count"]),
        "selected_regret": float(selected["absolute_regret"]),
        "stable_hash_available": False,
        "duplicate_multiplicity_available": False,
        "status": (
            "partial_complete_decided_before_hash"
            if stage != "unresolved_without_hashes"
            else "unavailable_final_hash_stage"
        ),
        "held_out_inputs_used": False,
    }


def tie_path_audit(table: pd.DataFrame, cross: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    complete = cross.loc[
        (cross["candidate_bank"] == "updated_objective")
        & (cross["locking_rule"] == "regret_constrained")
        & (cross["status"] == "complete_from_saved_candidates")
    ]
    updated_audit = pd.read_csv(UPDATED_AUDIT)
    for record in complete.itertuples(index=False):
        group = updated_audit.loc[
            (updated_audit["center"] == center_key(record.Center))
            & (updated_audit["branch"] == branch_key(record.Branch))
            & (updated_audit["cap"] == cap_key(record.Cap))
        ]
        pool_size = int(record.eligible_pool_size)
        rows.append(
            {
                "condition": record.condition,
                "Center": record.Center,
                "Branch": record.Branch,
                "Cap": record.Cap,
                "pool_size": pool_size,
                "pool_category": "1" if pool_size == 1 else ("2" if pool_size == 2 else "3+"),
                "decision_stage": record.decision_stage,
                "selected_run": int(record.selected_run),
                "selected_feature_count": int(record.selected_feature_count),
                "selected_regret": float(record.selected_regret),
                "stable_hash_available": True,
                "duplicate_multiplicity_available": True,
                "duplicate_records": int(
                    group["duplicate_mask_multiplicity"].astype(int).sub(1).clip(lower=0).sum()
                ),
                "status": "complete_canonical_mask_audit",
                "held_out_inputs_used": False,
            }
        )
    completed_conditions = set(complete["condition"].astype(str))
    for _, row in table.loc[table["center_key"].eq("rush")].iterrows():
        if str(row["condition"]) not in completed_conditions:
            rows.append(partial_rush_tie_audit(row))
    audit = pd.DataFrame(rows).sort_values(["Center", "Branch", "Cap"])
    if len(audit) != 24:
        raise ValueError(f"Expected 24 tie-path rows; observed {len(audit)}")
    audit.to_csv(OUT / "ELIGIBLE_POOL_TIE_PATH_AUDIT.csv", index=False)

    summaries: list[dict[str, object]] = []
    for field in ("pool_category", "decision_stage", "status"):
        for value, count in audit[field].value_counts(dropna=False).items():
            summaries.append(
                {
                    "summary_field": field,
                    "category": value,
                    "count": int(count),
                    "percentage_of_24": 100.0 * count / 24.0,
                }
            )
    pd.DataFrame(summaries).to_csv(OUT / "ELIGIBLE_POOL_TIE_PATH_SUMMARY.csv", index=False)
    return audit


def corrected_s16() -> None:
    sensitivity = pd.read_csv(SENSITIVITY_SOURCE)
    if sensitivity["selection_used_heldout"].astype(str).str.lower().ne("false").any():
        raise ValueError("S16 sensitivity source unexpectedly used held-out inputs")
    singleton = sensitivity["eligible_pool_size"].eq(1)
    corrected_rows = int(singleton.sum())
    sensitivity.loc[singleton, "selected_mean_jaccard"] = np.nan
    sensitivity.to_csv(SUPPLEMENTARY_DATA / "S16_LOCKING_SENSITIVITY_CORRECTED.csv", index=False)

    absolute = sensitivity.loc[
        sensitivity["status"].eq("complete")
        & sensitivity["tolerance_mode"].eq("absolute")
    ].copy()
    absolute["regret_tolerance"] = pd.to_numeric(absolute["regret_tolerance"])
    summary = (
        absolute.groupby(["dataset", "regret_tolerance"], as_index=False)
        .agg(
            pool_size=("eligible_pool_size", "mean"),
            selected_regret=("absolute_regret", "mean"),
            mean_jaccard=("selected_mean_jaccard", "mean"),
            non_singleton_jaccard_n=("selected_mean_jaccard", "count"),
            conditions=("condition", "count"),
        )
    )
    summary.to_csv(OUT / "S16_LOCKING_SENSITIVITY_PLOT_DATA.csv", index=False)
    correction = {
        "status": "PASS",
        "operation": "definition-consistent singleton presentation correction",
        "singleton_rows_set_to_na": corrected_rows,
        "source_sha256": sha256(SENSITIVITY_SOURCE),
        "held_out_inputs_used": False,
    }
    (OUT / "S16_SINGLETON_CORRECTION_PROVENANCE.json").write_text(
        json.dumps(correction, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def feasibility_summary(cross: pd.DataFrame, duplicates: pd.DataFrame) -> None:
    rows = []
    for keys, group in cross.groupby(["candidate_bank", "locking_rule", "status"], dropna=False):
        bank, rule, status = keys
        rows.append(
            {
                "candidate_bank": bank,
                "locking_rule": rule,
                "status": status,
                "conditions": len(group),
                "reason": (
                    "saved masks, features, and fixed development-CV locking scores available"
                    if status == "complete_from_saved_candidates"
                    else "Rush updated candidate masks are absent from the current workspace"
                ),
            }
        )
    pd.DataFrame(rows).to_csv(OUT / "CROSS_LOCK_FEASIBILITY.csv", index=False)
    duplicate_summary = (
        duplicates.groupby(["candidate_bank", "status"], dropna=False)
        .agg(
            conditions=("condition", "count"),
            conditions_with_duplicates=("duplicate_records", lambda values: int((values.fillna(0) > 0).sum())),
            selected_mask_changes=("selected_mask_changed", lambda values: int(values.fillna(False).astype(bool).sum())),
        )
        .reset_index()
    )
    duplicate_summary.to_csv(OUT / "DUPLICATE_SENSITIVITY_SUMMARY.csv", index=False)

    complete = cross.loc[cross["status"].eq("complete_from_saved_candidates")].copy()
    cell_summary = (
        complete.groupby(["candidate_bank", "locking_rule"], as_index=False)
        .agg(
            conditions=("condition", "count"),
            total_target_deviation=("target_deviation", "sum"),
            mean_selected_count=("selected_feature_count", "mean"),
            mean_locking_score=("locking_score", "mean"),
            mean_selected_regret=("selected_regret", "mean"),
            maximum_selected_regret=("selected_regret", "max"),
        )
    )
    selected = complete.pivot_table(
        index=["condition", "candidate_bank"],
        columns="locking_rule",
        values="selected_stable_mask_hash",
        aggfunc="first",
    ).reset_index()
    changes = (
        selected.assign(
            selected_mask_changed=lambda frame: frame["original_top_three"]
            != frame["regret_constrained"]
        )
        .groupby("candidate_bank", as_index=False)
        .agg(
            conditions_with_both_rules=("condition", "count"),
            selected_mask_changes_between_rules=("selected_mask_changed", "sum"),
        )
    )
    cell_summary = cell_summary.merge(changes, on="candidate_bank", how="left")
    cell_summary.to_csv(OUT / "CROSS_LOCK_2X2_SUMMARY.csv", index=False)


def write_provenance() -> None:
    inputs = [TABLE_S16, UPDATED_AUDIT, SENSITIVITY_SOURCE]
    provenance = {
        "operation": "existing-artifact-only V11 reviewer analyses",
        "ga_rerun": False,
        "rfecv_rerun": False,
        "direct_selection_rerun": False,
        "held_out_inputs_used": False,
        "stable_hash_rule": "authoritative package _stable_mask_hash; not redesigned",
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in inputs},
        "rush_updated_recovery": (
            "All 30 Rush run-best feature lists were recovered from the authoritative Drive source folder. "
            "The reconstructed sorted-union universe is used only for deterministic mask encoding; no Rush "
            "selection reached the stable-hash tie stage, and all current selections match the frozen evaluation."
        ),
    }
    (OUT / "V11_EXISTING_ARTIFACT_ANALYSIS_PROVENANCE.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    table = parse_table_s16()
    build_robust_summaries(table)
    corrected_s16()
    cross, duplicates = cross_lock_and_duplicate_audits(table)
    tie_path_audit(table, cross)
    feasibility_summary(cross, duplicates)
    write_provenance()
    print(
        json.dumps(
            {
                "status": "PASS",
                "table_s16_conditions": len(table),
                "cross_lock_cells": len(cross),
                "complete_cross_lock_cells": int(
                    cross["status"].eq("complete_from_saved_candidates").sum()
                ),
                "held_out_inputs_used": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
