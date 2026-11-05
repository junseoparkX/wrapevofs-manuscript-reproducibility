"""Plot fixed-bank CV-score perturbation sensitivity from reproduced results.

All 54 banks, both weighting schemes and all four selection policies are used.
No fitting or selection tuning is performed in this plotting script.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "supplementary_data/cv_score_sensitivity/results"
WORK = ROOT / "v19_work/supplement_polish_20261105/modern/s29"
FIGURES = ROOT / "v19_work/supplement_polish_20261105/modern/figures"
sys.path.insert(0, str(ROOT / "scripts"))
from audit_panel_alignment import require_matplotlib_panel_alignment
from v19_build_figures23 import configure, validate_text

POLICIES = ["highest_score", "legacy_top3", "unrestricted_medoid", "regret_medoid"]
POLICY_LABELS = ["Highest\nscore", "Legacy\ntop-three", "Full-bank\nmedoid", "Regret\nmedoid"]
POLICY_SHORT = ["Highest score", "Legacy top-three", "Full-bank medoid", "Regret medoid"]
POLICY_SHAPES = dict(zip(POLICIES, ["o", "s", "^", "v"]))
SCHEMES = ["leave_one_fold_out", "fold_bootstrap"]
SCHEME_TITLES = ["Leave one fold out", "Fold bootstrap"]
COHORTS = ["TCGA", "AMPAD"]
COHORT_COLORS = {"TCGA": "#386A8B", "AMPAD": "#8A6B98"}
COHORT_SHAPES = {"TCGA": "o", "AMPAD": "s"}
BRANCHES = ["svm_l1", "xgboost", "boruta_rf"]
BRANCH_LABELS = ["SVM-L1", "XGBoost", "Boruta-RF"]
NAME = "supp_figure_s29_cv_score_sensitivity"


def main() -> None:
    (WORK / "source_data").mkdir(parents=True, exist_ok=True)
    configure()
    mpl.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
                         "svg.fonttype": "none", "pdf.fonttype": 42,
                         "font.size": 6.7, "axes.labelsize": 6.7,
                         "xtick.labelsize": 6.3, "ytick.labelsize": 6.3,
                         "legend.fontsize": 6.3})
    source_names = ["bank_policy_summary.csv", "group_policy_summary.csv",
                    "paired_bank_comparison.csv", "weight_vectors.csv"]
    banks = pd.read_csv(SOURCE / source_names[0], float_precision="round_trip")
    groups = pd.read_csv(SOURCE / source_names[1], float_precision="round_trip")
    weights = pd.read_csv(SOURCE / "weight_vectors.csv", float_precision="round_trip")
    assert len(banks) == 54 * 2 * 4
    assert banks.bank_id.nunique() == 54
    assert banks.groupby(["scheme", "policy"]).size().eq(54).all()
    assert banks.groupby(["cohort", "branch", "scheme", "policy"]).size().isin([8, 10]).all()
    assert len(weights[weights.scheme == SCHEMES[0]]) == 5
    assert len(weights[weights.scheme == SCHEMES[1]]) == 126
    for scheme in SCHEMES:
        assert np.isclose(weights[weights.scheme == scheme].probability.sum(), 1)
    # Source group summaries must equal descriptive equal-bank aggregation.
    for cohort in ["ALL54", *COHORTS]:
        for scheme in SCHEMES:
            for policy in POLICIES:
                subset = banks[(banks.scheme == scheme) & (banks.policy == policy)]
                if cohort != "ALL54":
                    subset = subset[subset.cohort == cohort]
                row = groups[(groups["group"] == cohort) & (groups.scheme == scheme) & (groups.policy == policy)].iloc[0]
                assert len(subset) == int(row.banks)
                for src_col, out_col in [("retention_probability", "retention_probability"),
                                         ("mean_perturbed_score_gap", "mean_perturbed_score_gap"),
                                         ("probability_gap_above_delta", "mean_probability_gap_above_delta")]:
                    assert np.isclose(subset[src_col].mean(), row[out_col], atol=1e-14)

    fig = plt.figure(figsize=(170 / 25.4, 145 / 25.4))
    heat_axes = [fig.add_axes([x, .665, .29, .25], label=letter)
                 for x, letter in [(.18, "a"), (.68, "b")]]
    c_axes = [fig.add_axes([x, .185, .17, .265], label=label)
              for x, label in [(.115, "c_lofo"), (.355, "c_boot")]]
    d = fig.add_axes([.65, .185, .325, .265], label="d")
    for x, y, letter in [(.035, .94, "a"), (.535, .94, "b"),
                          (.035, .465, "c"), (.57, .465, "d")]:
        fig.text(x, y, letter, fontsize=10, weight="bold", va="bottom", ha="left")
    cmap = LinearSegmentedColormap.from_list("retention", ["#f3f5f7", "#a1bacb", "#386A8B"])
    heat_records = []
    for ax, scheme, title in zip(heat_axes, SCHEMES, SCHEME_TITLES):
        matrix, row_labels = [], []
        for cohort in COHORTS:
            for branch, label in zip(BRANCHES, BRANCH_LABELS):
                subset = banks[(banks.cohort == cohort) & (banks.branch == branch) & (banks.scheme == scheme)]
                n = subset.bank_id.nunique()
                values = []
                for policy in POLICIES:
                    sub = subset[subset.policy == policy]
                    value = 100 * sub.retention_probability.mean()
                    values.append(value)
                    heat_records.append({"scheme": scheme, "cohort": cohort, "branch": branch,
                                         "policy": policy, "banks": n, "mean_retention_percent": value})
                matrix.append(values)
                row_labels.append(f"{'AMP-AD' if cohort == 'AMPAD' else cohort} · {label} ({n})")
        im = ax.pcolormesh(np.arange(5)-.5, np.arange(7)-.5, matrix, vmin=0, vmax=100, cmap=cmap, shading="flat", rasterized=False)
        ax.set_ylim(5.5, -.5)
        ax.set_xticks(range(4), POLICY_LABELS)
        ax.set_yticks(range(6), row_labels)
        ax.tick_params(axis="both", length=0, pad=4, labelsize=6.5)
        ax.set_title(title, fontsize=7, pad=8)
        ax.axhline(2.5, color="white", linewidth=2)
        for spine in ax.spines.values():
            spine.set_visible(False)
    cbax = fig.add_axes([.40, .555, .30, .014], label="retention_colorbar")
    cb = fig.colorbar(im, cax=cbax, orientation="horizontal")
    cb.set_ticks([0, 25, 50, 75, 100])
    cb.set_label("Signature retention (%)", fontsize=6.7, labelpad=3)
    cb.outline.set_visible(False)
    cb.solids.set_rasterized(False)

    # Exact repeated coordinates are aggregated only by marker area; every bank
    # contributes once to each scheme. No jitter or coordinate rounding is used.
    pair_rows, plotted_counts = [], {}
    for ax, scheme, title in zip(c_axes, SCHEMES, SCHEME_TITLES):
        subset = banks[banks.scheme == scheme]
        paired = subset.pivot(index=["cohort", "bank_id", "branch"], columns="policy", values="retention_probability").reset_index()
        assert len(paired) == 54 and paired[POLICIES].notna().all().all()
        ax.plot([0, 100], [0, 100], color="#7B8794", linestyle=(0, (3, 3)), linewidth=.6, zorder=1)
        plotted_count = 0
        for cohort in COHORTS:
            rows = paired[paired.cohort == cohort]
            counts = rows.groupby(["highest_score", "regret_medoid"]).size().reset_index(name="banks")
            plotted_count += int(counts.banks.sum())
            ax.scatter(100 * counts.highest_score, 100 * counts.regret_medoid,
                       s=8 * counts.banks, marker=COHORT_SHAPES[cohort],
                       facecolors="none" if cohort == "AMPAD" else COHORT_COLORS[cohort],
                       edgecolors=COHORT_COLORS[cohort], linewidths=.7, alpha=.85, zorder=3)
        assert plotted_count == 54
        plotted_counts[scheme] = plotted_count
        paired["scheme"] = scheme
        pair_rows.append(paired)
        ax.set(xlim=(-7, 107), ylim=(-7, 107), xlabel="Highest-score retention (%)")
        ax.set_xticks([0, 50, 100])
        ax.set_yticks([0, 50, 100])
        ax.set_title(title, fontsize=6.7, pad=7)
    c_axes[0].set_ylabel("Regret-medoid retention (%)")
    c_axes[1].set_yticklabels([])
    fig.legend(handles=[Line2D([], [], marker="o", color=COHORT_COLORS["TCGA"], linestyle="none",
                               markersize=4, label="TCGA (30 banks)"),
                        Line2D([], [], marker="s", markerfacecolor="none", markeredgecolor=COHORT_COLORS["AMPAD"],
                               linestyle="none", markersize=4, label="AMP-AD (24 banks)")],
               loc="center", bbox_to_anchor=(.315, .075), ncol=2, fontsize=6.3,
               handletextpad=.35, columnspacing=1)

    # Full-cohort equal-bank means: all policies appear with identical salience.
    tradeoff = groups[groups["group"] == "ALL54"].copy()
    assert len(tradeoff) == 8
    for scheme in SCHEMES:
        for policy in POLICIES:
            row = tradeoff[(tradeoff.scheme == scheme) & (tradeoff.policy == policy)].iloc[0]
            d.scatter(100 * row.mean_probability_gap_above_delta, 100 * row.retention_probability,
                      marker=POLICY_SHAPES[policy], s=28,
                      facecolors="white" if scheme == SCHEMES[0] else "#7B8794",
                      edgecolors="black", linewidths=.7, zorder=3)
    d.set(xlim=(-4, 62), ylim=(55, 110),
          xlabel="Probability of score gap > 0.01 (%)", ylabel="Signature retention (%)")
    d.set_xticks([0, 20, 40, 60])
    d.set_yticks([60, 80, 100])
    d.set_title("All 54 banks", fontsize=7, pad=7)
    d.legend(handles=[Line2D([], [], linestyle="none", marker="o", markerfacecolor="white", markeredgecolor="black",
                             markersize=4, label="Leave one fold out"),
                      Line2D([], [], linestyle="none", marker="o", markerfacecolor="#7B8794", markeredgecolor="black",
                             markersize=4, label="Fold bootstrap")],
             loc="upper left", fontsize=6.3, handletextpad=.4, borderaxespad=.5)
    fig.legend(handles=[Line2D([], [], linestyle="none", marker=POLICY_SHAPES[p], color="black", markerfacecolor="white",
                               markersize=4, label=label) for p, label in zip(POLICIES, POLICY_SHORT)],
               loc="center", bbox_to_anchor=(.805, .057), ncol=2, fontsize=6.3,
               handletextpad=.35, columnspacing=1, labelspacing=.7)

    fig.canvas.draw()
    validate_text(fig)
    require_matplotlib_panel_alignment(fig, json_out=WORK / f"{NAME}.alignment.json",
        overlay_svg=WORK / f"{NAME}.alignment.svg", tolerance_pt=1.5, gutter_tolerance_pt=1.5,
        strict=True, row_groups=[["a", "b"], ["c_lofo", "c_boot", "d"]],
        exemptions=[{"panels": ["d"], "checks": ["panel-width", "horizontal-gutter"],
                     "reason": "Panel d spans the width of two small paired-scatter facets; all lower plot edges/heights match."},
                    {"panels": ["c_lofo", "c_boot"], "checks": ["panel-label"],
                     "reason": "Two facets share a figure-level c label."}])
    fig.savefig(FIGURES / f"{NAME}.pdf")
    fig.savefig(FIGURES / f"{NAME}.svg")
    fig.savefig(FIGURES / f"{NAME}.png", dpi=600)
    fig.savefig(WORK / f"{NAME}_review.png", dpi=300)
    plt.close(fig)
    for name in source_names:
        shutil.copy2(SOURCE / name, WORK / "source_data" / name)
    pd.DataFrame(heat_records).to_csv(WORK / "source_data/heatmap_cells.csv", index=False)
    pd.concat(pair_rows, ignore_index=True).to_csv(WORK / "source_data/paired_scatter_banks.csv", index=False)
    tradeoff.to_csv(WORK / "source_data/tradeoff_all54.csv", index=False)
    report = {"width_mm": 170, "height_mm": 145, "banks": 54, "cohorts": {"TCGA": 30, "AMPAD": 24},
              "policy_scheme_bank_records": len(banks), "heatmap_cells": len(heat_records),
              "paired_scatter_banks_by_scheme": plotted_counts, "tradeoff_points": len(tradeoff),
              "excluded_banks": [], "CI_or_pvalues": False,
              "pair_overlap_encoding": "Exact duplicate coordinates within cohort merged; marker area proportional to count, no rounding or jitter",
              "bootstrap_weights": "126 count vectors weighted by multinomial multiplicity / 3125",
              "source_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (WORK / "source_data").glob("*.csv")}}
    (WORK / "data_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
