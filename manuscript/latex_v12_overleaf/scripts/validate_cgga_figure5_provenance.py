"""Verify that the manuscript-local Figure 5 tables match frozen upstream outputs.

Run this audit from the complete manuscript reproducibility repository. The
submission ZIP intentionally contains the aggregate figure tables but not every
historical upstream analysis directory.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal


LATEX_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = LATEX_ROOT.parents[1]
LOCAL = LATEX_ROOT / "supplementary_data" / "cgga_figure5"

UPSTREAM = {
    "panel_a": REPOSITORY_ROOT / "data" / "plot_data" / "Figure_5" / "figure5b_compression_auroc.csv",
    "panel_b": REPOSITORY_ROOT / "data" / "plot_data" / "Figure_6" / "figure6c_paired_bootstrap_differences.csv",
    "panel_c_size_jaccard": REPOSITORY_ROOT
    / "data"
    / "plot_data"
    / "Figure_6"
    / "figure6b_jaccard_summary.csv",
    "panel_c_nogueira": REPOSITORY_ROOT
    / "analysis"
    / "regret_revision"
    / "figure2_compression_regret_plot_data.csv",
}

EXPECTED_SHA256 = {
    "panel_a": "3739d2013bd86a2cdf656c17fe70afdb437faf46fc27f8945422242f529f2b90",
    "panel_b": "c7542daa21ffdbb6939ebe7f8e41465bb53505b8ff077ad76455fa49a4b82340",
    "panel_c_size_jaccard": "f8e659ca1e9a5fe345c895be5965634e1d93fbf53a5057aa57d7fec2ff228078",
    "panel_c_nogueira": "02a9d415e13d63b17a2d551d9ba5394c7f824128d3b3539ffa59949446a7b6f4",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sorted_frame(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    return frame.sort_values(keys).reset_index(drop=True)


def main() -> None:
    missing = [str(path) for path in UPSTREAM.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "The complete reproducibility repository is required; missing: " + ", ".join(missing)
        )
    for name, path in UPSTREAM.items():
        actual = sha256_file(path)
        if actual != EXPECTED_SHA256[name]:
            raise AssertionError(f"Frozen upstream checksum changed for {name}: {actual}")

    panel_a = pd.read_csv(LOCAL / "panel_a_compression_auroc.csv")
    source_a = pd.read_csv(UPSTREAM["panel_a"])
    source_a["variant"] = source_a["variant"].replace({"full_medoid": "locked_medoid"})
    source_a = source_a[panel_a.columns]
    assert_frame_equal(
        sorted_frame(panel_a, ["method", "variant"]),
        sorted_frame(source_a, ["method", "variant"]),
        check_exact=True,
    )

    panel_b = pd.read_csv(LOCAL / "panel_b_locked_minus_rfecv.csv")
    source_b = pd.read_csv(UPSTREAM["panel_b"]).rename(
        columns={"delta_full_medoid_minus_rfecv": "difference"}
    )[panel_b.columns]
    assert_frame_equal(
        sorted_frame(panel_b, ["method", "metric"]),
        sorted_frame(source_b, ["method", "metric"]),
        check_exact=True,
    )

    size_jaccard = pd.read_csv(UPSTREAM["panel_c_size_jaccard"]).rename(
        columns={
            "run_feature_count_mean": "mean_feature_count",
            "pairwise_jaccard_mean": "mean_pairwise_jaccard",
        }
    )
    size_jaccard = size_jaccard[
        ["method", "method_label", "condition", "mean_feature_count", "mean_pairwise_jaccard"]
    ]

    nogueira = pd.read_csv(UPSTREAM["panel_c_nogueira"])
    nogueira = nogueira.loc[nogueira["dataset"].str.casefold().eq("cgga")]
    uniqueness = nogueira.groupby(["branch", "condition"])["nogueira_seed_agreement"].nunique()
    if not uniqueness.eq(1).all():
        raise AssertionError("Nogueira agreement is not invariant across locking-rule rows.")
    nogueira = (
        nogueira.groupby(["branch", "condition"], as_index=False)["nogueira_seed_agreement"]
        .first()
        .rename(columns={"branch": "method", "nogueira_seed_agreement": "nogueira_agreement"})
    )
    expected_c = size_jaccard.merge(nogueira, on=["method", "condition"], validate="one_to_one")
    expected_c.insert(
        3,
        "condition_label",
        expected_c["condition"].map(
            {"no_penalty": "No target-size guidance", "penalty": "Target-size guided"}
        ),
    )
    panel_c = pd.read_csv(LOCAL / "panel_c_five_run_agreement.csv")
    expected_c = expected_c[panel_c.columns]
    assert_frame_equal(
        sorted_frame(panel_c, ["method", "condition"]),
        sorted_frame(expected_c, ["method", "condition"]),
        check_exact=True,
    )

    print("Figure 5 provenance checks passed: panels a, b, and c match frozen upstream outputs.")


if __name__ == "__main__":
    main()
