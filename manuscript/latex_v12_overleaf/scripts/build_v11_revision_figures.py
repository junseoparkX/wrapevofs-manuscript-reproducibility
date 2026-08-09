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


HERE = Path(__file__).resolve().parent
V11 = HERE.parent
FIGURES = V11 / "figures"
OUT = V11 / "revision_outputs"
WIDTH_IN = 170.0 / 25.4
BLUE = "#0072B2"
GRAY = "#777777"
LIGHT_GRAY = "#C9C9C9"
BLACK = "#222222"
WARNING = "#D55E00"
DATASET_COLORS = {"AMP-AD": "#0072B2", "CGGA": "#6A51A3"}
DATASET_MARKERS = {"AMP-AD": "o", "CGGA": "s"}
BRANCH_MARKERS = {"SVM-L1": "o", "XGBoost": "s", "Boruta-RF": "D"}


mpl.rcParams.update(
    {
        "font.family": "DejaVu Sans",
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


def save_figure(figure: plt.Figure, stem: str) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for suffix in ("svg", "pdf", "png"):
        path = FIGURES / f"{stem}.{suffix}"
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


def build_s16() -> dict[str, str]:
    data = pd.read_csv(OUT / "S16_LOCKING_SENSITIVITY_PLOT_DATA.csv")
    figure, axes = plt.subplots(1, 3, figsize=(WIDTH_IN, 2.35))
    quantities = [
        ("pool_size", "Mean eligible-pool size", "Eligible-pool size"),
        (
            "mean_jaccard",
            "Selected mean Jaccard",
            "Eligible-pool representativeness",
        ),
        ("selected_regret", "Mean selected regret", "Empirical regret"),
    ]
    for axis, (column, ylabel, title), label in zip(axes, quantities, "abc"):
        for dataset in ("AMP-AD", "CGGA"):
            subset = data.loc[data["dataset"].eq(dataset)].sort_values("regret_tolerance")
            axis.plot(
                subset["regret_tolerance"],
                subset[column],
                color=DATASET_COLORS[dataset],
                marker=DATASET_MARKERS[dataset],
                markersize=4.0,
                markerfacecolor=("white" if dataset == "CGGA" else DATASET_COLORS[dataset]),
                markeredgecolor=DATASET_COLORS[dataset],
                linewidth=1.1,
                linestyle="--" if dataset == "CGGA" else "-",
                label=dataset,
            )
        axis.set_xlabel("Absolute regret tolerance")
        axis.set_ylabel(ylabel)
        axis.set_title(title, fontsize=7.6, fontweight="normal", pad=5)
        axis.set_xticks([0, 0.005, 0.01, 0.02], ["0", ".005", ".01", ".02"])
        clean_axis(axis)
        panel_label(axis, label)
    axes[0].legend(loc="upper left", fontsize=6.6)
    figure.subplots_adjust(left=0.085, right=0.995, bottom=0.22, top=0.84, wspace=0.43)
    return save_figure(figure, "figure_s16")


def slope_panel(
    axis: plt.Axes,
    data: pd.DataFrame,
    *,
    original: str,
    updated: str,
    ylabel: str,
    title: str,
    summary_text: str,
) -> None:
    for row in data.itertuples(index=False):
        original_value = float(getattr(row, original))
        updated_value = float(getattr(row, updated))
        stress = bool(row.stress_condition)
        branch = str(row.Branch)
        marker = BRANCH_MARKERS[branch]
        line_color = WARNING if stress else LIGHT_GRAY
        line_width = 1.4 if stress else 0.7
        axis.plot([0, 1], [original_value, updated_value], color=line_color, lw=line_width, zorder=1)
        axis.scatter(
            0,
            original_value,
            marker=marker,
            s=18,
            facecolor=GRAY,
            edgecolor="white",
            linewidth=0.45,
            zorder=2,
        )
        axis.scatter(
            1,
            updated_value,
            marker=marker,
            s=18,
            facecolor=WARNING if stress else BLUE,
            edgecolor="white",
            linewidth=0.45,
            zorder=2,
        )
        if stress:
            axis.annotate(
                "Rush/SVM-L1/Small",
                (1, updated_value),
                xytext=(0.54, 0.91),
                textcoords="axes fraction",
                arrowprops={"arrowstyle": "-", "color": WARNING, "lw": 0.7},
                fontsize=6.2,
                fontweight="normal",
                color=WARNING,
                ha="left",
                va="top",
            )
    axis.set_xticks([0, 1], ["Original", "Updated"])
    axis.set_xlim(-0.22, 1.22)
    axis.set_ylabel(ylabel)
    axis.set_title(title, fontsize=7.6, fontweight="normal", pad=5)
    axis.text(
        0.02,
        0.98,
        summary_text,
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontsize=6.2,
        fontweight="normal",
        color=BLACK,
    )
    clean_axis(axis)


def build_main_figure5() -> dict[str, str]:
    data = pd.read_csv(OUT / "S16_CONDITION_LEVEL_PAIRED.csv")
    tie = pd.read_csv(OUT / "ELIGIBLE_POOL_TIE_PATH_AUDIT.csv")
    figure, axes = plt.subplots(2, 2, figsize=(WIDTH_IN, 5.2))

    slope_panel(
        axes[0, 0],
        data,
        original="original_target_deviation",
        updated="updated_target_deviation",
        ylabel="Absolute target deviation",
        title="Matched target-size fidelity",
        summary_text="All: 216 -> 137; excluding stress: 135 -> 112",
    )
    panel_label(axes[0, 0], "a")

    slope_panel(
        axes[0, 1],
        data,
        original="original_all_zero_generations",
        updated="updated_all_zero_generations",
        ylabel="All-zero generations",
        title="Objective-flattening diagnostic",
        summary_text="All: 673 -> 333; excluding stress: 428 -> 267",
    )
    panel_label(axes[0, 1], "b")

    axis = axes[1, 0]
    for row in data.itertuples(index=False):
        stress = bool(row.stress_condition)
        axis.scatter(
            float(row.score_difference),
            float(row.updated_regret),
            marker=BRANCH_MARKERS[str(row.Branch)],
            s=24,
            facecolor=WARNING if stress else BLUE,
            edgecolor="white",
            linewidth=0.55,
            alpha=0.95,
        )
    axis.axhline(0.01, color=BLACK, linestyle="--", lw=0.8)
    axis.axvline(0.0, color=GRAY, linestyle=":", lw=0.7)
    axis.text(
        0.98,
        0.94,
        "Regret bound = .01",
        transform=axis.transAxes,
        ha="right",
        va="top",
        fontsize=6.3,
        fontweight="normal",
    )
    axis.set_xlabel("Updated - original locking score")
    axis.set_ylabel("Updated selected regret")
    axis.set_title("Development-CV score preservation", fontsize=7.6, fontweight="normal", pad=5)
    clean_axis(axis)
    panel_label(axis, "c")

    axis = axes[1, 1]
    pool_counts = tie["pool_category"].astype(str).value_counts()
    decision_counts = tie["decision_stage"].value_counts()
    categories = ["Pool 1", "Pool 2", "Pool >=3", "Singleton", "Jaccard", "Score", "Count", "Hash"]
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
    x[3:] += 0.8
    colors = [GRAY, GRAY, GRAY] + [BLUE] * 5
    bars = axis.bar(x, counts, color=colors, width=0.72, edgecolor="white", linewidth=0.4)
    for bar, count in zip(bars, counts):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            count + 0.35,
            str(count),
            ha="center",
            va="bottom",
            fontsize=6.2,
            fontweight="normal",
        )
    axis.axvline(2.9, color=LIGHT_GRAY, lw=0.7)
    axis.set_xticks(x, categories, rotation=35, ha="right")
    axis.set_ylabel("Conditions, n")
    axis.set_ylim(0, max(counts) * 1.18)
    axis.set_title("Strict eligible-pool behavior", fontsize=7.6, fontweight="normal", pad=5)
    clean_axis(axis)
    panel_label(axis, "d")

    branch_handles = [
        Line2D(
            [0],
            [0],
            marker=marker,
            color="none",
            markerfacecolor=BLUE,
            markeredgecolor="white",
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
            color="none",
            markerfacecolor=WARNING,
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
    figure.subplots_adjust(left=0.09, right=0.995, bottom=0.15, top=0.94, hspace=0.48, wspace=0.35)
    return save_figure(figure, "figure_5")


def main() -> None:
    hashes = {
        "figure_s16": build_s16(),
        "figure_5": build_main_figure5(),
    }
    (OUT / "V11_REVISION_FIGURE_HASHES.json").write_text(
        json.dumps(hashes, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "width_mm": 170, "figures": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
