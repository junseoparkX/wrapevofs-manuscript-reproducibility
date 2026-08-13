"""Reapply the authoritative package locking rule to frozen development scores.

This adapter does not fit or evaluate any model.  It reads the five-fold
development scores produced by the completed lock-freeze pass and calls the
current WrapEvoFS package implementation for candidate validation, strict
regret eligibility, Jaccard-medoid selection, and stable-mask-hash tie-breaking.
"""

from __future__ import annotations

import argparse
import hashlib
from itertools import permutations
import json
from pathlib import Path
import sys

import pandas as pd


CONDITION_KEYS = ["center", "branch", "cap"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_features(path: Path) -> list[str]:
    frame = pd.read_csv(path)
    if list(frame.columns) != ["feature"]:
        raise ValueError(f"Expected one 'feature' column in {path}")
    values = frame["feature"].astype(str).tolist()
    if not values or len(values) != len(set(values)):
        raise ValueError(f"Feature list must be nonempty and unique: {path}")
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--frozen-scores", type=Path, required=True)
    parser.add_argument("--bundle-condition-inventory", type=Path, required=True)
    parser.add_argument("--package-src", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    results_root = args.results_root.resolve()
    config_path = args.config.resolve()
    frozen_scores_path = args.frozen_scores.resolve()
    bundle_inventory_path = args.bundle_condition_inventory.resolve()
    package_src = args.package_src.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(package_src))
    from wrapevofs.config import LockingConfig
    from wrapevofs.locking import LockingCandidate, lock_representative_run

    config = json.loads(config_path.read_text(encoding="utf-8"))
    condition_config = {
        (row["center"], row["branch"], row["cap"]): row
        for row in config["conditions"]
    }
    frozen_scores = pd.read_csv(frozen_scores_path)
    bundle_inventory = pd.read_csv(bundle_inventory_path)
    archive_root = repo_root / config["paths"]["archive_root"]

    lock_config = LockingConfig(
        enabled=True,
        strategy="regret_constrained_medoid",
        tolerance_mode="absolute",
        regret_tolerance=0.01,
        minimum_pool_size=1,
        fallback_rule="strict_eligible_only",
        tie_breakers=[
            "higher_locking_score",
            "smaller_feature_count",
            "stable_mask_hash",
        ],
        metric_orientation="larger_is_better",
        locking_metric="macro_ovr_auroc",
        cv_folds=5,
        random_state=42,
    )

    audit_frames: list[pd.DataFrame] = []
    pairwise_frames: list[pd.DataFrame] = []
    condition_rows: list[dict[str, object]] = []
    comparison_rows: list[dict[str, object]] = []
    stable_id_checks: list[dict[str, object]] = []
    permutation_checks: list[dict[str, object]] = []

    for key in sorted(condition_config):
        center, branch, cap = key
        condition = condition_config[key]
        shared_root = archive_root / branch / center / "shared"
        universe_path = shared_root / "first_stage_selected_features.csv"
        candidate_universe = read_features(universe_path)

        score_subset = frozen_scores[
            (frozen_scores["center"] == center)
            & (frozen_scores["branch"] == branch)
            & (frozen_scores["cap"] == cap)
        ].copy()
        if len(score_subset) != 25:
            raise ValueError(f"Expected 25 frozen fold scores for {key}, got {len(score_subset)}")

        candidates: list[LockingCandidate] = []
        run_result_by_id: dict[int, dict[str, object]] = {}
        for run_id in range(1, 6):
            run_seed = 41 + run_id
            run_dir = (
                results_root
                / "recommended_untruncated"
                / center
                / branch
                / cap
                / f"seed_{run_seed}"
            )
            selected_features = read_features(run_dir / "run_best_features.csv")
            fold_rows = score_subset[score_subset["run_id"] == run_id].sort_values("fold")
            if fold_rows["fold"].tolist() != [1, 2, 3, 4, 5]:
                raise ValueError(f"Unexpected fold identities for {key}, run {run_id}")
            fold_scores = tuple(float(value) for value in fold_rows["locking_score"])
            run_result = json.loads((run_dir / "run_result.json").read_text(encoding="utf-8"))
            run_result_by_id[run_id] = run_result
            candidates.append(
                LockingCandidate(
                    run_id=run_id,
                    features=selected_features,
                    locking_score=sum(fold_scores) / len(fold_scores),
                    fold_locking_scores=fold_scores,
                    seed=run_seed,
                    candidate_universe=candidate_universe,
                )
            )

        lock = lock_representative_run(
            candidates,
            lock_config,
            full_configuration=config,
            seeds={"cv_random_state": 42, "run_model_seed_rule": "42 + run_id_one_based"},
        )
        permutation_hashes: set[str] = set()
        audit_matches = True
        pairwise_matches = True
        metadata_matches = True
        permutations_tested = 0
        for candidate_order in permutations(candidates):
            permuted = lock_representative_run(
                list(candidate_order),
                lock_config,
                full_configuration=config,
                seeds={
                    "cv_random_state": 42,
                    "run_model_seed_rule": "42 + run_id_one_based",
                },
            )
            permutations_tested += 1
            permutation_hashes.add(str(permuted.metadata["selected_stable_mask_hash"]))
            audit_matches = audit_matches and permuted.candidate_audit.equals(
                lock.candidate_audit
            )
            pairwise_matches = pairwise_matches and permuted.pairwise_jaccard.equals(
                lock.pairwise_jaccard
            )
            metadata_matches = metadata_matches and permuted.metadata == lock.metadata
        permutation_checks.append(
            {
                "center": center,
                "branch": branch,
                "cap": cap,
                "permutations_tested": permutations_tested,
                "unique_selected_feature_sets": len(permutation_hashes),
                "candidate_audit_identical": audit_matches,
                "pairwise_audit_identical": pairwise_matches,
                "metadata_identical": metadata_matches,
                "passed": (
                    len(permutation_hashes) == 1
                    and audit_matches
                    and pairwise_matches
                    and metadata_matches
                ),
            }
        )
        audit = lock.candidate_audit.copy()
        audit.insert(0, "cap", cap)
        audit.insert(0, "branch", branch)
        audit.insert(0, "center", center)
        audit_frames.append(audit)

        pairwise = lock.pairwise_jaccard.copy()
        pairwise.insert(0, "cap", cap)
        pairwise.insert(0, "branch", branch)
        pairwise.insert(0, "center", center)
        pairwise_frames.append(pairwise)

        for _, row in audit.iterrows():
            run_id = int(row["run_id"])
            archived_stable_id = str(run_result_by_id[run_id]["stable feature-set identifier"])
            stable_id_checks.append(
                {
                    "center": center,
                    "branch": branch,
                    "cap": cap,
                    "run_id": run_id,
                    "seed": 41 + run_id,
                    "archived_stable_feature_set_identifier": archived_stable_id,
                    "authoritative_stable_mask_hash": row["stable_mask_hash"],
                    "match": archived_stable_id == row["stable_mask_hash"],
                }
            )

        selected_row = audit[audit["selected"]].iloc[0]
        selected_set_rows = audit[audit["selected_feature_set"]]
        if not bool(lock.metadata["selected_within_declared_tolerance"]):
            raise AssertionError(f"Regret constraint failed for {key}")
        if float(lock.metadata["selected_absolute_regret"]) > 0.01:
            raise AssertionError(f"Selected regret exceeded 0.01 for {key}")

        bundle_row = bundle_inventory[
            (bundle_inventory["center"] == center)
            & (bundle_inventory["branch"] == branch)
            & (bundle_inventory["cap"] == cap)
        ].iloc[0]
        bundle_run_id = int(bundle_row["selected_run_id"])
        bundle_hash = str(audit.loc[audit["run_id"] == bundle_run_id, "stable_mask_hash"].iloc[0])
        authoritative_hash = str(lock.metadata["selected_stable_mask_hash"])
        comparison_rows.append(
            {
                "center": center,
                "branch": branch,
                "cap": cap,
                "bundle_selected_run_id": bundle_run_id,
                "bundle_selected_stable_mask_hash": bundle_hash,
                "authoritative_selected_run_id": int(lock.selected_run_id),
                "authoritative_selected_stable_mask_hash": authoritative_hash,
                "same_source_run": bundle_run_id == int(lock.selected_run_id),
                "same_scientific_feature_set": bundle_hash == authoritative_hash,
            }
        )
        condition_rows.append(
            {
                "center": center,
                "branch": branch,
                "cap": cap,
                "rfecv_target": int(condition["rfecv_target"]),
                "selected_run_id": int(lock.selected_run_id),
                "selected_seed": 41 + int(lock.selected_run_id),
                "selected_source_run_ids": json.dumps(lock.metadata["selected_source_run_ids"]),
                "selected_feature_count": len(lock.selected_features),
                "selected_locking_score": float(selected_row["locking_score"]),
                "selected_absolute_regret": float(lock.metadata["selected_absolute_regret"]),
                "eligible_pool_size": len(lock.metadata["eligible_run_ids"]),
                "eligible_run_ids": json.dumps(lock.metadata["eligible_run_ids"]),
                "selected_mean_jaccard": float(selected_row["mean_jaccard"])
                if pd.notna(selected_row["mean_jaccard"])
                else None,
                "selected_stable_mask_hash": authoritative_hash,
                "selected_duplicate_multiplicity": int(len(selected_set_rows)),
                "tie_break_path": lock.metadata["tie_break_path"],
                "duplicate_mask_policy": lock.metadata["duplicate_mask_policy"],
                "candidate_universe_sha256": lock.metadata["candidate_universe_sha256"],
                "held_out_used": bool(lock.metadata["held_out_used"]),
            }
        )

    audit_all = pd.concat(audit_frames, ignore_index=True)
    pairwise_all = pd.concat(pairwise_frames, ignore_index=True)
    condition_all = pd.DataFrame(condition_rows)
    comparison_all = pd.DataFrame(comparison_rows)
    stable_checks_all = pd.DataFrame(stable_id_checks)
    permutation_checks_all = pd.DataFrame(permutation_checks)

    output_files = {
        "candidate_locking_audit.csv": audit_all,
        "eligible_pairwise_jaccard.csv": pairwise_all,
        "recommended_18_condition_inventory.csv": condition_all,
        "bundle_vs_authoritative_selection_comparison.csv": comparison_all,
        "stable_identifier_verification.csv": stable_checks_all,
        "empirical_permutation_invariance.csv": permutation_checks_all,
    }
    for filename, frame in output_files.items():
        frame.to_csv(output_dir / filename, index=False)

    manifest = {
        "schema": "AMPAD-remaining90-authoritative-lock-freeze-v1",
        "operation": "reapply_current_package_lock_to_existing_development_fold_scores",
        "models_fitted": 0,
        "held_out_inputs_used": False,
        "runs": int(len(stable_checks_all)),
        "conditions": int(len(condition_all)),
        "all_archived_stable_identifiers_match": bool(stable_checks_all["match"].all()),
        "all_empirical_candidate_permutations_invariant": bool(
            permutation_checks_all["passed"].all()
        ),
        "empirical_candidate_permutations_tested": int(
            permutation_checks_all["permutations_tested"].sum()
        ),
        "all_bundle_and_authoritative_feature_sets_match": bool(
            comparison_all["same_scientific_feature_set"].all()
        ),
        "bundle_and_authoritative_source_run_differences": int(
            (~comparison_all["same_source_run"]).sum()
        ),
        "maximum_selected_absolute_regret": float(
            condition_all["selected_absolute_regret"].max()
        ),
        "locking": {
            "strategy": "regret_constrained_medoid",
            "tolerance_mode": "absolute",
            "regret_tolerance": 0.01,
            "metric_orientation": "larger_is_better",
            "tie_break_path": (
                "mean_jaccard > higher_locking_score > smaller_feature_count > "
                "stable_mask_hash"
            ),
            "stable_mask_hash_algorithm": "sha256(uint8_canonical_mask_bytes)",
            "duplicate_mask_policy": "retain_multiplicity_as_voting_candidates",
        },
        "inputs": {
            "config": str(config_path),
            "config_sha256": sha256_file(config_path),
            "frozen_scores": str(frozen_scores_path),
            "frozen_scores_sha256": sha256_file(frozen_scores_path),
            "bundle_condition_inventory": str(bundle_inventory_path),
            "bundle_condition_inventory_sha256": sha256_file(bundle_inventory_path),
            "package_src": str(package_src),
        },
        "artifacts": {},
    }
    for filename in output_files:
        manifest["artifacts"][filename] = sha256_file(output_dir / filename)
    (output_dir / "LOCK_FREEZE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "LOCK_FREEZE_COMPLETE").write_text(
        "Authoritative stable-mask-hash lock freeze completed without model fitting.\n",
        encoding="utf-8",
    )

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
