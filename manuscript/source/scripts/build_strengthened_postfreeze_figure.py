"""Build the concise main-text AMP-AD post-freeze figure.

This builder reuses only frozen analysis tables.  It does not refit a model or
change a selected mask.  The complete condition-level three-panel audit remains
available as the supplementary source; this main version consolidates the two
comparator panels to avoid an identical duplicate.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from figure_palette import BRANCH_COLORS, DARK, LIGHT, MID


matplotlib.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 6.5,
        "axes.labelsize": 6.8,
        "axes.titlesize": 8.3,
        "axes.linewidth": 0.75,
        "xtick.labelsize": 5.8,
        "ytick.labelsize": 5.8,
        "xtick.major.width": 0.75,
        "ytick.major.width": 0.75,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "svg.hashsalt": "WrapEvoFS-strengthened-postfreeze",
    }
)

HERE = Path(__file__).resolve()
MANUSCRIPT = HERE.parents[1]
WORKSPACE = MANUSCRIPT.parents[1]
SOURCE = WORKSPACE / "analysis" / "ampad_updated_one_time_heldout_20260808"
FIGURES = MANUSCRIPT / "figures"
SOURCE_DATA = MANUSCRIPT / "supplementary_data" / "strengthened_main"
WIDTH = 170 / 25.4

BRANCHES = ["svm_l1", "xgboost", "boruta_rf"]
BRANCH_LABELS = {"svm_l1": "SVM-L1", "xgboost": "XGBoost", "boruta_rf": "Boruta-RF"}
CAPS = ["low", "reference"]
CAP_LABELS = {"low": "Small", "reference": "Reference"}
CAP_MARKERS = {"low": "o", "reference": "s"}


def style_axis(axis: plt.Axes) -> None:
    axis.grid(False)
    axis.spines[["top", "right"]].set_visible(False)
    axis.tick_params(length=2.8, color=DARK, labelcolor=DARK)
    axis.spines["left"].set_color(DARK)
    axis.spines["bottom"].set_color(DARK)


def panel_label(axis: plt.Axes, label: str) -> None:
    axis.text(-0.16, 1.07, f"{label})", transform=axis.transAxes, fontsize=10.2,
              fontweight="bold", va="bottom", ha="left", color=DARK)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    metrics_path = SOURCE / "condition_metrics.csv"
    contrasts_path = SOURCE / "paired_condition_contrasts.csv"
    metrics = pd.read_csv(metrics_path)
    contrasts = pd.read_csv(contrasts_path)
    updated = metrics.loc[metrics["variant"] == "updated_regret_locked"].copy()
    centers = ["emory", "mayo", "mount_sinai", "rush"]
    center_labels = ["Emory", "Mayo", "Mount Sinai", "Rush"]

    figure, axes = plt.subplots(
        1,
        2,
        figsize=(WIDTH, 3.15),
        gridspec_kw={"width_ratios": [0.96, 1.22]},
    )

    # a) All 24 frozen signatures, organized by held-out center.
    axis = axes[0]
    offsets = {"svm_l1": -0.20, "xgboost": 0.0, "boruta_rf": 0.20}
    for branch in BRANCHES:
        for cap in CAPS:
            part = (
                updated.loc[(updated["branch"] == branch) & (updated["cap"] == cap)]
                .set_index("center")
                .loc[centers]
            )
            face = "white" if cap == "low" else BRANCH_COLORS[branch]
            axis.scatter(
                np.arange(4) + offsets[branch],
                part["macro_auroc"],
                s=29,
                marker=CAP_MARKERS[cap],
                facecolors=face,
                edgecolors=BRANCH_COLORS[branch],
                linewidth=1.15,
                zorder=3,
            )
    axis.set_xticks(range(4), center_labels, rotation=23, ha="right")
    axis.set_ylabel("Held-out macro AUROC")
    axis.set_ylim(0.60, 0.91)
    axis.set_title("Frozen signatures across centers", fontweight="normal", pad=8)
    style_axis(axis)
    panel_label(axis, "a")

    # b) Put both pooled comparators on one common scale.
    axis = axes[1]
    row_order = [(branch, cap) for branch in BRANCHES for cap in CAPS]
    comparator_specs = [
        ("archived_rfecv_only", "RFECV-only", "o", -0.13),
        ("archived_locked_medoid", "Legacy top-three", "D", 0.13),
    ]
    source_rows: list[dict] = []
    for comparator, _, comparator_marker, y_offset in comparator_specs:
        part = contrasts.loc[
            (contrasts["comparator"] == comparator) & (contrasts["metric"] == "macro_auroc")
        ].set_index(["branch", "cap"])
        for y, (branch, cap) in enumerate(row_order):
            row = part.loc[(branch, cap)]
            point = float(row["updated_minus_comparator"])
            low = float(row["ci_low"])
            high = float(row["ci_high"])
            face = "white" if cap == "low" else BRANCH_COLORS[branch]
            axis.errorbar(
                point,
                y + y_offset,
                xerr=[[point - low], [high - point]],
                fmt=comparator_marker,
                ms=4.4,
                mfc=face,
                mec=BRANCH_COLORS[branch],
                mew=1.0,
                ecolor=BRANCH_COLORS[branch],
                elinewidth=0.95,
                capsize=1.7,
                zorder=3,
            )
            source_rows.append(
                {
                    "branch": branch,
                    "cap": cap,
                    "comparator": comparator,
                    "metric": "macro_auroc",
                    "updated_minus_comparator": point,
                    "ci_low": low,
                    "ci_high": high,
                }
            )
    axis.axvline(0, color=DARK, lw=0.8, zorder=1)
    axis.set_yticks(
        range(6),
        [f"{BRANCH_LABELS[branch]}  {CAP_LABELS[cap]}" for branch, cap in row_order],
    )
    axis.invert_yaxis()
    axis.set_xlim(-0.075, 0.075)
    axis.set_xlabel("Updated minus comparator macro AUROC")
    axis.set_title("Pooled paired contrasts", fontweight="normal", pad=8)
    style_axis(axis)
    panel_label(axis, "b")

    branch_handles = [
        plt.Line2D([], [], marker="o", color=BRANCH_COLORS[b], linestyle="", label=BRANCH_LABELS[b])
        for b in BRANCHES
    ]
    comparator_handles = [
        plt.Line2D([], [], marker="o", color=DARK, markerfacecolor="white", linestyle="", label="RFECV-only"),
        plt.Line2D([], [], marker="D", color=DARK, markerfacecolor="white", linestyle="", label="Legacy top-three"),
        plt.Line2D([], [], marker="o", color=MID, markerfacecolor="white", linestyle="", label="Small cap"),
        plt.Line2D([], [], marker="s", color=MID, markerfacecolor=MID, linestyle="", label="Reference cap"),
    ]
    figure.legend(
        handles=branch_handles + comparator_handles,
        loc="lower center",
        ncol=7,
        frameon=False,
        fontsize=5.8,
        bbox_to_anchor=(0.5, 0.005),
        handletextpad=0.3,
        columnspacing=0.75,
    )
    figure.subplots_adjust(left=0.085, right=0.99, top=0.83, bottom=0.27, wspace=0.56)

    FIGURES.mkdir(parents=True, exist_ok=True)
    SOURCE_DATA.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(source_rows).to_csv(SOURCE_DATA / "figure_5_paired_contrasts.csv", index=False)
    updated.to_csv(SOURCE_DATA / "figure_5_condition_metrics.csv", index=False)

    hashes: dict[str, str] = {}
    for extension in ("pdf", "svg", "png"):
        path = FIGURES / f"figure_5_strengthened.{extension}"
        metadata = {"Creator": "WrapEvoFS build_strengthened_postfreeze_figure.py"}
        if extension == "pdf":
            metadata.update({"CreationDate": None, "ModDate": None})
        elif extension == "svg":
            metadata["Date"] = None
        else:
            metadata["Software"] = metadata.pop("Creator")
        figure.savefig(
            path,
            dpi=600 if extension == "png" else None,
            bbox_inches="tight",
            facecolor="white",
            metadata=metadata,
        )
        hashes[extension] = sha256(path)
    plt.close(figure)

    manifest = {
        "builder": str(HERE.relative_to(WORKSPACE)),
        "source_sha256": {metrics_path.name: sha256(metrics_path), contrasts_path.name: sha256(contrasts_path)},
        "output_sha256": hashes,
        "width_mm": 170,
        "scientific_note": "Frozen masks and existing post-freeze estimates only; no refitting.",
    }
    (SOURCE_DATA / "figure_5_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
