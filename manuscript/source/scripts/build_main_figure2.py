from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from figure_palette import BRANCH_LABEL_COLORS, CURRENT, DARK, LIGHT, ORIGINAL, STRESS


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIGURES = ROOT / "figures"
OUT = ROOT / "revision_outputs"
WIDTH_IN = 180.0 / 25.4
BLUE = CURRENT
GRAY = ORIGINAL
LIGHT_GRAY = LIGHT
BLACK = DARK
BRANCH_MARKERS = {"SVM-L1": "o", "XGBoost": "s", "Boruta-RF": "D"}


mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 7.2,
        "font.weight": "normal",
        "axes.titleweight": "normal",
        "axes.labelweight": "normal",
        "axes.linewidth": 0.7,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "legend.frameon": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    }
)


def panel_label(axis: plt.Axes, label: str) -> None:
    axis.text(
        -0.16,
        1.08,
        f"{label})",
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontsize=9.0,
        fontweight="bold",
        color=BLACK,
        clip_on=False,
    )


def clean_axis(axis: plt.Axes) -> None:
    axis.grid(False)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(labelsize=6.7)


def save_figure(figure: plt.Figure) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for suffix in ("svg", "pdf", "png"):
        path = FIGURES / f"figure_2.{suffix}"
        figure.savefig(
            path,
            dpi=300 if suffix == "png" else None,
            bbox_inches="tight",
            pad_inches=0.035,
            facecolor="white",
        )
        hashes[suffix] = hashlib.sha256(path.read_bytes()).hexdigest()
    plt.close(figure)
    return hashes


def slope_panel(
    axis: plt.Axes,
    data: pd.DataFrame,
    *,
    original: str,
    updated: str,
    ylabel: str,
    title: str,
) -> None:
    for row in data.itertuples(index=False):
        original_value = float(getattr(row, original))
        updated_value = float(getattr(row, updated))
        stress = bool(row.stress_condition)
        marker = BRANCH_MARKERS[str(row.Branch)]
        branch_color = BRANCH_LABEL_COLORS[str(row.Branch)]
        line_color = STRESS if stress else LIGHT_GRAY
        axis.plot(
            [0, 1],
            [original_value, updated_value],
            color=line_color,
            lw=1.4 if stress else 0.7,
            zorder=1,
        )
        axis.scatter(
            0,
            original_value,
            marker=marker,
            s=18,
            facecolor=STRESS if stress else GRAY,
            edgecolor="white",
            linewidth=0.45,
            zorder=2,
        )
        axis.scatter(
            1,
            updated_value,
            marker=marker,
            s=18,
            facecolor=STRESS if stress else branch_color,
            edgecolor="white",
            linewidth=0.45,
            zorder=2,
        )
    axis.set_xticks([0, 1], ["Original", "Updated"])
    axis.set_xlim(-0.22, 1.22)
    axis.set_ylabel(ylabel)
    axis.set_title(title, fontsize=7.6, pad=5)
    clean_axis(axis)


def build() -> dict[str, str]:
    data = pd.read_csv(OUT / "S16_CONDITION_LEVEL_PAIRED.csv")
    tie = pd.read_csv(OUT / "ELIGIBLE_POOL_TIE_PATH_AUDIT.csv")
    if len(data) != 24:
        raise ValueError(f"Expected 24 conditions, found {len(data)}")
    maximum_regret = float(data["updated_regret"].max())
    if maximum_regret > 0.01 or not np.isclose(maximum_regret, 0.0083473, atol=5e-7):
        raise ValueError(f"Unexpected maximum selected regret: {maximum_regret}")

    figure, axes = plt.subplots(2, 2, figsize=(WIDTH_IN, 5.05))

    slope_panel(
        axes[0, 0],
        data,
        original="original_target_deviation",
        updated="updated_target_deviation",
        ylabel="Absolute target deviation",
        title="Matched target-size fidelity",
    )
    panel_label(axes[0, 0], "a")

    slope_panel(
        axes[0, 1],
        data,
        original="original_all_zero_generations",
        updated="updated_all_zero_generations",
        ylabel="All-zero generations",
        title="Objective-flattening diagnostic",
    )
    panel_label(axes[0, 1], "b")

    axis = axes[1, 0]
    for row in data.itertuples(index=False):
        stress = bool(row.stress_condition)
        branch_color = BRANCH_LABEL_COLORS[str(row.Branch)]
        axis.scatter(
            float(row.score_difference),
            float(row.updated_regret),
            marker=BRANCH_MARKERS[str(row.Branch)],
            s=24,
            facecolor=STRESS if stress else branch_color,
            edgecolor="white",
            linewidth=0.55,
            alpha=0.95,
        )
    axis.axhline(0.01, color=BLACK, linestyle="--", lw=0.8)
    axis.axvline(0.0, color=GRAY, linestyle=":", lw=0.7)
    axis.text(
        0.98,
        0.94,
        "Regret bound = 0.01",
        transform=axis.transAxes,
        ha="right",
        va="top",
        fontsize=6.3,
    )
    axis.set_xlabel("Updated - original locking score")
    axis.set_ylabel("Updated selected regret")
    axis.set_title("Development-CV score preservation", fontsize=7.6, pad=5)
    clean_axis(axis)
    panel_label(axis, "c")

    axis = axes[1, 1]
    pool_counts = tie["pool_category"].astype(str).value_counts()
    decision_counts = tie["decision_stage"].value_counts()
    categories = [
        "One",
        "Two",
        "Three or more",
        "Singleton",
        "Jaccard",
        "Score",
        "Count",
        "Hash",
    ]
    counts = [
        int(pool_counts.get("1", 0)),
        int(pool_counts.get("2", 0)),
        int(pool_counts.get("3+", 0)),
        int(decision_counts.get("singleton_direct", 0)),
        int(decision_counts.get("unique_jaccard", 0)),
        int(decision_counts.get("higher_score", 0)),
        int(decision_counts.get("smaller_feature_count", 0)),
        int(decision_counts.get("stable_mask_hash", 0)),
    ]
    x = np.arange(len(categories), dtype=float)
    x[3:] += 1.15
    bars = axis.bar(
        x,
        counts,
        color=[GRAY, GRAY, GRAY] + [CURRENT] * 5,
        width=0.72,
        edgecolor="white",
        linewidth=0.4,
    )
    for bar, count in zip(bars, counts):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            count + 0.35,
            str(count),
            ha="center",
            va="bottom",
            fontsize=6.2,
        )
    axis.axvline(3.05, color=LIGHT_GRAY, lw=0.8)
    heading_y = max(counts) * 1.12
    axis.text(np.mean(x[:3]), heading_y, "Eligible-pool size", ha="center", va="bottom", fontsize=6.6)
    axis.text(np.mean(x[3:]), heading_y, "Selection decision", ha="center", va="bottom", fontsize=6.6)
    axis.set_xticks(x, categories, rotation=34, ha="right")
    axis.set_ylabel("Conditions, n")
    axis.set_ylim(0, max(counts) * 1.30)
    axis.set_title("Strict eligible-pool behavior", fontsize=7.6, pad=5)
    clean_axis(axis)
    panel_label(axis, "d")

    branch_handles = [
        Line2D(
            [0],
            [0],
            marker=marker,
            color="none",
            markerfacecolor=BRANCH_LABEL_COLORS[branch],
            markeredgecolor=BRANCH_LABEL_COLORS[branch],
            markersize=5,
            label=branch,
        )
        for branch, marker in BRANCH_MARKERS.items()
    ]
    branch_handles.append(
        Line2D(
            [0],
            [0],
            marker="o",
            color=STRESS,
            linewidth=1.2,
            markerfacecolor=STRESS,
            markeredgecolor="white",
            markersize=5,
            label="Prespecified stress condition",
        )
    )
    figure.legend(
        handles=branch_handles,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.004),
        ncol=4,
        fontsize=6.4,
        handletextpad=0.3,
        columnspacing=1.0,
    )
    figure.subplots_adjust(
        left=0.085,
        right=0.995,
        bottom=0.15,
        top=0.94,
        hspace=0.48,
        wspace=0.35,
    )
    return save_figure(figure)


def main() -> None:
    hashes = build()
    payload = {
        "figure": "Figure 2",
        "width_mm": 180,
        "conditions": 24,
        "maximum_selected_regret": 0.0083473,
        "held_out_inputs_used": False,
        "hashes": hashes,
    }
    (OUT / "MAIN_FIGURE2_HASHES.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", **payload}, sort_keys=True))


if __name__ == "__main__":
    main()
