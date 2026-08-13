"""Validate the frozen locking-simulation integration without rerunning it."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "supplementary_data" / "locking_rule_simulation"
PROTOCOL_SHA256 = "6bb91ec337c331aa4b69646f5166831503405d2721a40d16be75718179418d6f"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(observed: str | float, expected: float, tolerance: float = 1e-12) -> None:
    if not math.isclose(float(observed), expected, rel_tol=0.0, abs_tol=tolerance):
        raise AssertionError(f"Expected {expected}, observed {observed}")


def main() -> None:
    checks: list[str] = []

    primary = {row["rule"]: row for row in rows("table_s25_primary_summary.csv")}
    expected = {
        "highest_score": (0.002222612, 0.423792679),
        "legacy_top3_medoid": (0.002537063, 0.459779708),
        "full_bank_medoid": (0.002338613, 0.474539476),
        "regret_medoid": (0.002594897, 0.445894250),
    }
    if set(primary) != set(expected):
        raise AssertionError("Primary rule inventory changed")
    for rule, (oracle_regret, jaccard) in expected.items():
        close(primary[rule]["oracle_regret"], oracle_regret, 1e-9)
        close(primary[rule]["full_bank_mean_jaccard"], jaccard, 1e-9)
        if int(primary[rule]["n_scenarios"]) != 162:
            raise AssertionError(f"Unexpected primary scenario count for {rule}")
    close(primary["regret_medoid"]["empirical_regret"], 0.00130458463951, 1e-14)
    checks.append("primary equal-scenario summaries match frozen values")

    audit = {row["rule"]: row for row in rows("table_s25_regret_audit.csv")}
    current = audit["regret_medoid"]
    if int(current["scenarios_mean_gt_delta"]) != 0:
        raise AssertionError("Current-rule scenario-mean feasibility audit failed")
    if float(current["max_scenario_q95"]) >= 0.01:
        raise AssertionError("Current-rule scenario q95 reached the configured bound")
    if current["configured_individual_violation_count"] != "0 (4,995,000 banks)":
        raise AssertionError("Current-rule complete-bank feasibility audit changed")
    checks.append("strict empirical-regret audit covers 4,995,000 banks with zero violations")

    decisions = rows("table_s25_decision_paths.csv")
    exclusive_total = sum(
        float(row["mean_probability"])
        for row in decisions
        if row["decision_metric"] != "hash_stage_probability"
    )
    close(exclusive_total, 1.0, 5e-9)
    checks.append("mutually exclusive decision paths sum to one")

    delta_rows = rows("figure_s24_panel_b.csv")
    if {float(row["delta"]) for row in delta_rows} != {0.0, 0.005, 0.01, 0.02}:
        raise AssertionError("Tolerance panel does not contain the frozen delta set")
    r_rows = rows("figure_s24_panel_c.csv")
    if {int(row["candidate_count"]) for row in r_rows} != {3, 5, 10, 20, 50, 100}:
        raise AssertionError("Candidate-bank-size panel does not contain the frozen R set")
    checks.append("locking-simulation sensitivity axes match the frozen design")

    provenance = json.loads((DATA / "PROVENANCE.json").read_text(encoding="utf-8"))
    build = json.loads((DATA / "BUILD_MANIFEST.json").read_text(encoding="utf-8"))
    render = json.loads((DATA / "RENDER_MANIFEST.json").read_text(encoding="utf-8-sig"))
    if {provenance["protocol_sha256"], build["protocol_sha256"]} != {PROTOCOL_SHA256}:
        raise AssertionError("Protocol hash mismatch")
    if provenance["scientific_workload"] != {
        "primary_banks": 1_620_000,
        "sensitivity_banks": 3_375_000,
        "total_banks": 4_995_000,
        "scenario_count": 513,
        "ga_runs": 0,
    }:
        raise AssertionError("Scientific workload metadata changed")
    checks.append("protocol and workload provenance are internally consistent")

    outputs = {
        "svg": ROOT / "figures" / "figure_s24.svg",
        "pdf": ROOT / "figures" / "figure_s24.pdf",
        "png": ROOT / "figures" / "figure_s24.png",
    }
    for kind, path in outputs.items():
        if sha256(path) != render[f"{kind}_sha256"]:
            raise AssertionError(f"Rendered {kind} hash mismatch")
    svg = outputs["svg"].read_text(encoding="utf-8")
    if 'width="170mm"' not in svg or 'height="67mm"' not in svg:
        raise AssertionError("Locking-simulation figure canvas is not 170 x 67 mm")
    if "grid" in svg.lower():
        raise AssertionError("Locking-simulation figure contains an unexpected grid marker")
    for panel in ("a)", "b)", "c)"):
        if panel not in svg:
            raise AssertionError(f"Missing panel label {panel}")
    checks.append("locking-simulation PDF/SVG/PNG hashes, 170-mm canvas, and grid-free style pass")

    main_text = (ROOT / "sections" / "main_text.tex").read_text(encoding="utf-8")
    supplementary = (ROOT / "sections" / "supplementary.tex").read_text(encoding="utf-8")
    table = (ROOT / "tables" / "table_47.tex").read_text(encoding="utf-8")
    if main_text.count("Supplementary Fig.~S27") < 3:
        raise AssertionError("Figure S27 is not cited in Results, Discussion, and Methods")
    if main_text.count("Supplementary Table~S22") < 3:
        raise AssertionError("Table S22 is not cited in Results, Discussion, and Methods")
    if supplementary.count("\\label{fig:supp27}") != 1:
        raise AssertionError("Supplementary Figure S27 label is missing or duplicated")
    if table.count("\\label{tab:supp22}") != 1 or "q95 denotes" not in table:
        raise AssertionError("Supplementary Table S22 label or q95 definition failed")
    if "—" in main_text or "—" in supplementary or "—" in table:
        raise AssertionError("An em dash was introduced in the integrated manuscript text")
    checks.append("Results, Discussion, and Methods citations plus S27/S22 labels pass")

    source_manifest = (
        ROOT / "documentation" / "FIGURE_SOURCE_DATA_MANIFEST.csv"
    ).read_text(encoding="utf-8")
    if "Supplementary Figure S27" not in source_manifest or "figure_s24.pdf" not in source_manifest:
        raise AssertionError("Locking-simulation asset is absent from the source-data manifest")
    checks.append("source-data manifest includes Supplementary Figure S27")

    report = {
        "status": "PASS",
        "protocol_sha256": PROTOCOL_SHA256,
        "checks": checks,
        "manuscript_outputs": {
            "main_pdf_sha256": sha256(ROOT / "main.pdf"),
            "supplementary_pdf_sha256": sha256(ROOT / "supplementary_information.pdf"),
        },
        "claim_boundary": provenance["claim_boundary"],
    }
    destination = DATA / "INTEGRATION_VALIDATION.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
