"""Check submission-QA numerical and terminology invariants without rerunning analyses."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def require_text(path: Path, *fragments: str) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [fragment for fragment in fragments if fragment not in text]
    if missing:
        raise AssertionError(f"{path}: missing frozen fragments {missing}")


def main() -> None:
    main_text = ROOT / "sections" / "main_text.tex"
    require_text(
        main_text,
        "120 completed GA runs",
        "24 Small/Reference",
        "decreased from 216 to 137",
        "deviation remained lower at 135 versus 112",
        "decreased from 673 to 333",
        "from 428 to 267",
        "maximum selected regret was 0.00835",
        "tolerance of 0.01",
        "2 of the 24 corrected-objective conditions had singleton eligible pools",
        "6 had two candidates",
        "16 had at least three",
        "Unique Jaccard medoids determined 13 selections",
        "higher locking score resolved 9",
        "singleton selection resolved 2",
        "feature count and stable hash were not reached",
    )
    require_text(
        ROOT / "tables" / "table_04.tex",
        "36 archived AMP-AD configurations",
        "694 all-zero generations",
    )
    require_text(
        ROOT / "tables" / "table_40.tex",
        "All 24 conditions & Absolute target deviation & 24 & 216 & 137",
        "All 24 conditions & All-zero generations & 24 & 673 & 333",
        "Excluding Rush/SVM-L1/Small & Absolute target deviation & 23 & 135 & 112",
        "Excluding Rush/SVM-L1/Small & All-zero generations & 23 & 428 & 267",
    )
    with (ROOT / "revision_outputs" / "ELIGIBLE_POOL_TIE_PATH_AUDIT.csv").open(
        newline="", encoding="utf-8-sig"
    ) as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 24:
        raise AssertionError(f"Expected 24 tie-path rows, found {len(rows)}")
    pool_counts = {"1": 0, "2": 0, "3+": 0}
    decision_counts: dict[str, int] = {}
    for row in rows:
        pool_counts[row["pool_category"]] += 1
        decision_counts[row["decision_stage"]] = decision_counts.get(row["decision_stage"], 0) + 1
    if pool_counts != {"1": 2, "2": 6, "3+": 16}:
        raise AssertionError(f"Unexpected eligible-pool counts: {pool_counts}")
    expected_decisions = {"singleton_direct": 2, "unique_jaccard": 13, "higher_score": 9}
    if decision_counts != expected_decisions:
        raise AssertionError(f"Unexpected decision-stage counts: {decision_counts}")
    print("Frozen-value and decision-path checks passed.")


if __name__ == "__main__":
    main()
