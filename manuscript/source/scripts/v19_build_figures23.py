"""Rebuild v19 main Figures 2 and 3 from frozen aggregate source data.

The v18 manuscript, Figure 1, and manuscript text are never modified.
All paired observations are retained. Figure 2 uses condition-level bars;
Figure 3 separates candidate-bank and participant-partition variation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "v19_work" / "figures23"
FIGURES = ROOT / "figures"
from audit_panel_alignment import require_matplotlib_panel_alignment

COLORS = {"svm_l1": "#386A8B", "xgboost": "#7B8794", "boruta_rf": "#8A6B98"}
LABELS = {"svm_l1": "SVM-L1", "xgboost": "XGBoost", "boruta_rf": "Boruta-RF"}
KEYS = {v: k for k, v in LABELS.items()}
MARKERS = {"svm_l1": "o", "xgboost": "s", "boruta_rf": "^"}
INK = "#000000"
NEUTRAL = "#8a9298"
LIGHT = "#d5dadd"
WIDTH_MM = 170


def configure() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 7.5,
        "font.weight": "normal",
        "axes.labelsize": 7.5,
        "axes.labelweight": "normal",
        "axes.titleweight": "normal",
        "axes.titlesize": 7.5,
        "axes.linewidth": .65,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "xtick.major.size": 2.8,
        "ytick.major.size": 2.8,
        "xtick.major.width": .6,
        "ytick.major.width": .6,
        "legend.fontsize": 7,
        "legend.frameon": False,
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "savefig.facecolor": "white",
        "svg.hashsalt": "wrapevofs-v19-figures23",
    })


def panel(ax: plt.Axes, letter: str, x=-26, y=10) -> None:
    ax.annotate(letter, xy=(0, 1), xycoords="axes fraction",
                xytext=(x, y), textcoords="offset points", fontsize=10,
                fontweight="bold", ha="left", va="bottom", annotation_clip=False)


def branch_handles(*, shaped=True) -> list[Line2D]:
    return [Line2D([], [], linestyle="none", marker=MARKERS[b] if shaped else "o",
                   markersize=4.5, markerfacecolor=COLORS[b],
                   markeredgecolor=COLORS[b], label=LABELS[b]) for b in LABELS]


def validate_text(fig: plt.Figure) -> None:
    for text in fig.findobj(mpl.text.Text):
        if not text.get_text():
            continue
        if text.get_fontweight() in ("bold", "heavy", 700):
            assert text.get_text() in tuple("abcd"), text.get_text()
        assert mpl.colors.to_hex(text.get_color()).lower() == INK, text.get_text()


def export(fig: plt.Figure, name: str, *, align: dict) -> None:
    fig.canvas.draw()
    validate_text(fig)
    require_matplotlib_panel_alignment(
        fig, json_out=WORK / f"{name}.alignment.json",
        overlay_svg=WORK / f"{name}.alignment.svg", tolerance_pt=1.5,
        gutter_tolerance_pt=1.5, strict=True, **align)
    # Fixed page box preserves the requested physical width in LaTeX.
    fig.savefig(FIGURES / f"{name}.pdf")
    fig.savefig(FIGURES / f"{name}.svg")
    fig.savefig(FIGURES / f"{name}.png", dpi=600)
    fig.savefig(WORK / f"{name}_review.png", dpi=300)
    plt.close(fig)


def condition_bars(ax: plt.Axes, data: pd.DataFrame, branch: str,
                   old: str, new: str, ymax: float, ticks: list[int]) -> list[str]:
    """One original/updated pair per center-cap condition; zero-origin axes."""
    centers = ["Emory", "Mayo", "Mount Sinai", "Rush"]
    caps = ["Reference-cap", "Small-cap"]
    rows = pd.concat([data[(data.Branch == LABELS[branch]) &
                           (data.Center == center) & (data.Cap == cap)]
                      for center in centers for cap in caps])
    assert len(rows) == 8 and rows.condition.nunique() == 8
    xx = np.array([0, 1, 2.6, 3.6, 5.2, 6.2, 7.8, 8.8])
    width = .34
    ax.bar(xx-width/2, rows[old], width=width, facecolor="white",
           edgecolor=COLORS[branch], linewidth=.7, zorder=3)
    ax.bar(xx+width/2, rows[new], width=width, facecolor=COLORS[branch],
           edgecolor=COLORS[branch], linewidth=.5, zorder=3)
    # A zero-height bar is an observed zero, not a missing observation.
    for xpos, (_, row) in zip(xx, rows.iterrows()):
        for offset, field, filled in [(-width/2, old, False), (width/2, new, True)]:
            if row[field] == 0:
                ax.plot([xpos+offset-width*.39, xpos+offset+width*.39], [0, 0],
                        color=COLORS[branch], linewidth=1.0 if filled else .55,
                        clip_on=False, zorder=5)
        if row.stress_condition:
            for offset, field in [(-width/2, old), (width/2, new)]:
                if field == old:
                    ax.text(xpos+offset, row[field]+ymax*.035, str(int(row[field])),
                            ha="center", va="bottom", fontsize=6.7)
                else:
                    ax.annotate(str(int(row[field])), xy=(xpos+offset, row[field]),
                                xytext=(5, 1), textcoords="offset points",
                                ha="left", va="bottom", fontsize=6.7,
                                annotation_clip=False)
    ax.set_xticks(xx, ["R", "S"] * 4)
    ax.tick_params(axis="x", length=0, pad=3, labelsize=6.7)
    for center, xmid in zip(["Emory", "Mayo", "Sinai", "Rush"], xx.reshape(4, 2).mean(1)):
        ax.text(xmid, -.25, center, transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=6.7)
    ax.set(xlim=(-.65, 9.4), ylim=(0, ymax))
    ax.set_yticks(ticks)
    ax.tick_params(axis="y", labelsize=6.7)
    ax.grid(False)
    return rows.condition.tolist()


def figure2() -> dict:
    paths = [ROOT / "revision_outputs" / "S16_CONDITION_LEVEL_PAIRED.csv",
             ROOT / "revision_outputs" / "CROSS_LOCK_2X2_SUMMARY.csv"]
    data, cross = [pd.read_csv(p, float_precision="round_trip") for p in paths]
    assert len(data) == 24 and len(cross) == 4
    assert cross.conditions.eq(24).all()
    assert int(data.stress_condition.sum()) == 1
    assert data.updated_regret.max() <= .01
    assert (data.original_target_deviation.sum(), data.updated_target_deviation.sum()) == (216, 137)
    assert (data.original_all_zero_generations.sum(), data.updated_all_zero_generations.sum()) == (673, 333)

    fig = plt.figure(figsize=(WIDTH_MM / 25.4, 155 / 25.4))
    positions = [.105, .415, .725]
    top = [fig.add_axes([x, .745, .25, .18], label=f"a{i}") for i, x in enumerate(positions)]
    middle = [fig.add_axes([x, .455, .25, .18], label=f"b{i}") for i, x in enumerate(positions)]
    c = fig.add_axes([.105, .12, .36, .22], label="c")
    d = fig.add_axes([.615, .12, .36, .22], label="d")
    plotted_a, plotted_b = [], []
    target_axes = [(95, [0, 25, 50, 75]), (20, [0, 5, 10, 15, 20]), (22, [0, 5, 10, 15, 20])]
    zero_axes = [(285, [0, 50, 100, 150, 200, 250]), (70, [0, 20, 40, 60]), (45, [0, 10, 20, 30, 40])]
    for i, branch in enumerate(LABELS):
        ymax, ticks = target_axes[i]
        plotted_a += condition_bars(top[i], data, branch,
            "original_target_deviation", "updated_target_deviation", ymax, ticks)
        ymax, ticks = zero_axes[i]
        plotted_b += condition_bars(middle[i], data, branch,
            "original_all_zero_generations", "updated_all_zero_generations", ymax, ticks)
        top[i].set_title(LABELS[branch], pad=9)
    assert sorted(plotted_a) == sorted(plotted_b) == sorted(data.condition.tolist())
    top[0].set_ylabel("Absolute target deviation", labelpad=4)
    middle[0].set_ylabel("Legacy-zero diagnostic\ngenerations", labelpad=4, fontsize=7)
    for ax, letter in [(top[0], "a"), (middle[0], "b"), (c, "c"), (d, "d")]:
        panel(ax, letter, x=-29, y=10)
    fig.legend(handles=[Patch(facecolor="white", edgecolor=INK, linewidth=.7, label="Original"),
                        Patch(facecolor=INK, edgecolor=INK, label="Updated")],
               loc="center left", bbox_to_anchor=(.14, .378), ncol=2,
               handlelength=1.2, handletextpad=.5, columnspacing=1.5)
    fig.text(.69, .378, "R: reference cap   S: small cap", ha="center", va="center", fontsize=6.7)
    for row in data.itertuples(index=False):
        branch = KEYS[row.Branch]
        c.scatter(row.score_difference, row.updated_regret,
                  s=25, marker=MARKERS[branch], color=COLORS[branch],
                  edgecolors="white", linewidths=.5, zorder=4)
    c.axhline(.01, color=INK, linestyle=(0, (4, 3)), linewidth=.7)
    c.axvline(0, color=NEUTRAL, linestyle=(0, (2, 2)), linewidth=.6)
    c.set(xlabel="Updated − original locking score", ylabel="Selected score gap",
          xlim=(-.016, .026), ylim=(-.0005, .0125))
    c.set_xticks([-.01, 0, .01, .02])
    c.set_yticks([0, .005, .01], ["0", "0.005", "0.010"])
    c.text(.025, .0112, "δ = 0.01", fontsize=7, ha="right", va="center")

    # Same bank under both rules: maxima over the same 24 conditions.
    values = []
    for i, bank in enumerate(["original_objective", "updated_objective"]):
        for j, rule in enumerate(["original_top_three", "regret_constrained"]):
            row = cross[(cross.candidate_bank == bank) & (cross.locking_rule == rule)].iloc[0]
            value = float(row.maximum_selected_regret)
            values.append(value)
            d.bar(i + (-.18 if j == 0 else .18), value, width=.30,
                  facecolor="white" if j == 0 else COLORS["xgboost"],
                  edgecolor=COLORS["xgboost"], linewidth=.8, zorder=3)
    d.axhline(.01, color=INK, linestyle=(0, (4, 3)), linewidth=.7, zorder=2)
    d.text(1.48, .0108, "δ = 0.01", ha="right", va="bottom", fontsize=6.7)
    d.set(xlim=(-.5, 1.5), ylim=(0, .029), ylabel="Maximum selected score gap")
    d.set_xticks([0, 1], ["Original banks", "Updated banks"])
    d.tick_params(axis="x", length=0, labelsize=6.7, pad=4)
    d.set_yticks([0, .01, .02], ["0", "0.01", "0.02"])
    d.legend(handles=[Patch(facecolor="white", edgecolor=COLORS["xgboost"], label="Top-three medoid"),
                      Patch(facecolor=COLORS["xgboost"], edgecolor=COLORS["xgboost"], label="Regret-constrained")],
             loc="upper right", fontsize=6.7, handlelength=1.1, handletextpad=.5)
    fig.legend(handles=branch_handles(), loc="lower center", bbox_to_anchor=(.51, .012),
               ncol=3, handletextpad=.4, columnspacing=1.8)
    export(fig, "figure_2", align={
        "row_groups": [["a0", "a1", "a2"], ["b0", "b1", "b2"], ["c", "d"]],
        "column_groups": [["a0", "b0"], ["a1", "b1"], ["a2", "b2"]],
        "exemptions": [{"panels": ["a1", "a2", "b1", "b2"], "checks": ["panel-label"],
                        "reason": "Branch facets within lettered panels a and b."}]})
    for p in paths:
        shutil.copy2(p, WORK / "source_data" / p.name)
    return {"conditions_full": 24, "conditions_per_branch_facet": 8,
            "bars_per_metric": 48, "omitted_conditions": [],
            "plotted_condition_identifiers": plotted_a,
            "axes": "All bars begin at zero; explicit branch-specific y-axis ranges; no broken axes or exclusions",
            "target_deviation": [216, 137], "all_zero_generations": [673, 333],
            "legacy_zero_metric": "Updated counts are counterfactual zero-truncation diagnostics, not actual sampling failures",
            "actual_updated_sampling_fallbacks": 0,
            "cross_lock_conditions_per_bar": 24,
            "cross_lock_maximum_selected_gaps": values,
            "maximum_selected_regret": float(data.updated_regret.max())}


def figure3() -> dict:
    source = ROOT / "supplementary_data" / "tcga_nested_v1_v2"
    names = ["candidate_level_geometry.csv", "bank_level_locking_summary.csv",
             "agreement_by_repeat_branch.csv", "outer_fold_pairwise_stability.csv"]
    cand, banks, agreement, pairs = [pd.read_csv(source / n, float_precision="round_trip") for n in names]
    assert len(cand) == 150 and len(banks) == 30 and len(pairs) == 60
    changed = banks[banks.selected_differs_highest]
    nonsingle = banks[banks.eligible_pool_size > 1]
    retained = nonsingle[~nonsingle.selected_differs_highest]
    assert len(changed) == 11 and len(retained) == 13 and len(nonsingle) == 24
    # Recompute bank-level means from all five saved feature sets, independent
    # of the eligible-pool field used by the locking objective.
    within_rows = []
    for key, group in cand.groupby(["outer_repeat", "outer_fold", "branch"]):
        assert len(group) == 5
        feature_sets = [set(json.loads(s)) for s in group.features]
        overlaps = [len(x & y) / len(x | y)
                    for i, x in enumerate(feature_sets) for y in feature_sets[i+1:]]
        assert len(overlaps) == 10
        within_rows.append([*key, float(np.mean(overlaps))])
    within = pd.DataFrame(within_rows, columns=["outer_repeat", "outer_fold", "branch", "mean_pairwise_jaccard"])
    for row in agreement.itertuples(index=False):
        subset = within[(within.outer_repeat == row.outer_repeat) & (within.branch == row.branch)]
        assert np.isclose(subset.mean_pairwise_jaccard.mean(), row.mean_fold_level_within_bank_seed_jaccard, atol=1e-12)
        across = pairs[(pairs.outer_repeat == row.outer_repeat) & (pairs.branch == row.branch)]
        assert np.isclose(across.jaccard.mean(), row.across_outer_fold_locked_jaccard, atol=1e-12)
    within.to_csv(WORK / "source_data" / "within_bank_jaccard_recomputed.csv", index=False)
    fig = plt.figure(figsize=(WIDTH_MM / 25.4, 134 / 25.4))
    a = fig.add_axes([.105, .615, .365, .29], label="a")
    b = fig.add_axes([.615, .615, .365, .29], label="b")
    c = fig.add_axes([.105, .16, .17, .29], label="c_within")
    ca = fig.add_axes([.325, .16, .17, .29], label="c_across")
    d = fig.add_axes([.615, .16, .365, .29], label="d")
    for ax, letter in [(a, "a"), (b, "b"), (c, "c"), (d, "d")]:
        panel(ax, letter)
        ax.grid(False)
    a.axvspan(0, .01, color="#edf2f5", zorder=0)
    a.axvline(.01, color=INK, linestyle=(0, (4, 3)), linewidth=.7)
    for branch in LABELS:
        rows = cand[cand.branch == branch]
        a.scatter(rows.absolute_regret, rows.jaccard_distance_to_highest,
                  color=COLORS[branch], marker=MARKERS[branch], s=15, alpha=.53,
                  linewidths=0, zorder=2)
        selected = rows[rows.selected]
        a.scatter(selected.absolute_regret, selected.jaccard_distance_to_highest,
                  marker="s", s=34, facecolors="none", edgecolors=COLORS[branch],
                  linewidths=1, zorder=4)
    a.set(xlim=(-.0015, .041), ylim=(-.04, 1.05), xlabel="Development score gap",
          ylabel="Jaccard distance from highest score")
    a.set_xticks([0, .01, .02, .03, .04], ["0", "0.01", "0.02", "0.03", "0.04"])
    a.set_yticks([0, .25, .5, .75, 1], ["0", "0.25", "0.50", "0.75", "1"])
    a.legend(handles=[Line2D([], [], linestyle="none", marker="s", markerfacecolor="none",
                             markeredgecolor=INK, markersize=5, label="Locked (n=30)"),
                      Line2D([], [], linestyle="none", marker="o", color=INK,
                             markersize=4, label="Highest at origin (n=30)")],
             loc="lower right", bbox_to_anchor=(1, .07), fontsize=6.7, handletextpad=.4)
    b.axhline(0, color=LIGHT, linewidth=.65)
    b.axvline(.01, color=INK, linestyle=(0, (4, 3)), linewidth=.7)
    for branch in LABELS:
        rows = changed[changed.branch == branch]
        b.scatter(rows.selected_regret, rows.representativeness_gain,
                  color=COLORS[branch], marker=MARKERS[branch], s=32, linewidths=.5,
                  edgecolors="white", zorder=3)
    b.scatter([0], [0], s=38, marker="o", facecolors="white", edgecolors=INK, linewidths=.8, zorder=4)
    b.set(xlim=(-.0005, .0106), ylim=(-.005, .096), xlabel="Selected score gap",
          ylabel="Selection-criterion gain\n(eligible-pool mean Jaccard)")
    b.set_xticks([0, .005, .01], ["0", "0.005", "0.010"])
    b.set_yticks([0, .02, .04, .06, .08], ["0", "0.02", "0.04", "0.06", "0.08"])
    b.text(.0056, .015, "Changed: 11\nRetained at origin: 13", fontsize=6.7,
           ha="left", va="center", linespacing=1.4)
    for ax, title, metric in [(c, "Within bank", "within"), (ca, "Across folds", "across")]:
        for i, branch in enumerate(LABELS):
            for repeat in [1, 2]:
                x = i + (-.19 if repeat == 1 else .19)
                summary = agreement[(agreement.branch == branch) & (agreement.outer_repeat == repeat)].iloc[0]
                if metric == "within":
                    values = within[(within.branch == branch) & (within.outer_repeat == repeat)].mean_pairwise_jaccard.to_numpy()
                    center = summary.mean_fold_level_within_bank_seed_jaccard
                    assert len(values) == 5
                else:
                    values = pairs[(pairs.branch == branch) & (pairs.outer_repeat == repeat)].jaccard.to_numpy()
                    center = summary.across_outer_fold_locked_jaccard
                    assert len(values) == 10
                ax.bar(x, center, width=.34, facecolor=COLORS[branch] if repeat == 1 else "white",
                       edgecolor=COLORS[branch], linewidth=.75, alpha=.45 if repeat == 1 else 1, zorder=1)
                jitter = np.linspace(-.09, .09, len(values))
                ax.scatter(x+jitter, values, marker="o" if repeat == 1 else "s", s=6,
                           facecolors=COLORS[branch] if repeat == 1 else "white",
                           edgecolors=COLORS[branch], linewidths=.55, zorder=4)
        ax.set_xticks([0, 1, 2], ["SVM", "XGB", "Boruta"])
        ax.tick_params(axis="x", labelsize=6.7, length=0, pad=4)
        ax.set(xlim=(-.6, 2.6), ylim=(0, .225))
        ax.set_yticks([0, .05, .1, .15, .2], ["0", ".05", ".10", ".15", ".20"])
        ax.tick_params(axis="y", labelsize=6.7)
        ax.set_title(title, fontsize=7, pad=9)
    c.set_ylabel("Pairwise Jaccard")
    repeat_handles = [Line2D([], [], marker="o", linestyle="none", markersize=4.5,
                            markerfacecolor=INK, markeredgecolor=INK, label="Repeat 1"),
                      Line2D([], [], marker="s", linestyle="none", markersize=4.5,
                            markerfacecolor="white", markeredgecolor=INK, label="Repeat 2")]
    fig.legend(handles=repeat_handles, loc="center", bbox_to_anchor=(.30, .075), ncol=2,
               fontsize=6.7, handletextpad=.3, columnspacing=1.4)
    for branch in LABELS:
        for repeat in [1, 2]:
            rows = pairs[(pairs.branch == branch) & (pairs.outer_repeat == repeat)]
            marker = "o" if repeat == 1 else "s"
            face = COLORS[branch] if repeat == 1 else "white"
            d.scatter(rows.cardinality_similarity, rows.jaccard,
                      marker=marker, facecolors=face, edgecolors=COLORS[branch],
                      s=17, linewidths=.7, alpha=.65)
            d.scatter([rows.cardinality_similarity.median()], [rows.jaccard.median()],
                      marker=marker, s=46, facecolors=face, edgecolors=INK,
                      linewidths=.9, zorder=5)
    d.set(xlabel="Feature-count similarity", ylabel="Feature-set Jaccard",
          xlim=(.57, 1.025), ylim=(-.01, .24))
    d.set_xticks([.6, .7, .8, .9, 1])
    d.set_yticks([0, .1, .2], ["0", "0.10", "0.20"])
    d.legend(handles=[*repeat_handles, Line2D([], [], linestyle="none", marker="o",
                                            markersize=6.3, markerfacecolor="white",
                                            markeredgecolor=INK, label="Median")],
             loc="upper left", fontsize=6.7, handletextpad=.3, labelspacing=.4)
    fig.legend(handles=branch_handles(shaped=False), loc="lower center", bbox_to_anchor=(.52, .005),
               ncol=3, handletextpad=.4, columnspacing=1.8)
    export(fig, "figure_4_strengthened", align={
        "row_groups": [["a", "b"], ["c_within", "c_across"], ["c_within", "d"]],
        "column_groups": [["b", "d"]],
        "exemptions": [{"panels": ["c_across"], "checks": ["panel-label"],
                        "reason": "Second independently labeled comparison layer within panel c."}]})
    for n in names:
        shutil.copy2(source / n, WORK / "source_data" / n)
    return {"candidates": 150, "banks": 30, "changed": 11,
            "nonsingleton": 24, "retained_nonsingleton": 13,
            "singleton_excluded_from_gain": 6, "dependent_outer_pairs": 60,
            "within_bank_raw_means": 30, "underlying_within_bank_pairs": 300,
            "agreement_recomputation_absolute_tolerance": 1e-12,
            "max_selected_regret": float(banks.selected_regret.max())}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--figure", choices=["2", "3", "all"], default="all")
    args = parser.parse_args()
    (WORK / "source_data").mkdir(parents=True, exist_ok=True)
    configure()
    report = {}
    if args.figure in ("2", "all"):
        report["Figure 2"] = figure2()
    if args.figure in ("3", "all"):
        report["Figure 3"] = figure3()
    report["sources_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (WORK / "source_data").glob("*.csv")}
    (WORK / "data_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
