"""Build supplementary post-freeze AMP-AD and CGGA figures and tables.

The approved main Figures 4 and 5 are deliberately outside this builder. New
post-freeze analyses are additive Supplementary Figures S21--S23.
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

from figure_palette import BRANCH_COLORS, CURRENT, DARK, ORIGINAL

matplotlib.rcParams["svg.hashsalt"] = "WrapEvoFS-v12-postfreeze"


V12 = Path(__file__).resolve().parents[1]
ROOT = V12.parents[1]
FIGURES = V12 / "figures"
TABLES = V12 / "tables"
AMP = ROOT / "analysis/ampad_updated_one_time_heldout_20260808"
BENCH = ROOT / "analysis/cgga_coherent_benchmark_20260808/outputs"
NESTED = ROOT / "analysis/cgga_nested_relock_20260808/outputs"
NESTED_OLD = ROOT / "analysis/cgga_nested_validation/outputs/primary"
WIDTH = 170 / 25.4

COLORS = BRANCH_COLORS
LABELS = {"svm_l1": "SVM-L1", "xgboost": "XGBoost", "boruta_rf": "Boruta-RF"}
CAP_MARKERS = {"low": "o", "reference": "s"}


def style(axis: plt.Axes, panel: str, title: str) -> None:
    axis.grid(False)
    axis.spines[["top", "right"]].set_visible(False)
    axis.tick_params(labelsize=7, length=3)
    axis.set_title(title, fontsize=7.8, fontweight="normal", pad=7)
    axis.text(-0.14, 1.18, f"{panel})", transform=axis.transAxes, fontsize=11, fontweight="bold", va="top")


def save(figure: plt.Figure, stem: str) -> dict[str, str]:
    hashes = {}
    for extension in ["pdf", "svg", "png"]:
        path = FIGURES / f"{stem}.{extension}"
        if extension == "pdf":
            metadata = {"Creator": "WrapEvoFS build_postfreeze_results.py", "CreationDate": None, "ModDate": None}
        elif extension == "svg":
            metadata = {"Creator": "WrapEvoFS build_postfreeze_results.py", "Date": None}
        else:
            metadata = {"Software": "WrapEvoFS build_postfreeze_results.py"}
        figure.savefig(
            path,
            dpi=600 if extension == "png" else None,
            bbox_inches="tight",
            facecolor="white",
            metadata=metadata,
        )
        hashes[extension] = hashlib.sha256(path.read_bytes()).hexdigest()
    plt.close(figure)
    return hashes


def assert_ylabels_clear_left_neighbor(figure: plt.Figure, axes: np.ndarray, stem: str) -> None:
    """Fail the build if a right-hand panel's y labels intrude into the prior axes."""
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    for index in range(1, len(axes)):
        previous_axes = axes[index - 1].get_window_extent(renderer)
        for label in axes[index].get_yticklabels():
            if label.get_visible() and label.get_text().strip():
                if label.get_window_extent(renderer).overlaps(previous_axes):
                    raise RuntimeError(
                        f"{stem}: y-axis label '{label.get_text()}' intrudes into the preceding panel"
                    )


def build_amp_s21() -> dict[str, str]:
    metrics = pd.read_csv(AMP / "condition_metrics.csv")
    contrasts = pd.read_csv(AMP / "paired_condition_contrasts.csv")
    updated = metrics.loc[metrics["variant"] == "updated_regret_locked"].copy()
    centers = ["emory", "mayo", "mount_sinai", "rush"]
    center_labels = ["Emory", "Mayo", "Mount Sinai", "Rush"]
    figure, axes = plt.subplots(1, 3, figsize=(WIDTH, 3.05), gridspec_kw={"width_ratios": [1.00, 1.00, 1.00]})
    ax = axes[0]
    offsets = {"svm_l1": -0.18, "xgboost": 0.0, "boruta_rf": 0.18}
    for branch in ["svm_l1", "xgboost", "boruta_rf"]:
        for cap in ["low", "reference"]:
            part = updated.loc[(updated["branch"] == branch) & (updated["cap"] == cap)].set_index("center").loc[centers]
            x = np.arange(4) + offsets[branch]
            face = COLORS[branch] if cap == "reference" else "white"
            ax.scatter(x, part["macro_auroc"], s=28, marker=CAP_MARKERS[cap], facecolors=face, edgecolors=COLORS[branch], linewidth=1.2)
    ax.set_xticks(range(4), center_labels, rotation=25, ha="right")
    ax.set_ylabel("Held-out macro AUROC", fontsize=7.5)
    ax.set_ylim(0.60, 0.91)
    style(ax, "a", "Updated locked performance")
    row_order = [(b, c) for b in ["svm_l1", "xgboost", "boruta_rf"] for c in ["low", "reference"]]
    for panel, comparator, title in [
        (1, "archived_rfecv_only", "Versus RFECV-only"),
        (2, "archived_locked_medoid", "Versus original lock"),
    ]:
        ax = axes[panel]
        part = contrasts.loc[(contrasts["comparator"] == comparator) & (contrasts["metric"] == "macro_auroc")].set_index(["branch", "cap"])
        for y, (branch, cap) in enumerate(row_order):
            row = part.loc[(branch, cap)]
            marker = CAP_MARKERS[cap]
            face = COLORS[branch] if cap == "reference" else "white"
            ax.errorbar(row["updated_minus_comparator"], y, xerr=[[row["updated_minus_comparator"] - row["ci_low"]], [row["ci_high"] - row["updated_minus_comparator"]]], fmt=marker, ms=4.6, mfc=face, mec=COLORS[branch], ecolor=COLORS[branch], elinewidth=1.1, capsize=2)
        ax.axvline(0, color=DARK, lw=0.8)
        ax.set_yticks(range(6), [f"{LABELS[b]}  {'Small' if c == 'low' else 'Reference'}" for b, c in row_order])
        ax.tick_params(axis="y", labelsize=6.1, pad=1.5)
        ax.invert_yaxis()
        ax.set_xlim(-0.075, 0.075)
        ax.set_xlabel("Macro AUROC difference", fontsize=7.5)
        style(ax, chr(97 + panel), title)
    handles = [
        plt.Line2D([], [], marker="o", color=COLORS[b], markerfacecolor=COLORS[b], linestyle="", label=LABELS[b])
        for b in ["svm_l1", "xgboost", "boruta_rf"]
    ] + [
        plt.Line2D([], [], marker="o", color=DARK, markerfacecolor="white", linestyle="", label="Small cap"),
        plt.Line2D([], [], marker="s", color=DARK, markerfacecolor=DARK, linestyle="", label="Reference cap"),
    ]
    figure.legend(handles=handles, loc="lower center", ncol=5, frameon=False, fontsize=6.8, bbox_to_anchor=(0.5, -0.01), handletextpad=0.3, columnspacing=0.9)
    figure.subplots_adjust(left=0.075, right=0.995, top=0.89, bottom=0.25, wspace=0.88)
    assert_ylabels_clear_left_neighbor(figure, axes, "figure_s21")
    return save(figure, "figure_s21")


def build_benchmark_s22() -> dict[str, str]:
    metrics = pd.read_csv(BENCH / "benchmark_metrics.csv")
    intervals = pd.read_csv(BENCH / "benchmark_intervals.csv")
    contrasts = pd.read_csv(BENCH / "paired_regret_medoid_contrasts.csv")
    variants = ["rfecv_only", "elastic_net", "best_cv", "full_medoid", "unrestricted_medoid", "regret_medoid"]
    names = ["RFECV-only", "Elastic Net", "Highest CV", "Top-3 medoid", "Full-bank medoid", "Regret medoid"]
    offsets = {"svm_l1": -0.20, "xgboost": 0.0, "boruta_rf": 0.20}
    figure, axes = plt.subplots(1, 3, figsize=(WIDTH, 3.45), gridspec_kw={"width_ratios": [0.82, 1.05, 1.13]})
    for panel, value, title, xlabel in [
        (0, "n_features", "Signature size", "Selected features"),
        (1, "auroc", "Held-out AUROC", "Held-out AUROC"),
    ]:
        ax = axes[panel]
        for branch in ["svm_l1", "xgboost", "boruta_rf"]:
            part = metrics.loc[metrics["method"] == branch].set_index("variant").loc[variants]
            y = np.arange(len(variants)) + offsets[branch]
            if value == "auroc":
                ci = intervals.loc[(intervals["method"] == branch) & (intervals["metric"] == "auroc")].set_index("variant").loc[variants]
                ax.errorbar(part[value], y, xerr=np.vstack([part[value].to_numpy() - ci["ci_low"].to_numpy(), ci["ci_high"].to_numpy() - part[value].to_numpy()]), fmt="o", ms=4, color=COLORS[branch], ecolor=COLORS[branch], elinewidth=0.9, capsize=1.5)
            else:
                ax.scatter(part[value], y, s=18, color=COLORS[branch])
        ax.set_yticks(range(len(variants)), names)
        ax.invert_yaxis()
        ax.set_xlabel(xlabel, fontsize=7.5)
        style(ax, chr(97 + panel), title)
        if panel == 1:
            ax.tick_params(labelleft=False)
    ax = axes[2]
    comparators = ["rfecv_only", "elastic_net", "best_cv", "full_medoid", "unrestricted_medoid"]
    comparator_names = ["RFECV-only", "Elastic Net", "Highest CV", "Top-3 medoid", "Full-bank medoid"]
    for branch in ["svm_l1", "xgboost", "boruta_rf"]:
        part = contrasts.loc[(contrasts["method"] == branch) & (contrasts["metric"] == "auroc")].set_index("comparator").loc[comparators]
        y = np.arange(len(comparators)) + offsets[branch]
        ax.errorbar(part["difference"], y, xerr=np.vstack([part["difference"].to_numpy() - part["ci_low"].to_numpy(), part["ci_high"].to_numpy() - part["difference"].to_numpy()]), fmt="o", ms=4, color=COLORS[branch], ecolor=COLORS[branch], elinewidth=0.9, capsize=1.5)
    ax.axvline(0, color=DARK, lw=0.8)
    ax.set_yticks(range(len(comparators)), comparator_names)
    ax.tick_params(axis="y", labelsize=6.2, pad=1.5)
    ax.invert_yaxis()
    ax.set_xlabel("Regret medoid minus comparator AUROC", fontsize=7.5)
    ax.set_xlim(-0.17, 0.22)
    style(ax, "c", "Paired AUROC contrasts")
    handles = [plt.Line2D([], [], marker="o", color=COLORS[b], linestyle="", label=LABELS[b]) for b in ["svm_l1", "xgboost", "boruta_rf"]]
    figure.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=7, bbox_to_anchor=(0.5, -0.01))
    figure.subplots_adjust(left=0.12, right=0.995, top=0.86, bottom=0.20, wspace=0.75)
    assert_ylabels_clear_left_neighbor(figure, axes, "figure_s22")
    return save(figure, "figure_s22")


def build_nested_s23() -> dict[str, str]:
    selections = pd.read_csv(NESTED / "fold_selection_comparison.csv")
    old_fold = pd.read_csv(NESTED_OLD / "fold_metrics.csv")
    new_predictions = pd.read_csv(NESTED / "outer_fold_predictions.csv")
    new_fold = []
    from sklearn.metrics import roc_auc_score
    for fold, group in new_predictions.groupby("outer_fold"):
        new_fold.append((fold, roc_auc_score(group["y_true"], group["probability"])))
    new_fold = dict(new_fold)
    old_summary = json.loads((NESTED_OLD / "nested_validation_summary.json").read_text(encoding="utf-8"))
    new_summary = json.loads((NESTED / "summary.json").read_text(encoding="utf-8"))
    figure, axes = plt.subplots(1, 3, figsize=(WIDTH, 2.7))
    folds = np.arange(1, 6)
    axes[0].plot(folds, selections["legacy_selected_run_id"], "o-", color=ORIGINAL, label="Legacy")
    axes[0].plot(folds, selections["upgraded_selected_run_id"], "o-", color=CURRENT, label="Current")
    axes[0].set_xticks(folds)
    axes[0].set_xlabel("Outer fold", fontsize=7.5)
    axes[0].set_ylabel("Selected run ID", fontsize=7.5)
    style(axes[0], "a", "Saved-bank selections")
    axes[1].plot(folds, old_fold.set_index("outer_fold").loc[folds, "outer_auroc"], "o-", color=ORIGINAL)
    axes[1].plot(folds, [new_fold[x] for x in folds], "o-", color=CURRENT)
    axes[1].set_xticks(folds)
    axes[1].set_xlabel("Outer fold", fontsize=7.5)
    axes[1].set_ylabel("Outer-fold AUROC", fontsize=7.5)
    style(axes[1], "b", "Fold-level evaluation")
    metric_keys = ["auroc", "auprc", "balanced_accuracy"]
    metric_names = ["AUROC", "AUPRC", "Balanced\naccuracy"]
    for offset, (summary, color, label) in enumerate([(old_summary, ORIGINAL, "Legacy"), (new_summary, CURRENT, "Current")]):
        y = np.arange(3) + (-0.09 if offset == 0 else 0.09)
        estimates = np.asarray([summary["metrics"][key] for key in metric_keys])
        lows = np.asarray([summary["bootstrap_95_ci"][key][0] for key in metric_keys])
        highs = np.asarray([summary["bootstrap_95_ci"][key][1] for key in metric_keys])
        axes[2].errorbar(estimates, y, xerr=np.vstack([estimates - lows, highs - estimates]), fmt="o", color=color, ecolor=color, ms=4, capsize=2, label=label)
    axes[2].set_yticks(range(3), metric_names)
    axes[2].tick_params(axis="y", labelsize=6.4, pad=1.5)
    axes[2].invert_yaxis()
    axes[2].set_xlabel("OOF estimate (95% bootstrap CI)", fontsize=7.5)
    style(axes[2], "c", "Overall OOF sensitivity")
    handles = [plt.Line2D([], [], marker="o", color=ORIGINAL, label="Legacy top-3 lock"), plt.Line2D([], [], marker="o", color=CURRENT, label="Current regret lock")]
    figure.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=7, bbox_to_anchor=(0.5, -0.01))
    figure.subplots_adjust(left=0.08, right=0.995, top=0.88, bottom=0.23, wspace=0.72)
    assert_ylabels_clear_left_neighbor(figure, axes, "figure_s23")
    return save(figure, "figure_s23")


def latex_escape(value: str) -> str:
    return value.replace("_", "\\_").replace("%", "\\%")


def build_tables() -> None:
    metrics = pd.read_csv(AMP / "condition_metrics.csv")
    contrasts = pd.read_csv(AMP / "paired_condition_contrasts.csv")
    amp_rows = []
    for branch in ["svm_l1", "xgboost", "boruta_rf"]:
        for cap in ["low", "reference"]:
            point = metrics.loc[(metrics.branch == branch) & (metrics.cap == cap) & (metrics.variant == "updated_regret_locked"), "macro_auroc"].mean()
            cells = []
            for comparator in ["archived_rfecv_only", "archived_locked_medoid"]:
                row = contrasts.loc[(contrasts.branch == branch) & (contrasts.cap == cap) & (contrasts.comparator == comparator) & (contrasts.metric == "macro_auroc")].iloc[0]
                cells.append(f"{row.updated_minus_comparator:+.3f} [{row.ci_low:+.3f}, {row.ci_high:+.3f}]")
            amp_rows.append(f"{LABELS[branch]} & {'Small' if cap == 'low' else 'Reference'} & {point:.3f} & {cells[0]} & {cells[1]} \\\\")
    table44 = """\\begin{table}[p]
\\centering
\\caption{AMP-AD one-time post-freeze held-out evaluation of the 24 updated conditions}
\\label{tab:supp22}
\\scriptsize
\\begin{tabular}{llccc}
\\toprule
Branch & Cap & Mean center AUROC & Updated $-$ RFECV-only & Updated $-$ original lock \\\\
\\midrule
""" + "\n".join(amp_rows) + """
\\bottomrule
\\end{tabular}
\\begin{minipage}{0.98\\linewidth}\\scriptsize\\vspace{0.3em}
Point estimates in the fourth and fifth columns are pooled four-center macro-AUROC differences with 95\\% intervals from 2,000 common resamples stratified by held-out center and true class (seed 42). The 24 development locks and protocol hash were frozen before held-out labels or outcomes were loaded. The evaluation was performed once and did not trigger reselection, refitting, or parameter changes. This is post-freeze cross-center evaluation, not prospective clinical or independent external validation.
\\end{minipage}
\\end{table}
"""
    (TABLES / "table_44.tex").write_text(table44, encoding="utf-8")
    benchmark = pd.read_csv(BENCH / "benchmark_metrics.csv")
    interval = pd.read_csv(BENCH / "benchmark_intervals.csv")
    variant_names = {"rfecv_only": "RFECV-only", "elastic_net": "Elastic Net", "best_cv": "Highest CV", "full_medoid": "Legacy top-3 medoid", "unrestricted_medoid": "Full-bank medoid", "regret_medoid": "Regret medoid"}
    method_order = ["svm_l1", "xgboost", "boruta_rf"]
    variant_order = ["rfecv_only", "elastic_net", "best_cv", "full_medoid", "unrestricted_medoid", "regret_medoid"]
    benchmark["method_order"] = pd.Categorical(benchmark.method, method_order, ordered=True)
    benchmark["variant_order"] = pd.Categorical(benchmark.variant, variant_order, ordered=True)
    benchmark = benchmark.sort_values(["method_order", "variant_order"])
    rows = []
    for row in benchmark.itertuples(index=False):
        ci = interval.loc[(interval.method == row.method) & (interval.variant == row.variant) & (interval.metric == "auroc")].iloc[0]
        rows.append(f"{row.method_label} & {variant_names[row.variant]} & {int(row.n_features)} & {row.auroc:.3f} [{ci.ci_low:.3f}, {ci.ci_high:.3f}] & {row.auprc:.3f} & {row.balanced_accuracy:.3f} \\\\")
    table45 = """\\begin{table}[p]
\\centering
\\caption{CGGA coherent same-split, same-estimator benchmark}
\\label{tab:supp23}
\\scriptsize
\\begin{tabular}{llrccc}
\\toprule
Branch & Development-derived signature & Features & Held-out AUROC (95\\% CI) & AUPRC & Balanced accuracy \\\\
\\midrule
""" + "\n".join(rows) + """
\\bottomrule
\\end{tabular}
\\begin{minipage}{0.98\\linewidth}\\scriptsize\\vspace{0.3em}
All signatures use the same fixed 214/92 split and the same 500-tree random forest (maximum depth 12, minimum leaf size 2, balanced class weighting, random state 42). Feature selection was completed within development data before held-out evaluation. Intervals use 2,000 class-stratified resamples (seed 42). Elastic Net signatures were size matched within branch. No comparison establishes predictive superiority; paired contrasts are shown in Figure~5c and supplied machine-readable outputs.
\\end{minipage}
\\end{table}
"""
    (TABLES / "table_45.tex").write_text(table45, encoding="utf-8")
    selections = pd.read_csv(NESTED / "fold_selection_comparison.csv")
    old_fold = pd.read_csv(NESTED_OLD / "fold_metrics.csv").set_index("outer_fold")
    new_predictions = pd.read_csv(NESTED / "outer_fold_predictions.csv")
    from sklearn.metrics import roc_auc_score
    nested_rows = []
    for row in selections.itertuples(index=False):
        group = new_predictions.loc[new_predictions.outer_fold == row.outer_fold]
        new_auc = roc_auc_score(group.y_true, group.probability)
        nested_rows.append(f"{row.outer_fold} & {row.legacy_selected_run_id} & {row.upgraded_selected_run_id} & {row.upgraded_n_features} & {row.eligible_pool_size} & {row.upgraded_absolute_regret:.4f} & {old_fold.loc[row.outer_fold, 'outer_auroc']:.3f} & {new_auc:.3f} \\\\")
    table46 = """\\begin{table}[p]
\\centering
\\caption{CGGA saved nested-bank re-locking under the current regret-constrained rule}
\\label{tab:supp24}
\\scriptsize
\\begin{tabular}{rrrrrrrr}
\\toprule
Fold & Legacy run & Current run & Current features & Eligible & Regret & Legacy AUROC & Current AUROC \\\\
\\midrule
""" + "\n".join(nested_rows) + """
\\bottomrule
\\end{tabular}
\\begin{minipage}{0.98\\linewidth}\\scriptsize\\vspace{0.3em}
This post hoc internal sensitivity reuses five archived candidate banks from a reduced CPU search budget (20 individuals, 12 generations, five runs) and does not rerun the GA or access the original 92-participant held-out cohort. Current locking changed the selected run in all five outer folds. OOF AUROC was 0.692 for the archived top-three lock and 0.667 for the current lock; this adverse result is retained because the regret guarantee concerns the configured development score gap, not predictive superiority.
\\end{minipage}
\\end{table}
"""
    (TABLES / "table_46.tex").write_text(table46, encoding="utf-8")


def main() -> None:
    hashes = {
        "figure_s21": build_amp_s21(),
        "figure_s22": build_benchmark_s22(),
        "figure_s23": build_nested_s23(),
    }
    build_tables()
    manifest = {
        "target_width_mm": 170,
        "background_grid": False,
        "panel_label_policy": "bold panel letters only",
        "figure_hashes": hashes,
        "source_outputs": [str(AMP), str(BENCH), str(NESTED), str(NESTED_OLD)],
        "simulation_included": False,
    }
    (V12 / "POSTFREEZE_ANALYSIS_FIGURE_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
