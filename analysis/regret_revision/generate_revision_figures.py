"""Generate five journal-scale figures from audit tables."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "figures"
LATEX = ROOT / "manuscript" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
LATEX.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "axes.linewidth": 0.7,
        "lines.linewidth": 1.2,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
    }
)

DATASET_MARKERS = {"AMP-AD": "o", "CGGA": "s", "ADNI": "^"}
BRANCH_MARKERS = {"svm_l1": "o", "xgboost": "s", "boruta_rf": "^"}
RULE_STYLE = {
    "highest_development_cv_run": ("Highest development CV", "o", "white", "#1F5A6E"),
    "legacy_top_three_medoid": ("Legacy top-three medoid", "s", "#E8A23A", "#A96500"),
    "all_run_medoid": ("All-run medoid", "^", "#8E7DBE", "#5C4A8A"),
    "regret_constrained_medoid_abs_0.01": ("Regret medoid (0.01)", "D", "#2A9D6F", "#176B4C"),
}
DATASET_COLORS = {"AMP-AD": "#2A9D8F", "CGGA": "#D97706", "ADNI": "#6B7280"}
BRANCH_COLORS = {"svm_l1": "#2A9D8F", "xgboost": "#E69F00", "boruta_rf": "#D55E5A"}
TOLERANCES = (0.0, 0.005, 0.01, 0.02)


def panel_label(ax, label: str) -> None:
    ax.text(
        -0.10,
        1.04,
        label,
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        va="bottom",
    )


def finish(fig, number: int) -> None:
    fig.subplots_adjust(left=0.08, right=0.985, top=0.94, bottom=0.12, wspace=0.34, hspace=0.42)
    for target in (OUT / f"figure_{number}.png", LATEX / f"figure_{number}.png"):
        fig.savefig(target, dpi=320)
    fig.savefig(OUT / f"figure_{number}.svg")
    plt.close(fig)


def draw_box(ax, x, y, w, h, text, *, fill="white", dashed=False, lw=0.9):
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor=fill,
        edgecolor="black",
        linewidth=lw,
        linestyle="--" if dashed else "-",
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=7.2)
    return box


def figure1() -> None:
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 4.8), gridspec_kw={"height_ratios": [1.05, 0.95]})
    ax = axes[0]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    panel_label(ax, "a")
    labels = [
        "Supplied development\nmatrix",
        "Direct candidate\nset",
        "RFECV target\n$k^*$",
        "Repeated GA\nsearches",
        "Regret-eligible\npool",
        "Jaccard medoid\n+ deterministic ties",
    ]
    box_width = 0.135
    xs = np.linspace(0.015, 0.85, len(labels))
    for idx, (x, label) in enumerate(zip(xs, labels)):
        fill = "0.94" if idx in {2, 4, 5} else "white"
        draw_box(ax, x, 0.39, box_width, 0.28, label, fill=fill)
        if idx < len(labels) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (x + box_width, 0.53),
                    (xs[idx + 1], 0.53),
                    arrowstyle="-|>",
                    mutation_scale=9,
                    linewidth=0.8,
                    color="black",
                )
            )
    ax.text(0.015, 0.82, "Development only", fontsize=8.5, fontweight="bold")
    ax.plot([0.01, 0.985], [0.76, 0.76], color="black", lw=0.7)
    ax.text(
        0.50,
        0.18,
        r"Eligible when $L_{best}-L_r\leq\delta$; fallback expands by development score only",
        ha="center",
        fontsize=7.4,
    )

    ax = axes[1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    panel_label(ax, "b")
    draw_box(ax, 0.04, 0.56, 0.25, 0.24, "Lock configuration\nmetric, delta, seeds", fill="0.94")
    draw_box(ax, 0.375, 0.56, 0.25, 0.24, "Immutable audit\n+ locked signature", fill="0.86")
    draw_box(ax, 0.71, 0.56, 0.25, 0.24, "Held-out evaluation\nsecondary only", dashed=True)
    for left, right in ((0.29, 0.375), (0.625, 0.71)):
        ax.add_patch(
            FancyArrowPatch(
                (left, 0.68),
                (right, 0.68),
                arrowstyle="-|>",
                mutation_scale=10,
                linewidth=0.9,
                color="black",
            )
        )
    ax.axvline(0.675, ymin=0.38, ymax=0.94, color="black", lw=1.0, linestyle="--")
    ax.text(0.675, 0.91, "locking boundary", ha="center", va="bottom", fontsize=7.5)
    ax.text(
        0.50,
        0.20,
        "Held-out outcomes cannot select the strategy, tolerance, fitness mode, penalty, metric, or run.",
        ha="center",
        fontsize=7.5,
        fontweight="bold",
    )
    finish(fig, 1)


def figure2(compression: pd.DataFrame) -> None:
    data = compression[
        compression["selection_rule"].isin(RULE_STYLE)
        & compression["compression_ratio"].notna()
        & compression["development_cv_regret"].notna()
    ].copy()
    data.to_csv(HERE / "figure2_compression_regret_plot_data.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.45), gridspec_kw={"width_ratios": [1.18, 1]})
    ax = axes[0]
    for rule, (label, marker, face, edge) in RULE_STYLE.items():
        subset = data[data["selection_rule"] == rule]
        ax.scatter(
            100 * subset["compression_ratio"],
            subset["development_cv_regret"],
            s=24,
            marker=marker,
            facecolors=face,
            edgecolors=edge,
            linewidths=0.55,
            alpha=0.82,
            label=label,
        )
    ax.axhline(0.01, color="black", linestyle="--", lw=0.8, label="0.01 regret bound")
    ax.set_xlabel("Compression relative to Direct (%)")
    ax.set_ylabel("Development-CV regret")
    ax.set_xlim(-3, 100)
    ax.set_ylim(-0.0015, max(0.045, float(data["development_cv_regret"].max()) * 1.08))
    ax.grid(axis="both", color="0.88", lw=0.5)
    ax.legend(frameon=False, loc="upper left", ncol=1)
    panel_label(ax, "a")

    ax = axes[1]
    positions = np.arange(len(RULE_STYLE))
    labels = []
    for pos, (rule, (label, marker, face, edge)) in enumerate(RULE_STYLE.items()):
        values = data.loc[data["selection_rule"] == rule, "development_cv_regret"].dropna().to_numpy()
        q1, median, q3 = np.quantile(values, [0.25, 0.5, 0.75])
        ax.vlines(pos, q1, q3, color=edge, lw=4.0)
        ax.scatter(pos, median, marker=marker, s=40, facecolors=face, edgecolors=edge, zorder=3)
        labels.append(label.replace(" development CV", "\nCV").replace(" medoid", "\nmedoid"))
    ax.axhline(0.01, color="black", linestyle="--", lw=0.8)
    ax.set_xticks(positions, labels, rotation=0)
    ax.set_ylabel("Development-CV regret")
    ax.set_title("Median and interquartile range")
    ax.grid(axis="y", color="0.88", lw=0.5)
    panel_label(ax, "b")
    finish(fig, 2)


def figure3(sensitivity: pd.DataFrame) -> None:
    data = sensitivity[
        (sensitivity["status"] == "complete")
        & (sensitivity["tolerance_mode"] == "absolute")
    ].copy()
    data["regret_tolerance"] = pd.to_numeric(data["regret_tolerance"])
    summary = (
        data.groupby(["dataset", "regret_tolerance"], as_index=False)
        .agg(
            pool_size=("eligible_pool_size", "mean"),
            selected_regret=("absolute_regret", "mean"),
            mean_jaccard=("selected_mean_jaccard", "mean"),
            changed_from_best=("absolute_regret", lambda values: float(np.mean(np.asarray(values) > EPSILON))),
        )
    )
    summary.to_csv(HERE / "figure3_locking_sensitivity_plot_data.csv", index=False)
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.85))
    quantities = [
        ("pool_size", "Mean eligible pool size"),
        ("mean_jaccard", "Selected mean Jaccard"),
        ("selected_regret", "Mean selected regret"),
    ]
    for ax, (column, ylabel), label in zip(axes, quantities, "abc"):
        for dataset, marker in DATASET_MARKERS.items():
            subset = summary[summary["dataset"] == dataset].sort_values("regret_tolerance")
            if subset.empty:
                continue
            ax.plot(
                subset["regret_tolerance"],
                subset[column],
                marker=marker,
                markersize=4.5,
                markerfacecolor="white" if dataset == "CGGA" else DATASET_COLORS[dataset],
                markeredgecolor=DATASET_COLORS[dataset],
                color=DATASET_COLORS[dataset],
                linestyle="--" if dataset == "CGGA" else "-",
                label=dataset,
            )
        ax.set_xlabel("Absolute regret tolerance")
        ax.set_ylabel(ylabel)
        ax.set_xticks(TOLERANCES)
        ax.grid(axis="y", color="0.88", lw=0.5)
        panel_label(ax, label)
    axes[0].legend(frameon=False, loc="upper left")
    finish(fig, 3)


EPSILON = 1e-12


def figure4(penalty: pd.DataFrame) -> None:
    data = penalty.copy()
    data.to_csv(HERE / "figure4_penalty_flattening_plot_data.csv", index=False)
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.9))
    ax = axes[0]
    for branch, marker in BRANCH_MARKERS.items():
        subset = data[data["branch"] == branch]
        ax.scatter(
            subset["target_deviation"],
            subset["fraction_zero_legacy_fitness"],
            marker=marker,
            s=24,
            facecolors=BRANCH_COLORS[branch],
            edgecolors="white",
            linewidths=0.65,
            label=branch.replace("_", "-").upper(),
        )
    failure = data[data["known_failure_mode"]]
    ax.scatter(
        failure["target_deviation"],
        failure["fraction_zero_legacy_fitness"],
        marker="*",
        s=95,
        facecolors="#7F1D1D",
        edgecolors="#4C1111",
        label="AMP-AD failure mode",
        zorder=4,
    )
    ax.axhline(0.5, color="black", linestyle="--", lw=0.8)
    ax.set_xlabel(r"$|k-k^*|$")
    ax.set_ylabel("Zero legacy run-best fraction")
    ax.grid(color="0.88", lw=0.5)
    ax.legend(frameon=False, loc="lower right", fontsize=6.3)
    panel_label(ax, "a")

    ax = axes[1]
    for dataset, marker in DATASET_MARKERS.items():
        subset = data[data["dataset"] == dataset]
        if subset.empty:
            continue
        ax.scatter(
            subset["target_deviation"],
            subset["number_all_zero_generations"],
            marker=marker,
            s=25,
            facecolors="white" if dataset == "CGGA" else DATASET_COLORS[dataset],
            edgecolors=DATASET_COLORS[dataset],
            linewidths=0.6,
            label=dataset,
        )
    ax.set_xlabel(r"$|k-k^*|$")
    ax.set_ylabel("All-zero generations (of 250)")
    ax.grid(color="0.88", lw=0.5)
    ax.legend(frameon=False, loc="upper left")
    panel_label(ax, "b")

    ax = axes[2]
    warning_counts = (
        data.assign(warning=data["warning_status"].ne("none"))
        .groupby(["dataset", "warning"], as_index=False)
        .size()
    )
    datasets = sorted(data["dataset"].unique())
    total = data.groupby("dataset").size()
    warned = data.assign(w=data["warning_status"].ne("none")).groupby("dataset")["w"].sum()
    x = np.arange(len(datasets))
    values = [100 * warned.get(dataset, 0) / total[dataset] for dataset in datasets]
    ax.bar(
        x,
        values,
        width=0.58,
        color=[DATASET_COLORS[dataset] for dataset in datasets],
        edgecolor=[DATASET_COLORS[dataset] for dataset in datasets],
        linewidth=0.9,
        alpha=0.88,
    )
    ax.set_xticks(x, datasets)
    ax.set_ylabel("Configurations warned (%)")
    ax.set_ylim(0, 105)
    ax.grid(axis="y", color="0.88", lw=0.5)
    panel_label(ax, "c")
    finish(fig, 4)


def figure5(compression: pd.DataFrame) -> None:
    preferred = compression[
        (compression["selection_rule"] == "regret_constrained_medoid_abs_0.01")
        & compression["heldout_delta"].notna()
    ].copy()
    paired_path = HERE / "figure5_cgga_legacy_paired_intervals.csv"
    paired = pd.read_csv(paired_path)
    preferred.to_csv(HERE / "figure5_preferred_regret_heldout_points.csv", index=False)
    paired.to_csv(HERE / "figure5_cgga_legacy_paired_intervals.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    rng = np.random.default_rng(42)
    datasets = [dataset for dataset in ("AMP-AD", "CGGA") if dataset in set(preferred["dataset"])]
    for xpos, dataset in enumerate(datasets):
        subset = preferred[preferred["dataset"] == dataset]
        jitter = rng.uniform(-0.16, 0.16, size=len(subset))
        for branch, marker in BRANCH_MARKERS.items():
            pick = subset["branch"] == branch
            ax.scatter(
                np.full(int(pick.sum()), xpos) + jitter[pick.to_numpy()],
                subset.loc[pick, "heldout_delta"],
                marker=marker,
                s=27,
                facecolors="white",
                edgecolors="black",
                linewidths=0.65,
                label=branch.replace("_", "-").upper() if xpos == 0 else None,
            )
        ax.scatter(
            xpos,
            subset["heldout_delta"].median(),
            marker="D",
            s=38,
            color="black",
            zorder=4,
            label="Median" if xpos == 0 else None,
        )
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(range(len(datasets)), datasets)
    ax.set_ylabel("Locked minus Direct held-out AUROC")
    ax.set_title("Point differences; evaluated locked runs only")
    ax.grid(axis="y", color="0.88", lw=0.5)
    ax.legend(frameon=False, loc="lower left", fontsize=6.3)
    panel_label(ax, "a")

    ax = axes[1]
    auc = paired[paired["metric"] == "roc_auc"].reset_index(drop=True)
    y = np.arange(len(auc))
    ax.errorbar(
        auc["delta_full_medoid_minus_rfecv"],
        y,
        xerr=np.vstack(
            [
                auc["delta_full_medoid_minus_rfecv"] - auc["ci_low"],
                auc["ci_high"] - auc["delta_full_medoid_minus_rfecv"],
            ]
        ),
        fmt="s",
        markersize=4.2,
        markerfacecolor="white",
        markeredgecolor="black",
        ecolor="black",
        elinewidth=0.8,
        capsize=2,
    )
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(y, auc["method_label"])
    ax.set_xlabel("Legacy medoid minus RFECV-only AUROC")
    ax.set_title("CGGA paired bootstrap 95% intervals")
    ax.grid(axis="x", color="0.88", lw=0.5)
    panel_label(ax, "b")
    finish(fig, 5)


def main() -> None:
    compression = pd.read_csv(ROOT / "audits" / "compression_regret_summary.csv")
    sensitivity = pd.read_csv(ROOT / "audits" / "locking_rule_sensitivity.csv")
    penalty = pd.read_csv(ROOT / "audits" / "penalty_flattening_audit.csv")
    figure1()
    figure2(compression)
    figure3(sensitivity)
    figure4(penalty)
    figure5(compression)
    print(f"Generated main figures in {OUT} and {LATEX}")


if __name__ == "__main__":
    main()
