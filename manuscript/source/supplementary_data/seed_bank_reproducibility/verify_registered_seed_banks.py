"""Independent reconstruction of the original protocol-defined seed-bank study.

Reads participant-free candidate masks/fold scores, feature-name universes and
the frozen local protocol/aggregate results only. Does not execute the original
analysis, access participant arrays/predictions, train models, or calibrate delta.

Run (Python 3.10+, NumPy, pandas):
    python verify_registered_seed_banks.py --output OUTPUT_DIRECTORY

Original frozen inputs remain read-only; reconstructed outputs go to --output.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SCHEMES = ("original_candidate_seed", "common_RF_seed342")
BRANCH_LABELS = {"svm_l1": "SVM-L1", "xgboost": "XGBoost", "boruta_rf": "Boruta-RF"}
METRICS = (
    "highest_Jaccard", "locked_Jaccard", "difference_locked_minus_highest",
    "highest_exact_agreement", "locked_exact_agreement",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def save_csv(name: str, rows: list[dict]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


@dataclass(frozen=True)
class Candidate:
    run: int
    mask: frozenset[str]
    mask_hash: str
    score: float


def overlap(a: Candidate, b: Candidate) -> float:
    return len(a.mask & b.mask) / len(a.mask | b.mask)


def choose(candidates: list[Candidate], delta: float) -> tuple[Candidate, Candidate, list[Candidate]]:
    """Independent implementation of frozen highest/strict-medoid decisions."""
    highest = min(candidates, key=lambda c: (-c.score, len(c.mask), c.mask_hash, c.run))
    pool = sorted(
        (c for c in candidates if highest.score - c.score <= delta),
        key=lambda c: (c.mask_hash, c.run),
    )
    assert pool
    def key(candidate: Candidate):
        peers = [overlap(candidate, other) for other in pool if candidate.run != other.run]
        centrality = float(np.mean(peers)) if peers else 1.0
        return -centrality, -candidate.score, len(candidate.mask), candidate.mask_hash, candidate.run
    selected = min(pool, key=key)
    assert highest.score - selected.score <= delta
    return highest, selected, pool


def synthetic_contract_checks() -> None:
    """Protect the full-precision boundary and retained-multiplicity tie rules."""
    items = [Candidate(0, frozenset(["a"]), "b", .9),
             Candidate(1, frozenset(["z"]), "c", .89),
             Candidate(2, frozenset(["z"]), "d", .885)]
    gap = .9 - .885
    assert choose(items, np.nextafter(gap, 0))[1].run == 0
    assert choose(items, gap)[1].run == 1
    assert choose(list(reversed(items)), gap)[1].run == 1
    tied = [Candidate(0, frozenset(["a", "b"]), "a", .9),
            Candidate(1, frozenset(["z"]), "z", .9),
            Candidate(2, frozenset(["x"]), "b", .9)]
    high, locked, _ = choose(tied, 0)
    assert high.run == locked.run == 2  # fewer features, then hash


def compare_rows(actual: list[dict], expected: list[dict], keys: tuple[str, ...]) -> dict:
    """Compare every recorded field, not just displayed or averaged numbers."""
    def row_key(row):
        return tuple(str(row[field]) for field in keys)
    a = {row_key(row): row for row in actual}
    b = {row_key(row): row for row in expected}
    assert len(a) == len(actual) == len(b) == len(expected)
    assert a.keys() == b.keys(), (a.keys() - b.keys(), b.keys() - a.keys())
    numerical_fields = 0
    exact_numeric_matches = 0
    exact_text_matches = 0
    max_error = 0.0
    for key in a:
        assert set(b[key]) <= set(a[key])
        for field, original in b[key].items():
            new = a[key][field]
            if field in keys or field.endswith("mask_hash") or field in {"scheme", "condition"}:
                assert str(new) == str(original), (key, field, new, original)
                exact_text_matches += 1
            else:
                old_value, new_value = float(original), float(new)
                assert math.isfinite(old_value) and math.isfinite(new_value)
                error = abs(new_value - old_value)
                assert error == 0, (key, field, new_value, old_value, error)
                max_error = max(max_error, error)
                numerical_fields += 1
                exact_numeric_matches += int(error == 0)
    return {
        "rows": len(a), "exact_text_fields": exact_text_matches,
        "numeric_fields": numerical_fields, "exact_numeric_matches": exact_numeric_matches,
        "maximum_absolute_numeric_error": max_error,
    }


def table_s33(summary: list[dict], branch_means: list[dict]) -> str:
    lines = [
        "% Draft only: not inserted into manuscript. Generated by verify_registered_seed_banks.py.",
        r"\begin{table}[p]", r"\centering", r"\footnotesize",
        r"\caption{\textbf{Protocol-defined independent seed-bank comparison at fixed allowance $\delta=0.01$.} "
        r"For each screening branch, four independent 20-seed CPU collections supplied nested prefixes "
        r"$R=5,10,20$. $J_{\mathrm{high}}$ and $J_{\mathrm{lock}}$ are mean Jaccard similarities across "
        r"the six pairs of selected bank signatures. $\Delta J$ is the mean paired difference "
        r"(locked minus highest). $A_{\mathrm{high}}$ and $A_{\mathrm{lock}}$ are the corresponding "
        r"fractions of pairs with exactly identical feature sets. All branches, prefix sizes, and both "
        r"scorer schemes are reported; equal-branch means weight the three branches equally.}",
        r"\label{tab:supp33}", r"\setlength{\tabcolsep}{5pt}",
        r"\begin{tabular}{@{}lrrrrrr@{}}", r"\toprule",
        r"Branch & $R$ & $J_{\mathrm{high}}$ & $J_{\mathrm{lock}}$ & $\Delta J$ & $A_{\mathrm{high}}$ & $A_{\mathrm{lock}}$ \\",
        r"\midrule",
    ]
    for index, scheme in enumerate(SCHEMES):
        if index:
            lines.append(r"\midrule")
        label = ("A. Primary: candidate-specific RF seeds" if index == 0
                 else "B. Secondary: common RF seed 342")
        lines.extend([r"\multicolumn{7}{@{}l}{\textbf{" + label + r"}} \\", r"\addlinespace[2pt]"])
        selected = [r for r in summary if r["scheme"] == scheme]
        selected.sort(key=lambda r: (list(BRANCH_LABELS).index(r["branch"]), r["R"]))
        for row in selected + [r for r in branch_means if r["scheme"] == scheme]:
            if row["branch"] == "equal_branch_mean" and row["R"] == 5:
                lines.append(r"\addlinespace[2pt]")
            label = BRANCH_LABELS.get(row["branch"], r"\emph{Equal-branch mean}")
            values = [f"{row[field]:.6f}" for field in METRICS]
            # A displayed plus sign clarifies the direction without changing source precision.
            values[2] = f"{row[METRICS[2]]:+.6f}" if row[METRICS[2]] != 0 else "0.000000"
            lines.append(" & ".join([label, str(row["R"]), *values]) + r" \\")
    lines.extend([
        r"\bottomrule", r"\end{tabular}", r"\par\smallskip",
        r"\begin{minipage}{0.98\textwidth}\footnotesize",
        r"\textit{Design and interpretation.} The local protocol was frozen before candidate generation; "
        r"this does not denote registration in an external preregistry. The analysis conditions on one fixed "
        r"TCGA development partition of 392 participants, with the original preprocessing, screening universes "
        r"and RFECV targets held fixed. The primary scorer uses candidate-specific RF seeds and common "
        r"development folds; the secondary scorer fixes the RF seed at 342. The same 240 candidates "
        r"were reused across scorers and nested $R$ prefixes. Six pairs share four banks, prefixes are "
        r"correlated, and branches share participants; no confidence intervals or $p$-values are reported. "
        r"Exact agreement is zero for both policies in every condition. This is a new CPU-backend extension, "
        r"not reproduction of GPU trajectories or participant-level or external validation. The later "
        r"16-bank, five-candidate calibration analysis is a separate post hoc reblocking of these same runs. "
        r"Full-precision source files contain all 108 pairs, 72 bank selections, 18 condition summaries "
        r"and six equal-branch means. Displayed values are rounded to six decimals.",
        r"\end{minipage}", r"\end{table}", "",
    ])
    return "\n".join(lines)


def main() -> None:
    global HERE
    data_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=data_root / "reconstructed")
    args = parser.parse_args()
    HERE = args.output.resolve()
    HERE.mkdir(parents=True, exist_ok=True)
    workspace = data_root.parent
    original = data_root / "frozen"
    public = workspace / "tolerance_calibration"
    inputs = [original / name for name in [
        "protocol.json", "protocol_initial_8workers.json", "FROZEN_BEFORE_NEW_CANDIDATES.sha256",
        "FROZEN_INITIAL_8WORKERS.sha256", "resource_amendment.json", "launch_receipt.json",
        "results/analysis_validation.json", "results/condition_summary.csv", "results/bank_pairs.csv",
        "results/selections.csv", "results/all_candidates.csv",
        "prepare_experiment.py", "run_experiment.py", "analyze_banks.py", "validate_design.py",
    ]] + [public / name for name in ["candidate_development_audit.csv", "feature_universes.json"]]
    input_hashes = {str(path.relative_to(workspace)): sha(path) for path in inputs}
    protocol = json.loads((original / "protocol.json").read_text(encoding="utf-8"))
    protocol_hash = sha(original / "protocol.json")
    assert protocol_hash == (original / "FROZEN_BEFORE_NEW_CANDIDATES.sha256").read_text().strip()
    assert sha(original / "protocol_initial_8workers.json") == (original / "FROZEN_INITIAL_8WORKERS.sha256").read_text().strip()
    for name, digest in protocol["code_sha256"].items():
        assert sha(original / name) == digest, (name, "Original frozen source code changed")
    amendment = json.loads((original / "resource_amendment.json").read_text())
    launch = json.loads((original / "launch_receipt.json").read_text())
    assert amendment["registered_candidates_generated_before_amendment"] == 0
    assert amendment["scientific_design_changed"] is False
    assert amendment["amended_protocol_sha256"] == launch["protocol_sha256"] == protocol_hash
    assert amendment["amended_utc"] < launch["started_utc"]
    assert protocol["total_GA_runs"] == 240 and protocol["independent_banks_per_condition"] == 4
    assert protocol["bank_sizes"] == [5, 10, 20] and protocol["backend"] == "cpu"
    assert protocol["locking"]["regret_tolerance"] == .01
    assert tuple(protocol["score_schemes"]) == SCHEMES
    assert {c["branch"] for c in protocol["conditions"]} == set(BRANCH_LABELS)
    assert all(c["development_rows"] == 392 for c in protocol["conditions"])
    source_validation = json.loads((original / "results/analysis_validation.json").read_text())
    assert source_validation["protocol_sha256"] == protocol_hash
    for name, digest in source_validation["output_sha256"].items():
        assert sha(original / "results" / name) == digest, (name, "Original aggregate source changed")

    synthetic_contract_checks()
    raw = read_csv(public / "candidate_development_audit.csv")
    universes = json.loads((public / "feature_universes.json").read_text())["universes"]
    assert len(raw) == 240
    identities = [(r["branch"], int(r["original_bank"]), int(r["run"])) for r in raw]
    assert len(set(identities)) == 240
    condition_by_branch = {c["branch"]: c for c in protocol["conditions"]}
    candidates = {}
    candidate_records = []
    target_metadata_discrepancies = []
    for row in raw:
        branch = row["branch"]
        condition = condition_by_branch[branch]
        bank, run = int(row["original_bank"]), int(row["run"])
        assert bank in range(4) and run in range(20)
        assert int(row["GA_seed"]) == condition["seed_banks"][bank][run]
        assert row["development_sha256"] == condition["development_sha256"]
        if int(row["target_k"]) != condition["target_k"]:
            target_metadata_discrepancies.append({
                "branch": branch, "original_bank": bank, "run": run,
                "public_CSV_target_k": int(row["target_k"]),
                "frozen_protocol_target_k": condition["target_k"],
            })
        universe = universes[branch]
        assert len(universe) == condition["feature_universe_size"] and len(set(universe)) == len(universe)
        features = json.loads(row["features_json"])
        mask = frozenset(features)
        assert len(features) == len(mask) == int(row["feature_count"]) > 0
        assert mask <= set(universe)
        encoded = bytes(int(feature in mask) for feature in universe)
        assert hashlib.sha256(encoded).hexdigest() == row["mask_hash"]
        for scheme in SCHEMES:
            score = float(row[scheme + "_score"])
            folds = np.asarray(json.loads(row[scheme + "_folds_json"]), dtype=float)
            assert folds.shape == (5,) and np.isfinite(folds).all() and math.isfinite(score)
            assert abs(float(folds.mean()) - score) < 1e-12
            candidates[(branch, scheme, bank, run)] = Candidate(run, mask, row["mask_hash"], score)
            candidate_records.append({
                "condition": condition["condition_id"], "bank": bank, "run": run,
                "GA_seed": int(row["GA_seed"]), "scheme": scheme, "mask_hash": row["mask_hash"],
                "feature_count": len(mask), "locking_score": score,
            })
    candidate_check = compare_rows(candidate_records, read_csv(original / "results/all_candidates.csv"),
                                   ("condition", "scheme", "bank", "run"))
    selections, pairs = [], []
    for condition in protocol["conditions"]:
        branch = condition["branch"]
        for scheme in SCHEMES:
            for size in protocol["bank_sizes"]:
                chosen = []
                for bank in range(4):
                    group = [candidates[(branch, scheme, bank, run)] for run in range(size)]
                    highest, locked, pool = choose(group, .01)
                    chosen.append((highest, locked))
                    selections.append({
                        "condition": condition["condition_id"], "scheme": scheme, "R": size, "bank": bank,
                        "highest_mask_hash": highest.mask_hash, "locked_mask_hash": locked.mask_hash,
                        "highest_feature_count": len(highest.mask), "locked_feature_count": len(locked.mask),
                        "eligible_pool_size": len(pool), "unique_masks": len({c.mask_hash for c in group}),
                        "locked_development_regret": highest.score - locked.score,
                        "branch": branch, "highest_run": highest.run, "locked_run": locked.run,
                    })
                for a, b in combinations(range(4), 2):
                    ah, al = chosen[a]
                    bh, bl = chosen[b]
                    high_j, locked_j = overlap(ah, bh), overlap(al, bl)
                    pairs.append({
                        "condition": condition["condition_id"], "scheme": scheme, "R": size,
                        "bank_A": a, "bank_B": b, "highest_Jaccard": high_j, "locked_Jaccard": locked_j,
                        "difference_locked_minus_highest": locked_j - high_j,
                        "highest_exact_agreement": int(ah.mask == bh.mask),
                        "locked_exact_agreement": int(al.mask == bl.mask), "branch": branch,
                    })
    selection_check = compare_rows(selections, read_csv(original / "results/selections.csv"),
                                   ("condition", "scheme", "R", "bank"))
    pair_check = compare_rows(pairs, read_csv(original / "results/bank_pairs.csv"),
                              ("condition", "scheme", "R", "bank_A", "bank_B"))
    # Use the original aggregation kernel for an exact binary-float comparison;
    # the actual mask selection and all 108 pair computations above are independent.
    frame = pd.DataFrame(pairs)
    summary = frame.groupby(["condition", "scheme", "R"], as_index=False)[list(METRICS)].mean().to_dict("records")
    for row in summary:
        row["branch"] = next(c["branch"] for c in protocol["conditions"] if c["condition_id"] == row["condition"])
    summary_check = compare_rows(summary, read_csv(original / "results/condition_summary.csv"), ("condition", "scheme", "R"))
    means = []
    for scheme in SCHEMES:
        for size in protocol["bank_sizes"]:
            selected = [r for r in summary if r["scheme"] == scheme and r["R"] == size]
            assert len(selected) == 3
            means.append({
                "condition": "equal_branch_mean", "scheme": scheme, "R": size,
                **{field: float(np.mean([r[field] for r in selected])) for field in METRICS},
                "branch": "equal_branch_mean", "branches": 3,
                "banks_per_branch": 4, "pairs_per_branch": 6,
            })
    assert len(selections) == 72 and len(pairs) == 108 and len(summary) == 18 and len(means) == 6
    assert all(r["highest_exact_agreement"] == r["locked_exact_agreement"] == 0 for r in pairs)
    save_csv("bank_selections_reconstructed.csv", selections)
    save_csv("bank_pairs_reconstructed.csv", pairs)
    save_csv("condition_summary_reconstructed.csv", summary)
    save_csv("equal_branch_means.csv", means)
    (HERE / "supplementary_table_s33_draft.tex").write_text(table_s33(summary, means), encoding="utf-8")
    assert input_hashes == {str(path.relative_to(workspace)): sha(path) for path in inputs}, "Read-only inputs changed."
    evidence = {
        "protocol_sha256": protocol_hash, "frozen_protocol_sha256_matches": True,
        "protocol_frozen_utc": protocol["frozen_utc"], "resource_amendment_utc": amendment["amended_utc"],
        "launch_started_utc": launch["started_utc"],
        "freeze_timing_scope": "Local protocol and amendment records precede launch; not external preregistration or a new audit of remote job receipts.",
        "original_analysis_source": "seed_bank_reproducibility/frozen/analyze_banks.py",
        "original_code_hashes_verified": protocol["code_sha256"], "input_sha256": input_hashes,
        "public_target_metadata_discrepancies": target_metadata_discrepancies,
    }
    (HERE / "source_provenance.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    checks = {
        "all_candidate_scores_and_masks": candidate_check, "bank_selections": selection_check,
        "bank_pairs": pair_check, "condition_summaries": summary_check,
    }
    validation = {
        "status": "VERIFIED_WITH_METADATA_WARNING" if target_metadata_discrepancies else "PASS",
        "numerical_reproduction_status": "PASS", "verification_status": "VERIFIED",
        "public_target_metadata_consistency": "MISMATCH" if target_metadata_discrepancies else "MATCH",
        "verified_utc": datetime.now(timezone.utc).isoformat(), "protocol_sha256": protocol_hash,
        "reconstruction_script_sha256": sha(Path(__file__)),
        "method": "Independent highest/strict-medoid implementation from participant-free CSV, original aggregation kernel; no GA refit or original-script execution.",
        "python": sys.version, "numpy": np.__version__, "pandas": pd.__version__,
        "candidate_masks_verified": 240, "candidate_score_records_verified": 480,
        "bank_selection_rows_verified": 72, "pair_rows_verified": 108,
        "condition_summary_rows_verified": 18, "equal_branch_mean_rows": 6,
        "comparison": checks, "all_recorded_numeric_fields_bit_exact": True,
        "all_selected_mask_hashes_exact": True, "all_exact_agreements_zero": True,
        "public_target_metadata_discrepancy_count": len(target_metadata_discrepancies),
        "metadata_warning": ("Public candidate CSV labels Boruta-RF target_k=18 but frozen protocol and run code specify 8; "
                             "not corrected here. Selection reconstruction uses masks/scores, not target_k."
                             if target_metadata_discrepancies else None),
        "primary_equal_branch_mean": [r for r in means if r["scheme"] == SCHEMES[0]],
        "all_equal_branch_means": means, "fixed_delta": .01,
        "new_CI_or_p_values_created": False, "new_model_or_GA_fits": 0,
        "participant_arrays_or_predictions_accessed": False, "read_only_inputs_unchanged": True,
        "writes_confined_to": str(HERE),
        "fallacy_scan_coverage": "11/11; scoped to supplied aggregate design/results",
        "fallacy_scan": {
            "Simpson_paradox": "Branch-specific signs differ; all 18 rows and equally weighted branch means retained, without asserting uniform effects.",
            "ecological_fallacy": "No participant or biomarker-population inference from bank-level overlap.",
            "Berkson_paradox": "No causal association analysis; only fixed selected development inputs. Sampling-population selection cannot be audited from these summaries.",
            "collider_bias": "No regression/adjustment or causal conditioning claim; mechanism not evaluated from summary masks.",
            "base_rate_neglect": "Not applicable: no diagnostic sensitivity, specificity, predictive values or prevalence claims.",
            "regression_to_mean": "Highest-score is an extremum selection rule, but both rules are applied to the same candidates; no before/after improvement inference.",
            "survivorship_bias": "All frozen 240 candidate identities/seeds and all 18 planned condition/scorer/R combinations are present; no trajectories refit or dropped here.",
            "look_elsewhere_effect": "No tests or significance thresholds; all R/scorer/branch combinations shown, no best-R selection.",
            "forking_paths": "Original fixed-delta protocol kept separate from later post hoc reblocking/calibration; local freeze is not external preregistration.",
            "correlation_causation": "Conditional descriptive CPU extension only; no causal improvement or GPU-trajectory reproduction claim.",
            "reverse_causality": "Not applicable to deterministic comparison of fixed candidate selection rules; no observational directional claim.",
        },
    }
    validation["output_sha256"] = {p.name: sha(p) for p in sorted(HERE.iterdir())
                                   if p.is_file() and p.suffix in {".csv", ".tex", ".json"} and p.name != "validation.json"}
    (HERE / "validation.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "verified_counts": [240, 480, 72, 108, 18],
                      "all_recorded_numeric_fields_bit_exact": True,
                      "metadata_warning": validation["metadata_warning"],
                      "equal_branch_means": means}, indent=2))


if __name__ == "__main__":
    main()
