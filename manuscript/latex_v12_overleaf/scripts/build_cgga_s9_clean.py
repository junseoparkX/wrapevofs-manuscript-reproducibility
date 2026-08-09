"""Rebuild Supplementary Figure S9 from frozen aggregate CGGA outputs.

This presentation-only builder removes the redundant settings block that was
previously drawn beside panel c. It does not fit a model, select a feature, or
recalculate any scientific result.
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

matplotlib.rcParams["svg.hashsalt"] = "WrapEvoFS-v12-s9-clean"


V12 = Path(__file__).resolve().parents[1]
DATA = V12 / "supplementary_data" / "cgga_tuned_rf_s9"
FIGURES = V12 / "figures"
WIDTH = 170 / 25.4

METHODS = ["svm_l1", "xgboost", "boruta_rf"]
LABELS = {"svm_l1": "SVM-L1", "xgboost": "XGBoost", "boruta_rf": "Boruta-RF"}
COLORS = {"svm_l1": "#239b71", "xgboost": "#e69500", "boruta_rf": "#d95c4a"}
MARKERS = {"svm_l1": "o", "xgboost": "s", "boruta_rf": "D"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def style(axis: plt.Axes, panel: str, title: str) -> None:
    axis.grid(False)
    axis.spines[["top", "right"]].set_visible(False)
    axis.tick_params(labelsize=7, length=3)
    axis.set_title(title, fontsize=8.2, fontweight="normal", pad=7)
    axis.text(
        -0.14,
        1.18,
        f"{panel})",
        transform=axis.transAxes,
        fontsize=11,
        fontweight="bold",
        va="top",
    )


def save(figure: plt.Figure) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for extension in ["pdf", "svg", "png"]:
        path = FIGURES / f"figure_s9.{extension}"
        if extension == "pdf":
            metadata = {
                "Creator": "WrapEvoFS build_cgga_s9_clean.py",
                "CreationDate": None,
                "ModDate": None,
            }
        elif extension == "svg":
            metadata = {"Creator": "WrapEvoFS build_cgga_s9_clean.py", "Date": None}
        else:
            metadata = {"Software": "WrapEvoFS build_cgga_s9_clean.py"}
        figure.savefig(
            path,
            dpi=600 if extension == "png" else None,
            bbox_inches="tight",
            facecolor="white",
            metadata=metadata,
        )
        hashes[extension] = sha256(path)
    plt.close(figure)
    return hashes


def main() -> None:
    nested_path = DATA / "nested_cv_auroc.csv"
    heldout_path = DATA / "heldout_intervals.csv"
    importance_path = DATA / "primary_feature_importance.csv"
    nested = pd.read_csv(nested_path).set_index("method").loc[METHODS]
    heldout = pd.read_csv(heldout_path)
    importance = pd.read_csv(importance_path).sort_values("importance", ascending=True)

    figure = plt.figure(figsize=(WIDTH, 5.05))
    grid = figure.add_gridspec(
        2,
        2,
        height_ratios=[0.92, 1.42],
        left=0.14,
        right=0.985,
        top=0.93,
        bottom=0.095,
        wspace=0.42,
        hspace=0.55,
    )

    ax = figure.add_subplot(grid[0, 0])
    y = np.arange(len(METHODS))[::-1]
    for yi, method in zip(y, METHODS):
        row = nested.loc[method]
        ax.errorbar(
            row["estimate"],
            yi,
            xerr=row["sd"],
            fmt=MARKERS[method],
            ms=5.8,
            color=COLORS[method],
            ecolor=COLORS[method],
            elinewidth=1.15,
            capsize=2,
        )
    ax.set_yticks(y, [LABELS[method] for method in METHODS])
    for label, method in zip(ax.get_yticklabels(), METHODS):
        label.set_color(COLORS[method])
    ax.set_xlim(0.70, 0.98)
    ax.set_xlabel("Nested CV AUROC, mean ± SD", fontsize=7.5)
    style(ax, "a", "Nested development-CV performance")

    ax = figure.add_subplot(grid[0, 1])
    metrics = ["auroc", "auprc", "balanced_accuracy"]
    metric_labels = ["AUROC", "AUPRC", "Balanced\naccuracy"]
    offsets = {"svm_l1": -0.16, "xgboost": 0.0, "boruta_rf": 0.16}
    x = np.arange(len(metrics))
    for method in METHODS:
        part = heldout.loc[heldout["method"].eq(method)].set_index("metric").loc[metrics]
        estimate = part["estimate"].to_numpy()
        low = part["ci_low"].to_numpy()
        high = part["ci_high"].to_numpy()
        ax.errorbar(
            x + offsets[method],
            estimate,
            yerr=np.vstack([estimate - low, high - estimate]),
            fmt=MARKERS[method],
            ms=5.2,
            color=COLORS[method],
            ecolor=COLORS[method],
            elinewidth=1.05,
            capsize=2,
            label=LABELS[method],
        )
    ax.set_xticks(x, metric_labels)
    ax.set_ylim(0.45, 0.83)
    ax.set_ylabel("Held-out estimate", fontsize=7.5)
    style(ax, "b", "Held-out tuned-RF sensitivity")
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.21),
        ncol=3,
        frameon=False,
        fontsize=6.5,
        handlelength=1.0,
        columnspacing=0.9,
    )

    ax = figure.add_subplot(grid[1, :])
    y = np.arange(len(importance))
    bars = ax.barh(y, importance["importance"], color=COLORS["svm_l1"], alpha=0.78, height=0.58)
    ax.set_yticks(y, importance["feature"])
    ax.set_xlim(0, 0.165)
    ax.set_xlabel("Random-forest feature importance", fontsize=7.5)
    style(ax, "c", "Primary SVM-L1 signature feature importance")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0, pad=4)
    for bar, value in zip(bars, importance["importance"]):
        ax.text(
            value + 0.0022,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.3f}",
            va="center",
            fontsize=6.2,
            color="#263746",
        )

    hashes = save(figure)
    manifest = {
        "figure": "Supplementary Figure S9",
        "builder": "scripts/build_cgga_s9_clean.py",
        "presentation_only_change": True,
        "scientific_recomputation": False,
        "removed_element": "redundant in-figure selected-settings block",
        "source_sha256": {
            str(path.relative_to(V12)): sha256(path)
            for path in [nested_path, heldout_path, importance_path]
        },
        "output_sha256": hashes,
    }
    manifest_path = DATA / "figure_s9_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Built Figure S9 at 170 mm; manifest: {manifest_path}")


if __name__ == "__main__":
    main()
