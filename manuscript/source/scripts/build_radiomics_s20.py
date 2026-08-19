"""Build Supplementary Figure S20 and aggregate radiomics source summaries.

The script consumes only non-identifying aggregate CSV/JSON files stored under
``supplementary_data/private_radiomics``. It never reads participant-level
matrices or held-out prediction rows.
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

from figure_palette import CURRENT, DARK, FEATURE_SPACE_COLORS, OCHRE, SAGE, TERRACOTTA


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "supplementary_data" / "private_radiomics"
FIGURES = ROOT / "figures"
COLORS = FEATURE_SPACE_COLORS
MARKERS = {"svm_l1": "o", "xgboost": "s", "boruta_rf": "^"}
BRANCH_LABELS = {"svm_l1": "SVM-L1", "xgboost": "XGBoost", "boruta_rf": "Boruta-RF"}
VIEW_LABELS = {"full_1781": "Full 1,781", "stable_1346": "Filtered 1,346"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def panel_label(ax: plt.Axes, label: str) -> None:
    ax.text(-0.13, 1.06, f"{label})", transform=ax.transAxes, fontsize=10, fontweight="bold", va="top")


def draw_cohort(ax: plt.Axes) -> None:
    ax.set_axis_off()
    neutral = DARK
    muted = "#A0AEC0"

    # A restrained cohort timeline avoids flowchart-style boxes.
    x_positions = [0.08, 0.36, 0.64, 0.92]
    counts = ["326", "262", "259", "197"]
    stage_labels = ["Source\npatients", "T1ce\neligible", "Radiomics\ncomplete", "MGMT linked\n(80/117)"]
    ax.plot([x_positions[0], x_positions[-1]], [0.72, 0.72], transform=ax.transAxes,
            color=muted, linewidth=1.0, solid_capstyle="round", zorder=1)
    ax.scatter(x_positions, [0.72] * 4, transform=ax.transAxes, s=31,
               facecolor=["white", "white", "white", neutral], edgecolor=neutral,
               linewidth=1.0, zorder=2)
    for x, count, label in zip(x_positions, counts, stage_labels):
        ax.text(x, 0.82, count, transform=ax.transAxes, ha="center", va="center",
                fontsize=8.5, fontweight="normal")
        ax.text(x, 0.61, label, transform=ax.transAxes, ha="center", va="top",
                fontsize=5.9, fontweight="normal", linespacing=1.05)

    # The bar preserves the actual 137/60 fixed split at a glance.
    split_left, split_right = 0.08, 0.92
    split_at = split_left + (split_right - split_left) * (137 / 197)
    ax.text(split_left, 0.43, "Fixed patient-level split", transform=ax.transAxes,
            ha="left", va="center", fontsize=6.2, fontweight="normal")
    ax.plot([split_left, split_at], [0.36, 0.36], transform=ax.transAxes,
            color=neutral, linewidth=7.0, solid_capstyle="butt")
    ax.plot([split_at, split_right], [0.36, 0.36], transform=ax.transAxes,
            color="#CBD5E0", linewidth=7.0, solid_capstyle="butt")
    ax.text((split_left + split_at) / 2, 0.29, "Development 137\n81/56", transform=ax.transAxes,
            ha="center", va="top", fontsize=5.9, fontweight="normal", linespacing=1.05)
    ax.text((split_at + split_right) / 2, 0.29, "Held out 60\n36/24", transform=ax.transAxes,
            ha="center", va="top", fontsize=5.9, fontweight="normal", linespacing=1.05)

    ax.text(0.08, 0.09, "Feature spaces", transform=ax.transAxes,
            ha="left", va="center", fontsize=6.2, fontweight="normal")
    ax.scatter([0.43, 0.72], [0.09, 0.09], transform=ax.transAxes, s=20,
               color=[COLORS["full_1781"], COLORS["stable_1346"]])
    ax.text(0.46, 0.09, "Full 1,781", transform=ax.transAxes,
            ha="left", va="center", fontsize=5.9, fontweight="normal")
    ax.text(0.75, 0.09, "Filtered 1,346", transform=ax.transAxes,
            ha="left", va="center", fontsize=5.9, fontweight="normal")
    ax.set_title("Cohort and fixed split", loc="left", fontsize=8.3, fontweight="normal", pad=2)
    panel_label(ax, "a")


def draw_compression(ax: plt.Axes, compression: pd.DataFrame) -> None:
    stage_x = {"Input": 0, "Direct": 1, "RFECV target": 2, "Locked": 4}
    for view in VIEW_LABELS:
        for branch in BRANCH_LABELS:
            subset = compression.query("view == @view and branch == @branch")
            main = subset[subset["stage"].isin(stage_x)].copy()
            main["x"] = main["stage"].map(stage_x)
            main = main.sort_values("x")
            color = COLORS[view]
            marker = MARKERS[branch]
            ax.plot(main["x"], main["feature_count"], color=color, alpha=0.48, lw=0.9)
            ax.scatter(main["x"], main["feature_count"], color=color, marker=marker, s=25,
                       edgecolor="white", linewidth=0.4, zorder=3)
            ga = subset[subset["stage"].str.startswith("GA seed")]
            jitter = np.linspace(-0.15, 0.15, len(ga))
            ax.scatter(3 + jitter, ga["feature_count"], color=color, marker=marker, s=17,
                       alpha=0.75, edgecolor="white", linewidth=0.3)
    ax.set_yscale("log")
    ax.set_xticks(range(5), ["Input", "Direct", "RFECV", "5 GA\nruns", "Locked"])
    ax.set_ylabel("Feature count (log scale)")
    ax.set_title("Feature-count trajectory", loc="left", fontsize=8.3, fontweight="normal", pad=2)
    handles = [
        mpl.lines.Line2D([], [], color=COLORS[view], marker="o", lw=1, label=VIEW_LABELS[view])
        for view in VIEW_LABELS
    ] + [
        mpl.lines.Line2D([], [], color="#4A5568", marker=MARKERS[branch], lw=0, label=BRANCH_LABELS[branch])
        for branch in BRANCH_LABELS
    ]
    ax.legend(handles=handles, frameon=False, fontsize=5.7, ncol=2, loc="upper right",
              handlelength=1.4, columnspacing=0.8)
    panel_label(ax, "b")


def draw_seed_agreement(ax: plt.Axes, stability: pd.DataFrame) -> None:
    ordered = stability.assign(
        view_order=pd.Categorical(stability["view"], ["full_1781", "stable_1346"], ordered=True),
        branch_order=pd.Categorical(stability["branch"], ["svm_l1", "xgboost", "boruta_rf"], ordered=True),
    ).sort_values(["view_order", "branch_order"])
    x = np.arange(len(ordered))
    ax.scatter(x - 0.10, ordered["mean_pairwise_jaccard_all_five"], color=CURRENT, marker="o", s=26,
               label="Mean Jaccard")
    ax.scatter(x + 0.10, ordered["nogueira_stability_all_five"], color=TERRACOTTA, marker="D", s=21,
               label="Nogueira")
    ax.axhline(0, color=DARK, linewidth=0.7)
    labels = [
        ("Full" if row.view == "full_1781" else "Filtered") + "\n" + BRANCH_LABELS[row.branch]
        for row in ordered.itertuples()
    ]
    ax.set_xticks(x, labels, rotation=32, ha="right", rotation_mode="anchor")
    ax.set_ylim(-0.10, 1.03)
    ax.set_ylabel("Agreement coefficient")
    ax.set_title("Five-seed agreement", loc="left", fontsize=8.3, fontweight="normal", pad=2)
    ax.legend(frameon=False, fontsize=6.2, loc="upper left")
    panel_label(ax, "c")


def draw_effects(ax: plt.Axes, effects: pd.DataFrame) -> None:
    rows = []
    for view in ("full_1781", "stable_1346"):
        for branch in ("svm_l1", "xgboost", "boruta_rf"):
            rows.append(effects.query(
                "view == @view and branch == @branch and comparison == 'Locked - Direct'"
            ).iloc[0])
    for branch in ("svm_l1", "xgboost", "boruta_rf"):
        rows.append(effects.query(
            "view == 'stable_vs_full' and branch == @branch and comparison == 'Stable locked - Full locked'"
        ).iloc[0])
    plot = pd.DataFrame(rows).reset_index(drop=True)
    y = np.arange(len(plot))[::-1]
    labels = []
    for index, row in plot.iterrows():
        view = row["view"]
        color = COLORS.get(view, SAGE)
        ax.errorbar(
            row["delta"], y[index],
            xerr=[[row["delta"] - row["ci_low"]], [row["ci_high"] - row["delta"]]],
            fmt=MARKERS[row["branch"]], color=color, ecolor=color, elinewidth=0.9,
            capsize=2.0, markersize=4.2,
        )
        if view == "stable_vs_full":
            labels.append("Filtered−Full " + BRANCH_LABELS[row["branch"]])
        else:
            labels.append(("Full " if view == "full_1781" else "Filtered ") + BRANCH_LABELS[row["branch"]])
    ax.axvline(0, color=DARK, linewidth=0.8)
    ax.set_yticks(y, labels)
    ax.set_xlim(-0.32, 0.20)
    ax.set_xlabel("Paired held-out AUROC difference (95% CI)")
    ax.set_title("Locked−Direct and feature-space effects", loc="left", fontsize=8.3, fontweight="normal", pad=2)
    panel_label(ax, "d")


def write_derived_summary(locking: pd.DataFrame, stability: pd.DataFrame, effects: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for view in ("full_1781", "stable_1346"):
        for branch in ("svm_l1", "xgboost", "boruta_rf"):
            lock_row = locking.query("view == @view and branch == @branch").iloc[0]
            stab_row = stability.query("view == @view and branch == @branch").iloc[0]
            audit = pd.read_csv(DATA / f"{view}__{branch}__locking_candidate_audit.csv")
            selected_features = set(json.loads(audit.loc[audit["selected"], "canonical_features"].iloc[0]))
            other_view = "stable_1346" if view == "full_1781" else "full_1781"
            other_audit = pd.read_csv(DATA / f"{other_view}__{branch}__locking_candidate_audit.csv")
            other_features = set(json.loads(other_audit.loc[other_audit["selected"], "canonical_features"].iloc[0]))
            cross_jaccard = len(selected_features & other_features) / len(selected_features | other_features)
            effect = effects.query(
                "view == @view and branch == @branch and comparison == 'Locked - Direct'"
            ).iloc[0]
            rows.append(
                {
                    "view": view,
                    "branch": branch,
                    "direct_feature_count": int(lock_row["direct_feature_count"]),
                    "rfecv_target_k": int(lock_row["rfecv_target_k"]),
                    "locked_feature_count": int(lock_row["locked_feature_count"]),
                    "compression_vs_direct": 1 - int(lock_row["locked_feature_count"]) / int(lock_row["direct_feature_count"]),
                    "eligible_pool_size": int(stab_row["eligible_pool_size"]),
                    "selected_absolute_regret": float(stab_row["selected_absolute_regret"]),
                    "mean_pairwise_jaccard_all_five": float(stab_row["mean_pairwise_jaccard_all_five"]),
                    "nogueira_stability_all_five": float(stab_row["nogueira_stability_all_five"]),
                    "duplicate_masks_present": bool((audit["duplicate_mask_multiplicity"] > 1).any()),
                    "cross_view_locked_jaccard": cross_jaccard,
                    "locked_minus_direct_auroc": float(effect["delta"]),
                    "locked_minus_direct_ci_low": float(effect["ci_low"]),
                    "locked_minus_direct_ci_high": float(effect["ci_high"]),
                }
            )
    frame = pd.DataFrame(rows)
    frame.to_csv(DATA / "radiomics_condition_summary.csv", index=False)
    return frame


def main() -> None:
    compression = pd.read_csv(DATA / "compression_trajectory.csv")
    locking = pd.read_csv(DATA / "locking_summary.csv")
    stability = pd.read_csv(DATA / "seed_stability_summary.csv")
    effects = pd.read_csv(DATA / "paired_heldout_effects.csv")
    summary = write_derived_summary(locking, stability, effects)

    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 6.8,
            "axes.labelsize": 7.0,
            "axes.titlesize": 8.3,
            "xtick.labelsize": 5.8,
            "ytick.labelsize": 5.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "wrapevofs-radiomics-s20",
        }
    )
    figure = plt.figure(figsize=(6.6929, 7.35), constrained_layout=True)
    grid = figure.add_gridspec(2, 2, height_ratios=[0.86, 1.14], width_ratios=[0.94, 1.06])
    draw_cohort(figure.add_subplot(grid[0, 0]))
    draw_compression(figure.add_subplot(grid[0, 1]), compression)
    draw_seed_agreement(figure.add_subplot(grid[1, 0]), stability)
    draw_effects(figure.add_subplot(grid[1, 1]), effects)

    outputs = []
    for extension in ("pdf", "svg", "png"):
        path = FIGURES / f"figure_s20.{extension}"
        if extension == "pdf":
            metadata = {
                "Creator": "WrapEvoFS build_radiomics_s20.py",
                "Producer": "Matplotlib",
                "CreationDate": None,
                "ModDate": None,
            }
        elif extension == "svg":
            metadata = {
                "Creator": "WrapEvoFS build_radiomics_s20.py",
                "Date": None,
                "Title": "Supplementary Figure S20 VGH brain-tumour radiomics",
            }
        else:
            metadata = {"Software": "WrapEvoFS build_radiomics_s20.py"}
        figure.savefig(
            path,
            dpi=300,
            bbox_inches="tight",
            facecolor="white",
            metadata=metadata,
        )
        outputs.append({"path": f"figures/{path.name}", "sha256": sha256_file(path)})
    plt.close(figure)

    sources = sorted(path for path in DATA.iterdir() if path.is_file() and path.name != "radiomics_figure_manifest.json")
    manifest = {
        "figure": "Supplementary Figure S20",
        "target_width_mm": 170,
        "background_grid": False,
        "participant_level_inputs_read": False,
        "heldout_prediction_rows_read": False,
        "outputs": outputs,
        "source_files": [{"path": f"supplementary_data/private_radiomics/{path.name}", "sha256": sha256_file(path)} for path in sources],
        "summary_rows": len(summary),
    }
    (DATA / "radiomics_figure_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
