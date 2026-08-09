"""Validate aggregate scientific and privacy invariants for the V12 radiomics insert."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "supplementary_data" / "private_radiomics"


def main() -> None:
    run_audit = json.loads((DATA / "completed_run_audit.json").read_text(encoding="utf-8"))
    assert run_audit["status"] == "PASS"
    assert run_audit["ga_jobs_verified"] == 30
    assert run_audit["all_jobs_completed_50_generations"] is True
    assert run_audit["all_run_artifact_checksums_valid"] is True
    assert run_audit["held_out_used_during_preparation_or_ga"] is False

    runs = pd.read_csv(DATA / "ga_run_inventory_verified.csv")
    assert len(runs) == 30
    assert set(runs["completed_generations"]) == {50}
    assert not runs["held_out_used"].astype(bool).any()
    assert runs["artifact_checksums_valid"].astype(bool).all()

    locking = pd.read_csv(DATA / "locking_summary.csv")
    stability = pd.read_csv(DATA / "seed_stability_summary.csv")
    conditions = pd.read_csv(DATA / "radiomics_condition_summary.csv")
    metrics = pd.read_csv(DATA / "heldout_metrics.csv")
    effects = pd.read_csv(DATA / "paired_heldout_effects.csv")
    assert len(locking) == len(stability) == len(conditions) == 6
    assert len(metrics) == 18
    assert len(effects) == 15
    assert not locking["held_out_used_for_locking"].astype(bool).any()
    assert (stability["selected_absolute_regret"] <= 0.01).all()
    assert np.allclose(stability["selected_absolute_regret"], 0.0)
    assert sorted(stability["eligible_pool_size"].tolist()) == [1, 1, 1, 1, 1, 2]
    assert np.isclose(conditions["compression_vs_direct"].min(), 0.10)
    assert np.isclose(conditions["compression_vs_direct"].max(), 0.81)
    assert np.isclose(conditions["compression_vs_direct"].median(), 0.755621890547264)
    assert np.isclose(conditions["cross_view_locked_jaccard"].min(), 0.04878048780487805)
    assert np.isclose(conditions["cross_view_locked_jaccard"].max(), 0.2727272727272727)
    assert ((effects["ci_low"] <= 0) & (effects["ci_high"] >= 0)).all()

    manifest = json.loads((DATA / "radiomics_figure_manifest.json").read_text(encoding="utf-8"))
    assert manifest["target_width_mm"] == 170
    assert manifest["background_grid"] is False
    assert manifest["participant_level_inputs_read"] is False
    assert manifest["heldout_prediction_rows_read"] is False
    for name in ("figure_s20.pdf", "figure_s20.svg", "figure_s20.png"):
        assert (ROOT / "figures" / name).is_file()

    forbidden = {
        "heldout_predictions_pseudonymous.csv",
        "split_manifest_pseudonymous.csv",
        "prepared.joblib",
        "heldout_evaluation_input.joblib",
    }
    assert not forbidden.intersection(path.name for path in DATA.rglob("*"))
    print("Radiomics integration invariants passed.")


if __name__ == "__main__":
    main()
