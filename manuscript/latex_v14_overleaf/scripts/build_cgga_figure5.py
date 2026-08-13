"""Build the results-focused V12 main Figure 5 from frozen CGGA summaries.

No participant-level input, model object, or prediction row is read. The script
only renders pre-existing aggregate performance, paired-bootstrap, and five-run
agreement summaries copied into ``supplementary_data/cgga_figure5``.
"""

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

from figure_palette import BRANCH_COLORS, DARK, LIGHT, MID


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "supplementary_data" / "cgga_figure5"
FIGURES = ROOT / "figures"

METHOD_ORDER = ["svm_l1", "xgboost", "boruta_rf"]
METHOD_LABEL = {"svm_l1": "SVM-L1", "xgboost": "XGBoost", "boruta_rf": "Boruta-RF"}
METHOD_COLOR = BRANCH_COLORS
METHOD_MARKER = {"svm_l1": "o", "xgboost": "s", "boruta_rf": "D"}
METRIC_ORDER = ["roc_auc", "auprc", "balanced_accuracy"]
METRIC_MARKER = {"roc_auc": "o", "auprc": "s", "balanced_accuracy": "D"}
METRIC_SHORT = {"roc_auc": "AUROC", "auprc": "AUPRC", "balanced_accuracy": "Bal. acc."}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(
        -0.17,
        1.15,
        f"{label})",
        transform=ax.transAxes,
        fontsize=10.2,
        fontweight="bold",
        color=DARK,
        ha="left",
        va="top",
    )


def validate_inputs(compression: pd.DataFrame, effects: pd.DataFrame, agreement: pd.DataFrame) -> None:
    expected_methods = set(METHOD_ORDER)
    if set(compression["method"]) != expected_methods or len(compression) != 6:
        raise AssertionError("Panel a must contain Direct and locked rows for exactly three branches.")
    if set(compression["variant"]) != {"direct", "locked_medoid"}:
        raise AssertionError("Panel a variants do not match the frozen comparison.")
    if len(effects) != 9 or set(effects["method"]) != expected_methods or set(effects["metric"]) != set(METRIC_ORDER):
        raise AssertionError("Panel b must contain three metrics for each of three branches.")
    if not ((effects["ci_low"] <= effects["difference"]) & (effects["difference"] <= effects["ci_high"])).all():
        raise AssertionError("A paired point estimate lies outside its interval.")
    if not ((effects["ci_low"] <= 0) & (effects["ci_high"] >= 0)).all():
        raise AssertionError("The frozen claim that all nine intervals include zero is not satisfied.")
    if set(effects["n_bootstrap"]) != {2000} or set(effects["bootstrap_seed"]) != {42}:
        raise AssertionError("Unexpected paired-bootstrap configuration.")
    if len(agreement) != 6 or set(agreement["method"]) != expected_methods:
        raise AssertionError("Panel c must contain two guidance conditions for each branch.")
    if set(agreement["condition"]) != {"no_penalty", "penalty"}:
        raise AssertionError("Panel c guidance conditions are incomplete.")
    numeric_blocks = [
        compression[["n_features", "estimate", "ci_low", "ci_high"]],
        effects[["difference", "ci_low", "ci_high"]],
        agreement[["mean_feature_count", "mean_pairwise_jaccard", "nogueira_agreement"]],
    ]
    if not all(np.isfinite(block.to_numpy(dtype=float)).all() for block in numeric_blocks):
        raise AssertionError("Figure 5 source data contain a nonfinite value.")


def draw_compression(ax: plt.Axes, frame: pd.DataFrame) -> None:
    for method in METHOD_ORDER:
        part = frame.loc[frame["method"].eq(method)].set_index("variant")
        direct = part.loc["direct"]
        locked = part.loc["locked_medoid"]
        color = METHOD_COLOR[method]
        marker = METHOD_MARKER[method]
        ax.annotate(
            "",
            xy=(locked["n_features"], locked["estimate"]),
            xytext=(direct["n_features"], direct["estimate"]),
            arrowprops={"arrowstyle": "-|>", "lw": 1.05, "color": color, "alpha": 0.72},
            zorder=1,
        )
        for row, filled in ((direct, False), (locked, True)):
            ax.errorbar(
                row["n_features"],
                row["estimate"],
                yerr=[[row["estimate"] - row["ci_low"]], [row["ci_high"] - row["estimate"]]],
                fmt=marker,
                markersize=5.3,
                markerfacecolor=color if filled else "white",
                markeredgecolor=color,
                markeredgewidth=1.0,
                color=color,
                ecolor=color,
                elinewidth=0.9,
                capsize=2.2,
                zorder=3,
            )
        midpoint_x = (float(direct["n_features"]) + float(locked["n_features"])) / 2
        label_y = {"svm_l1": 0.612, "xgboost": 0.736, "boruta_rf": 0.714}[method]
        ax.text(
            midpoint_x,
            label_y,
            f"\N{MINUS SIGN}{100 * float(locked['feature_reduction']):.0f}%",
            color=color,
            fontsize=6.8,
            fontweight="bold",
            ha="center",
            va="bottom",
            bbox={"boxstyle": "round,pad=0.16", "facecolor": "white", "edgecolor": "none", "alpha": 0.94},
            zorder=6,
        )
    ax.set_xlim(0, 80)
    ax.set_ylim(0.48, 0.82)
    ax.set_xticks([0, 20, 40, 60, 80])
    ax.set_yticks([0.50, 0.60, 0.70, 0.80])
    ax.set_xlabel("Selected features")
    ax.set_ylabel("Held-out AUROC")
    ax.set_title("Compression and AUROC", fontsize=8.3, fontweight="normal", pad=8)
    stage_handles = [
        Line2D([], [], marker="o", linestyle="none", markerfacecolor="white", markeredgecolor=MID,
               markersize=4.7, label="Direct"),
        Line2D([], [], marker="o", linestyle="none", markerfacecolor=MID, markeredgecolor=MID,
               markersize=4.7, label="Locked"),
    ]
    ax.legend(handles=stage_handles, frameon=False, fontsize=5.8, ncol=2, loc="lower right",
              handletextpad=0.25, columnspacing=0.7, borderaxespad=0.2)
    panel_label(ax, "a")


def draw_incremental_effects(ax: plt.Axes, frame: pd.DataFrame) -> None:
    base_y = {"svm_l1": 2.0, "xgboost": 1.0, "boruta_rf": 0.0}
    offsets = {"roc_auc": 0.19, "auprc": 0.0, "balanced_accuracy": -0.19}
    for method in METHOD_ORDER:
        for metric in METRIC_ORDER:
            row = frame.loc[frame["method"].eq(method) & frame["metric"].eq(metric)].iloc[0]
            y = base_y[method] + offsets[metric]
            ax.errorbar(
                row["difference"],
                y,
                xerr=[[row["difference"] - row["ci_low"]], [row["ci_high"] - row["difference"]]],
                fmt=METRIC_MARKER[metric],
                markersize=4.5,
                markerfacecolor=METHOD_COLOR[method],
                markeredgecolor=METHOD_COLOR[method],
                color=METHOD_COLOR[method],
                ecolor=METHOD_COLOR[method],
                elinewidth=0.9,
                capsize=1.8,
                zorder=3,
            )
    ax.axvline(0, color=MID, linewidth=0.8, zorder=0)
    ax.set_xlim(-0.15, 0.15)
    ax.set_xticks([-0.15, -0.075, 0, 0.075, 0.15])
    ax.set_xticklabels(["-0.15", "-0.075", "0", "+0.075", "+0.15"])
    ax.set_ylim(-0.46, 2.64)
    ax.set_yticks([2, 1, 0], [METHOD_LABEL[m] for m in METHOD_ORDER])
    for tick, method in zip(ax.get_yticklabels(), METHOD_ORDER):
        tick.set_color(METHOD_COLOR[method])
    ax.set_xlabel("Locked - RFECV-only")
    ax.set_title("Increment beyond RFECV", fontsize=8.3, fontweight="normal", pad=8)
    handles = [
        Line2D([], [], marker=METRIC_MARKER[m], linestyle="none", color=DARK, markersize=4.2,
               label=METRIC_SHORT[m])
        for m in METRIC_ORDER
    ]
    ax.legend(handles=handles, frameon=False, fontsize=5.2, ncol=3, loc="upper center",
              handletextpad=0.15, columnspacing=0.45, borderaxespad=0.3)
    panel_label(ax, "b")


def draw_agreement(ax: plt.Axes, frame: pd.DataFrame) -> None:
    metric_specs = [
        ("mean_pairwise_jaccard", "o", -0.13),
        ("nogueira_agreement", "D", 0.13),
    ]
    for index, method in enumerate(METHOD_ORDER):
        part = frame.loc[frame["method"].eq(method)].set_index("condition")
        for column, marker, metric_offset in metric_specs:
            x_open = index + metric_offset - 0.026
            x_filled = index + metric_offset + 0.026
            y_open = float(part.loc["no_penalty", column])
            y_filled = float(part.loc["penalty", column])
            color = METHOD_COLOR[method]
            ax.plot([x_open, x_filled], [y_open, y_filled], color=color, linewidth=0.85, alpha=0.72)
            ax.scatter(x_open, y_open, s=25, marker=marker, facecolor="white", edgecolor=color,
                       linewidth=1.0, zorder=3)
            ax.scatter(x_filled, y_filled, s=25, marker=marker, facecolor=color, edgecolor=color,
                       linewidth=1.0, zorder=3)
    ax.axhline(0, color=LIGHT, linewidth=0.8, zorder=0)
    ax.set_xlim(-0.45, 2.45)
    ax.set_ylim(-0.06, 0.60)
    ax.set_xticks(range(3), [METHOD_LABEL[m] for m in METHOD_ORDER])
    for tick, method in zip(ax.get_xticklabels(), METHOD_ORDER):
        tick.set_color(METHOD_COLOR[method])
    ax.set_ylabel("Agreement coefficient")
    ax.set_title("Five-run agreement", fontsize=8.3, fontweight="normal", pad=8)
    metric_handles = [
        Line2D([], [], marker="o", linestyle="none", color=DARK, markerfacecolor=DARK,
               markersize=4.2, label="Jaccard"),
        Line2D([], [], marker="D", linestyle="none", color=DARK, markerfacecolor=DARK,
               markersize=3.9, label="Nogueira"),
    ]
    condition_handles = [
        Line2D([], [], marker="o", linestyle="none", color=DARK, markerfacecolor="white",
               markersize=4.2, label="No guidance"),
        Line2D([], [], marker="o", linestyle="none", color=DARK, markerfacecolor=DARK,
               markersize=4.2, label="Guided"),
    ]
    metric_legend = ax.legend(handles=metric_handles, frameon=False, fontsize=5.0, ncol=1,
                              loc="upper left", handletextpad=0.2, borderaxespad=0.35)
    ax.add_artist(metric_legend)
    ax.legend(handles=condition_handles, frameon=False, fontsize=5.0, ncol=1,
              loc="upper right", handletextpad=0.2, borderaxespad=0.35)
    panel_label(ax, "c")


def main() -> None:
    compression_path = DATA / "panel_a_compression_auroc.csv"
    effects_path = DATA / "panel_b_locked_minus_rfecv.csv"
    agreement_path = DATA / "panel_c_five_run_agreement.csv"
    compression = pd.read_csv(compression_path)
    effects = pd.read_csv(effects_path)
    agreement = pd.read_csv(agreement_path)
    validate_inputs(compression, effects, agreement)

    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 6.5,
            "axes.labelsize": 6.8,
            "axes.titlesize": 8.3,
            "xtick.labelsize": 5.7,
            "ytick.labelsize": 5.7,
            "axes.edgecolor": DARK,
            "axes.labelcolor": DARK,
            "xtick.color": DARK,
            "ytick.color": DARK,
            "text.color": DARK,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.75,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "wrapevofs-v12-cgga-figure5-results",
        }
    )
    figure, axes = plt.subplots(1, 3, figsize=(6.6929, 3.55), gridspec_kw={"width_ratios": [1, 1, 1]})
    draw_compression(axes[0], compression)
    draw_incremental_effects(axes[1], effects)
    draw_agreement(axes[2], agreement)
    figure.subplots_adjust(left=0.075, right=0.995, bottom=0.19, top=0.80, wspace=0.48)

    outputs = []
    for extension in ("pdf", "svg", "png"):
        path = FIGURES / f"figure_5.{extension}"
        if extension == "pdf":
            metadata = {
                "Creator": "WrapEvoFS build_cgga_figure5.py",
                "Producer": "Matplotlib",
                "CreationDate": None,
                "ModDate": None,
            }
        elif extension == "svg":
            metadata = {
                "Creator": "WrapEvoFS build_cgga_figure5.py",
                "Date": None,
                "Title": "Figure 5 CGGA compression, incremental effects, and agreement",
            }
        else:
            metadata = {"Software": "WrapEvoFS build_cgga_figure5.py"}
        figure.savefig(path, dpi=600, facecolor="white", metadata=metadata)
        outputs.append({"path": f"figures/{path.name}", "sha256": sha256_file(path)})
    plt.close(figure)

    source_paths = [
        compression_path,
        effects_path,
        agreement_path,
        DATA / "README.md",
        DATA / "requirements.txt",
    ]
    manifest = {
        "figure": "Figure 5",
        "target_width_mm": 170,
        "layout": "one row; three equal-size panels",
        "background_grid": False,
        "panel_labels": ["a)", "b)", "c)"],
        "panel_label_style": "bold and equal size",
        "ga_rerun": False,
        "model_refit": False,
        "heldout_predictions_regenerated": False,
        "all_nine_paired_intervals_include_zero": True,
        "render_environment": {
            "python": "3.12",
            "matplotlib": mpl.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
        "outputs": outputs,
        "source_files": [
            {"path": f"supplementary_data/cgga_figure5/{path.name}", "sha256": sha256_file(path)}
            for path in source_paths
        ],
    }
    manifest_path = DATA / "figure5_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
