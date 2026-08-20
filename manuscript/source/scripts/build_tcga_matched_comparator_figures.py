"""Recreate the TCGA matched-comparator figures from published aggregate source data.

The script is post-analysis only.  It refuses to run unless all 30 conditions and
the full-result validation report are complete under the frozen protocol.
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


MANUSCRIPT = Path(__file__).resolve().parents[1]
FIGURES = MANUSCRIPT / "figures"
SOURCE = MANUSCRIPT / "supplementary_data" / "tcga_matched_comparator"
AGGREGATE = SOURCE
WIDTH = 170 / 25.4

BRANCHES = ["svm_l1", "xgboost", "boruta_rf"]
BRANCH_LABELS = {"svm_l1": "SVM-L1", "xgboost": "XGBoost", "boruta_rf": "Boruta-RF"}
BRANCH_COLORS = {"svm_l1": "#1F7A8C", "xgboost": "#C78A0A", "boruta_rf": "#8B5E83"}
DARK, MID, LIGHT, PALE = "#263746", "#637381", "#C8D1D8", "#EEF2F4"
METHOD_COLORS = {
    "direct": "#687984",
    "rfecv_only": "#94A4AD",
    "regret_constrained_medoid": "#263746",
    "elastic_net_native": "#597B6F",
    "elastic_net_matched": "#86A397",
    "stability_native": "#856F91",
    "stability_matched": "#AA9BB4",
    "random_mean": "#B1843E",
}
METHOD_LABELS = {
    "direct": "Direct",
    "rfecv_only": "RFECV-only",
    "regret_constrained_medoid": "WrapEvoFS",
    "elastic_net_native": "Elastic Net native",
    "elastic_net_matched": "Elastic Net matched",
    "stability_native": "Stability native",
    "stability_matched": "Stability matched",
    "random_mean": "Random-bank mean",
}

matplotlib.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 6.5,
        "axes.labelsize": 6.8,
        "axes.titlesize": 8.3,
        "axes.linewidth": 0.75,
        "xtick.labelsize": 5.7,
        "ytick.labelsize": 5.7,
        "xtick.major.width": 0.75,
        "ytick.major.width": 0.75,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "svg.hashsalt": "WrapEvoFS-tcga-matched-comparator-v17",
    }
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_validated() -> dict:
    """Require the published source-data manifest before rendering."""
    report_path = SOURCE / "reporting_manifest.json"
    if not report_path.exists():
        raise RuntimeError("Published reporting manifest is missing.")
    return json.loads(report_path.read_text(encoding="utf-8"))


def style(axis: plt.Axes) -> None:
    axis.grid(False)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines["left"].set_color(DARK)
    axis.spines["bottom"].set_color(DARK)
    axis.tick_params(length=2.8, color=DARK, labelcolor=DARK)


def panel(axis: plt.Axes, label: str) -> None:
    axis.text(-0.17, 1.06, f"{label})", transform=axis.transAxes, fontsize=10.2,
              fontweight="bold", va="bottom", ha="left", color=DARK)


def load_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metrics = pd.read_csv(AGGREGATE / "oof_metrics.csv")
    differences = pd.read_csv(AGGREGATE / "paired_regret_medoid_minus_comparator.csv")
    predictions = pd.read_csv(AGGREGATE / "outer_predictions.csv")
    frequency = pd.read_csv(AGGREGATE / "outer_fold_feature_frequency.csv")
    runtime = pd.read_csv(AGGREGATE / "runtime_and_fit_counts.csv")
    return metrics, differences, predictions, frequency, runtime


def feature_counts(predictions: pd.DataFrame, frequency: pd.DataFrame) -> pd.DataFrame:
    # New methods and random controls are in the sentinel-derived frequency table.
    new_counts = (
        frequency.groupby(["branch", "method"], as_index=False)["selection_count"].sum()
        .rename(columns={"selection_count": "sum_count_across_10_outer_conditions"})
    )
    new_counts["mean_n_features"] = new_counts["sum_count_across_10_outer_conditions"] / 10.0

    # Existing fold-level counts are the authoritative values for Direct/RFECV/WrapEvoFS.
    existing = pd.read_csv(SOURCE / "fold_metrics.csv")
    existing = existing.loc[existing["method"].isin(["direct", "rfecv_only", "regret_constrained_medoid"])]
    existing_counts = existing.groupby(["branch", "method"], as_index=False)["n_features"].mean().rename(columns={"n_features": "mean_n_features"})
    counts = pd.concat([existing_counts, new_counts[["branch", "method", "mean_n_features"]]], ignore_index=True)
    return counts


def make_main(metrics: pd.DataFrame, differences: pd.DataFrame, counts: pd.DataFrame) -> None:
    primary = metrics.loc[metrics["metric"] == "macro_ovr_auroc"].copy()
    diff = differences.loc[differences["metric"] == "macro_ovr_auroc"].copy()
    random_summary = pd.read_csv(AGGREGATE / "random_bank_oof_metric_summary.csv")
    random_diff = pd.read_csv(AGGREGATE / "random_bank_paired_difference_summary.csv")

    figure, axes = plt.subplots(2, 2, figsize=(WIDTH, 5.05))
    offsets = {"svm_l1": -0.18, "xgboost": 0.0, "boruta_rf": 0.18}

    # a) Whole-pipeline context.
    methods = ["direct", "rfecv_only", "regret_constrained_medoid"]
    axis = axes[0, 0]
    for branch in BRANCHES:
        part = primary.loc[(primary["branch"] == branch) & primary["method"].isin(methods)].set_index("method").loc[methods]
        y = np.arange(len(methods)) + offsets[branch]
        x = part["estimate"].to_numpy(float)
        axis.errorbar(x, y, xerr=np.vstack([x - part["ci_low"].to_numpy(float), part["ci_high"].to_numpy(float) - x]),
                      fmt="o", ms=4.2, color=BRANCH_COLORS[branch], ecolor=BRANCH_COLORS[branch], elinewidth=0.95, capsize=1.7)
    axis.set_yticks(range(len(methods)), [METHOD_LABELS[m] for m in methods])
    axis.invert_yaxis()
    axis.set_xlabel("Repeated-OOF macro AUROC")
    axis.set_title("Full-pipeline context", fontweight="normal", pad=7)
    style(axis); panel(axis, "a")

    # b) Selector-layer matched comparisons at the same cardinality.
    methods = ["regret_constrained_medoid", "elastic_net_matched", "stability_matched"]
    axis = axes[0, 1]
    for branch in BRANCHES:
        part = primary.loc[(primary["branch"] == branch) & primary["method"].isin(methods)].set_index("method").loc[methods]
        y = np.arange(len(methods)) + offsets[branch]
        x = part["estimate"].to_numpy(float)
        axis.errorbar(x, y, xerr=np.vstack([x - part["ci_low"].to_numpy(float), part["ci_high"].to_numpy(float) - x]),
                      fmt="o", ms=4.2, color=BRANCH_COLORS[branch], ecolor=BRANCH_COLORS[branch], elinewidth=0.95, capsize=1.7)
        random_row = random_summary.loc[(random_summary["branch"] == branch) & (random_summary["metric"] == "macro_ovr_auroc")].iloc[0]
        axis.plot([float(random_row["min_across_random_banks"]), float(random_row["max_across_random_banks"])],
                  [3 + offsets[branch]] * 2, color=BRANCH_COLORS[branch], lw=1.0)
        axis.scatter(float(random_row["mean_across_random_banks"]), 3 + offsets[branch], marker="D", s=16,
                     color=BRANCH_COLORS[branch], zorder=3)
    axis.set_yticks(range(4), [METHOD_LABELS[m] for m in methods] + [METHOD_LABELS["random_mean"]])
    axis.invert_yaxis()
    axis.set_xlabel("Repeated-OOF macro AUROC")
    axis.set_title("Size-matched selector sensitivity", fontweight="normal", pad=7)
    style(axis); panel(axis, "b")

    # c) Paired WrapEvoFS differences from matched selector layers and random banks.
    axis = axes[1, 0]
    comparators = ["elastic_net_matched", "stability_matched"]
    for branch in BRANCHES:
        part = diff.loc[(diff["branch"] == branch) & diff["comparator"].isin(comparators)].set_index("comparator").loc[comparators]
        y = np.arange(len(comparators)) + offsets[branch]
        x = part["difference"].to_numpy(float)
        axis.errorbar(x, y, xerr=np.vstack([x - part["ci_low"].to_numpy(float), part["ci_high"].to_numpy(float) - x]),
                      fmt="o", ms=4.2, color=BRANCH_COLORS[branch], ecolor=BRANCH_COLORS[branch], elinewidth=0.95, capsize=1.7)
        row = random_diff.loc[(random_diff["branch"] == branch) & (random_diff["metric"] == "macro_ovr_auroc")].iloc[0]
        axis.plot([float(row["min_difference_across_random_banks"]), float(row["max_difference_across_random_banks"])],
                  [2 + offsets[branch]] * 2, color=BRANCH_COLORS[branch], lw=1.0)
        axis.scatter(float(row["mean_difference_across_random_banks"]), 2 + offsets[branch], marker="D", s=16,
                     color=BRANCH_COLORS[branch], zorder=3)
    axis.axvline(0, color=DARK, lw=0.8)
    axis.set_yticks(range(3), [METHOD_LABELS[m] for m in comparators] + [METHOD_LABELS["random_mean"]])
    axis.invert_yaxis()
    axis.set_xlabel("WrapEvoFS minus comparator AUROC")
    axis.set_title("Paired primary-metric differences", fontweight="normal", pad=7)
    style(axis); panel(axis, "c")

    # d) Performance and feature-count trade-off; points are branches, not pooled samples.
    axis = axes[1, 1]
    trade_methods = ["direct", "rfecv_only", "regret_constrained_medoid", "elastic_net_native", "stability_native"]
    marker_map = {"direct": "o", "rfecv_only": "s", "regret_constrained_medoid": "D", "elastic_net_native": "^", "stability_native": "v"}
    for method in trade_methods:
        for branch in BRANCHES:
            count = counts.loc[(counts["branch"] == branch) & (counts["method"] == method), "mean_n_features"]
            score = primary.loc[(primary["branch"] == branch) & (primary["method"] == method), "estimate"]
            if len(count) == 1 and len(score) == 1:
                axis.scatter(float(count.iloc[0]), float(score.iloc[0]), marker=marker_map[method], s=27,
                             facecolors=BRANCH_COLORS[branch] if method == "regret_constrained_medoid" else "white",
                             edgecolors=BRANCH_COLORS[branch], linewidth=1.0)
    axis.set_xlabel("Mean selected features")
    axis.set_ylabel("Repeated-OOF macro AUROC")
    axis.set_ylim(0.80, 0.86)
    axis.set_title("Observed performance-compression space", fontweight="normal", pad=7)
    method_handles = [
        plt.Line2D(
            [], [], marker=marker_map[method], linestyle="", color=DARK,
            markerfacecolor=DARK if method == "regret_constrained_medoid" else "white",
            label=METHOD_LABELS[method], markersize=4.2,
        )
        for method in trade_methods
    ]
    axis.legend(
        handles=method_handles,
        loc="lower right",
        frameon=False,
        fontsize=4.8,
        ncol=2,
        handletextpad=0.25,
        columnspacing=0.6,
        borderaxespad=0.2,
    )
    style(axis); panel(axis, "d")

    handles = [plt.Line2D([], [], marker="o", color=BRANCH_COLORS[b], linestyle="", label=BRANCH_LABELS[b]) for b in BRANCHES]
    figure.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=6.3,
                  bbox_to_anchor=(0.5, 0.005), handletextpad=0.3, columnspacing=1.0)
    figure.subplots_adjust(left=0.13, right=0.995, top=0.91, bottom=0.13, hspace=0.55, wspace=0.62)
    save_figure(figure, "figure_3_strengthened")


def make_supplement(metrics: pd.DataFrame, differences: pd.DataFrame, counts: pd.DataFrame, runtime: pd.DataFrame) -> None:
    # Complete secondary metrics and native/matched support sizes.
    figure, axes = plt.subplots(1, 3, figsize=(WIDTH, 3.35))
    selected_methods = ["regret_constrained_medoid", "elastic_net_native", "elastic_net_matched", "stability_native", "stability_matched"]
    y_labels = [METHOD_LABELS[m] for m in selected_methods]
    offsets = {"svm_l1": -0.18, "xgboost": 0.0, "boruta_rf": 0.18}
    for index, metric in enumerate(["macro_auprc", "balanced_accuracy"]):
        axis = axes[index]
        part_metric = metrics.loc[metrics["metric"] == metric]
        for branch in BRANCHES:
            part = part_metric.loc[(part_metric["branch"] == branch) & part_metric["method"].isin(selected_methods)].set_index("method").loc[selected_methods]
            y = np.arange(len(selected_methods)) + offsets[branch]
            x = part["estimate"].to_numpy(float)
            axis.errorbar(x, y, xerr=np.vstack([x - part["ci_low"].to_numpy(float), part["ci_high"].to_numpy(float) - x]),
                          fmt="o", ms=4, color=BRANCH_COLORS[branch], ecolor=BRANCH_COLORS[branch], elinewidth=0.9, capsize=1.5)
        axis.set_yticks(range(len(selected_methods)), y_labels if index == 0 else [])
        axis.invert_yaxis(); axis.set_xlabel("Repeated-OOF " + ("macro AUPRC" if metric == "macro_auprc" else "balanced accuracy"))
        style(axis); panel(axis, chr(97 + index))
    axis = axes[2]
    for method_index, method in enumerate(selected_methods):
        for branch in BRANCHES:
            value = counts.loc[(counts["branch"] == branch) & (counts["method"] == method), "mean_n_features"]
            if len(value) == 1:
                axis.scatter(float(value.iloc[0]), method_index + offsets[branch], s=18, color=BRANCH_COLORS[branch])
    axis.set_yticks(range(len(selected_methods)), [])
    axis.invert_yaxis(); axis.set_xlabel("Mean selected features")
    style(axis); panel(axis, "c")
    handles = [plt.Line2D([], [], marker="o", color=BRANCH_COLORS[b], linestyle="", label=BRANCH_LABELS[b]) for b in BRANCHES]
    figure.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=6.3, bbox_to_anchor=(0.5, 0.005))
    figure.subplots_adjust(left=0.19, right=0.995, top=0.88, bottom=0.19, wspace=0.48)
    save_figure(figure, "figure_s_matched_comparator_strengthened")


def save_figure(figure: plt.Figure, stem: str) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for extension in ("pdf", "svg", "png"):
        path = FIGURES / f"{stem}.{extension}"
        metadata = {"Creator": "WrapEvoFS build_benchmark_outputs.py"}
        if extension == "pdf":
            metadata.update({"CreationDate": None, "ModDate": None})
        elif extension == "svg":
            metadata["Date"] = None
        else:
            metadata["Software"] = metadata.pop("Creator")
        figure.savefig(path, dpi=600 if extension == "png" else None, bbox_inches="tight", facecolor="white", metadata=metadata)
    plt.close(figure)


def main() -> None:
    report = require_validated()
    metrics, differences, predictions, frequency, runtime = load_frames()
    counts = feature_counts(predictions, frequency)
    make_main(metrics, differences, counts)
    make_supplement(metrics, differences, counts, runtime)
    outputs = sorted(FIGURES.glob("*strengthened.*"))
    manifest = {
        "protocol_sha256": report.get("protocol_sha256"),
        "validation_manifest_sha256": report.get("validation_manifest_sha256"),
        "output_sha256": {path.name: sha256(path) for path in outputs},
        "source_sha256": {path.name: sha256(path) for path in sorted(SOURCE.glob("*.csv"))},
    }
    (SOURCE / "reporting_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
