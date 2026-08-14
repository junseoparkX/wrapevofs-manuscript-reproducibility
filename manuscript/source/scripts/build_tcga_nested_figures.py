from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
from itertools import combinations
from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from figure_palette import BRANCH_COLORS, DARK, LIGHT, MID, PALE


MM_TO_INCH = 1 / 25.4
FIGURE_WIDTH_IN = 170 * MM_TO_INCH
COLORS = BRANCH_COLORS
BRANCH_LABELS = {"svm_l1": "SVM-L1", "xgboost": "XGBoost", "boruta_rf": "Boruta-RF"}
BRANCHES = ("svm_l1", "xgboost", "boruta_rf")
METHODS = (
    "direct",
    "rfecv_only",
    "highest_locking_score",
    "legacy_top3_medoid",
    "unrestricted_medoid",
    "regret_constrained_medoid",
)
METHOD_LABELS = {
    "direct": "Direct",
    "rfecv_only": "RFECV-only",
    "highest_locking_score": "Highest score",
    "legacy_top3_medoid": "Legacy top-3",
    "unrestricted_medoid": "Unrestricted medoid",
    "regret_constrained_medoid": "Regret medoid",
}
DELTA = 0.01


def branch_handles() -> list[mpl.lines.Line2D]:
    return [
        mpl.lines.Line2D(
            [],
            [],
            marker="o",
            linestyle="none",
            markersize=4.4,
            markerfacecolor=COLORS[branch],
            markeredgecolor=COLORS[branch],
            label=BRANCH_LABELS[branch],
        )
        for branch in BRANCHES
    ]


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 6.5,
            "axes.labelsize": 6.8,
            "axes.titlesize": 8.3,
            "axes.titleweight": "normal",
            "xtick.labelsize": 5.7,
            "ytick.labelsize": 5.7,
            "legend.fontsize": 5.5,
            "axes.linewidth": 0.75,
            "xtick.major.width": 0.65,
            "ytick.major.width": 0.65,
            "xtick.major.size": 3.0,
            "ytick.major.size": 3.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "wrapevofs-tcga-v1-v2-20260812",
            "text.color": DARK,
            "axes.labelcolor": DARK,
            "axes.edgecolor": DARK,
            "xtick.color": DARK,
            "ytick.color": DARK,
        }
    )


def clean_axis(axis: plt.Axes) -> None:
    axis.grid(False)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)


def panel_label(axis: plt.Axes, label: str, *, x: float = -0.16, y: float = 1.08) -> None:
    axis.text(
        x,
        y,
        label,
        transform=axis.transAxes,
        fontsize=10.2,
        fontweight="bold",
        va="bottom",
        ha="left",
        clip_on=False,
    )


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return 1.0 if not union else len(left & right) / len(union)


def parse_features(value: str) -> list[str]:
    parsed = json.loads(value) if value.lstrip().startswith("[") else ast.literal_eval(value)
    return list(map(str, parsed))


def nogueira_stability(mask_values: list[str]) -> float:
    """Chance-corrected stability across masks on one canonical universe."""
    if len(mask_values) < 2:
        return math.nan
    lengths = {len(value) for value in mask_values}
    if len(lengths) != 1 or not lengths or next(iter(lengths)) == 0:
        return math.nan
    matrix = np.asarray([[character == "1" for character in value] for value in mask_values], dtype=float)
    mean_fraction = float(matrix.mean())
    denominator = mean_fraction * (1.0 - mean_fraction)
    if denominator <= 0:
        return math.nan
    mean_sample_variance = float(matrix.var(axis=0, ddof=1).mean())
    return 1.0 - mean_sample_variance / denominator


def read_analysis(results_root: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    candidate_rows = []
    bank_rows = []
    selected_sets = []
    method_sets = []
    for repeat in (1, 2):
        for fold in range(1, 6):
            for branch in BRANCHES:
                directory = results_root / f"repeat_{repeat:02d}" / f"fold_{fold:02d}" / branch
                frame = pd.read_csv(
                    directory / "locking_candidate_audit.csv",
                    dtype={"canonical_mask": str, "stable_mask_hash": str, "candidate_universe_sha256": str},
                )
                frame["outer_repeat"] = repeat
                frame["outer_fold"] = fold
                frame["branch"] = branch
                frame["features"] = frame["canonical_features"].map(parse_features)
                frame["feature_set"] = frame["features"].map(set)
                highest = frame.sort_values(
                    ["locking_score", "feature_count", "stable_mask_hash"],
                    ascending=[False, True, True],
                    kind="mergesort",
                ).iloc[0]
                selected = frame.loc[frame["selected"]].iloc[0]
                eligible = frame.loc[frame["eligible"]].copy()
                highest_set = set(highest["features"])
                frame["jaccard_to_highest"] = frame["feature_set"].map(lambda value: jaccard(value, highest_set))
                frame["jaccard_distance_to_highest"] = 1 - frame["jaccard_to_highest"]
                candidate_rows.extend(frame.drop(columns=["feature_set"]).to_dict("records"))
                eligible_size = len(eligible)
                if eligible_size == 1:
                    gain = np.nan
                    highest_mean = np.nan
                    selected_mean = np.nan
                else:
                    highest_mean = float(highest["mean_jaccard"])
                    selected_mean = float(selected["mean_jaccard"])
                    gain = selected_mean - highest_mean
                bank_rows.append(
                    {
                        "outer_repeat": repeat,
                        "outer_fold": fold,
                        "branch": branch,
                        "eligible_pool_size": eligible_size,
                        "selected_run_id": int(selected["run_id"]),
                        "highest_run_id": int(highest["run_id"]),
                        "selected_regret": float(selected["absolute_regret"]),
                        "selected_feature_count": int(selected["feature_count"]),
                        "highest_feature_count": int(highest["feature_count"]),
                        "selected_differs_highest": str(selected["stable_mask_hash"]) != str(highest["stable_mask_hash"]),
                        "highest_mean_jaccard": highest_mean,
                        "selected_mean_jaccard": selected_mean,
                        "representativeness_gain": gain,
                        "selected_highest_jaccard": jaccard(set(selected["features"]), highest_set),
                    }
                )
                selected_sets.append(
                    {
                        "outer_repeat": repeat,
                        "outer_fold": fold,
                        "branch": branch,
                        "features": set(selected["features"]),
                        "feature_count": int(selected["feature_count"]),
                        "rna_count": sum(name.startswith("RNA::") for name in selected["features"]),
                        "scnv_count": sum(name.startswith("SCNV::") for name in selected["features"]),
                    }
                )
                feature_sets = json.loads((directory / "feature_sets.json").read_text(encoding="utf-8"))
                for method, features in feature_sets.items():
                    method_sets.append(
                        {
                            "outer_repeat": repeat,
                            "outer_fold": fold,
                            "branch": branch,
                            "method": method,
                            "features": set(map(str, features)),
                            "feature_count": len(features),
                        }
                    )
    candidates = pd.DataFrame(candidate_rows)
    banks = pd.DataFrame(bank_rows)
    selected = pd.DataFrame(selected_sets)
    method_sets_frame = pd.DataFrame(method_sets)

    agreement_rows = []
    outer_pair_rows = []
    for repeat in (1, 2):
        for branch in BRANCHES:
            seed_values = []
            nogueira_values = []
            for fold in range(1, 6):
                frame = candidates.loc[
                    candidates["outer_repeat"].eq(repeat)
                    & candidates["outer_fold"].eq(fold)
                    & candidates["branch"].eq(branch)
                ]
                sets = [set(value) for value in frame["features"]]
                seed_values.append(float(np.mean([jaccard(left, right) for left, right in combinations(sets, 2)])))
                nogueira_values.append(nogueira_stability(frame["canonical_mask"].astype(str).tolist()))
            locked = selected.loc[selected["outer_repeat"].eq(repeat) & selected["branch"].eq(branch)].sort_values("outer_fold")
            locked_rows = list(locked.to_dict("records"))
            outer_values = []
            for left, right in combinations(locked_rows, 2):
                identity = jaccard(left["features"], right["features"])
                size_similarity = min(left["feature_count"], right["feature_count"]) / max(left["feature_count"], right["feature_count"])
                outer_values.append(identity)
                outer_pair_rows.append(
                    {
                        "outer_repeat": repeat,
                        "branch": branch,
                        "fold_left": left["outer_fold"],
                        "fold_right": right["outer_fold"],
                        "jaccard": identity,
                        "cardinality_similarity": size_similarity,
                        "left_count": left["feature_count"],
                        "right_count": right["feature_count"],
                    }
                )
            agreement_rows.append(
                {
                    "outer_repeat": repeat,
                    "branch": branch,
                    "mean_fold_level_within_bank_seed_jaccard": float(np.mean(seed_values)),
                    "mean_fold_level_within_bank_nogueira_stability": float(np.nanmean(nogueira_values)),
                    "across_outer_fold_locked_jaccard": float(np.mean(outer_values)),
                    "within_minus_across_jaccard": float(np.mean(seed_values) - np.mean(outer_values)),
                }
            )
    return candidates, banks, selected, pd.DataFrame(agreement_rows), pd.DataFrame(outer_pair_rows), method_sets_frame


def save_frame(frame: pd.DataFrame, path: Path) -> None:
    serializable = frame.copy()
    for column in serializable.columns:
        if not len(serializable):
            continue
        example = next((value for value in serializable[column] if isinstance(value, (set, list, dict))), None)
        if example is not None:
            serializable[column] = serializable[column].map(
                lambda value: json.dumps(sorted(value) if isinstance(value, set) else value)
                if isinstance(value, (set, list, dict))
                else value
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable.to_csv(path, index=False)


def save_figure(fig: plt.Figure, stem: Path, manifest: list[dict], multipage_pdf: bool = False) -> None:
    metadata = {"Creator": "WrapEvoFS reproducible TCGA v1/v2 analysis", "CreationDate": None, "ModDate": None}
    if not multipage_pdf:
        fig.savefig(stem.with_suffix(".pdf"), metadata=metadata)
        fig.savefig(stem.with_suffix(".svg"), metadata={"Date": None})
        fig.savefig(stem.with_suffix(".png"), dpi=600, metadata={"Software": "WrapEvoFS"})
        for suffix in (".pdf", ".svg", ".png"):
            path = stem.with_suffix(suffix)
            manifest.append({"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size})
    plt.close(fig)


def figure_6(candidates: pd.DataFrame, banks: pd.DataFrame, agreement: pd.DataFrame, outer_pairs: pd.DataFrame, output: Path, manifest: list[dict]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(FIGURE_WIDTH_IN, 4.78))
    fig.subplots_adjust(left=0.10, right=0.985, bottom=0.15, top=0.90, hspace=0.50, wspace=0.42)
    ax = axes[0, 0]
    ax.axvspan(0, DELTA, color=PALE, zorder=0)
    for branch in BRANCHES:
        subset = candidates.loc[candidates["branch"].eq(branch)]
        ax.scatter(subset["absolute_regret"], subset["jaccard_distance_to_highest"], s=12, color=COLORS[branch], alpha=0.55, edgecolors="none")
        chosen = subset.loc[subset["selected"]]
        ax.scatter(chosen["absolute_regret"], chosen["jaccard_distance_to_highest"], marker="D", s=23, facecolors="white", edgecolors=COLORS[branch], linewidths=0.9, zorder=4)
    ax.axvline(DELTA, color=MID, linestyle="--", linewidth=0.8)
    ax.set(xlabel="Empirical regret", ylabel="Jaccard distance", xlim=(-0.001, max(0.036, candidates["absolute_regret"].max() * 1.04)), ylim=(-0.03, 1.03))
    candidate_handle = mpl.lines.Line2D([], [], marker="o", linestyle="none", markersize=4.0, markerfacecolor=DARK, markeredgecolor="none", label="Candidate")
    selected_handle = mpl.lines.Line2D([], [], marker="D", linestyle="none", markersize=4.6, markerfacecolor="white", markeredgecolor=DARK, label="Selected medoid")
    ax.legend(handles=[candidate_handle, selected_handle], frameon=False, ncol=2, loc="lower right", handletextpad=0.35, columnspacing=0.8)
    panel_label(ax, "a)", x=-0.10, y=1.02)
    clean_axis(ax)

    ax = axes[0, 1]
    for branch in BRANCHES:
        subset = banks.loc[banks["branch"].eq(branch) & banks["representativeness_gain"].notna()]
        for changed, marker in ((False, "o"), (True, "D")):
            points = subset.loc[subset["selected_differs_highest"].eq(changed)]
            ax.scatter(points["selected_regret"], points["representativeness_gain"], s=26 if changed else 20, marker=marker, facecolors=COLORS[branch] if changed else "white", edgecolors=COLORS[branch], linewidths=0.9, alpha=0.95)
    ax.axvline(DELTA, color=MID, linestyle="--", linewidth=0.8)
    ax.axhline(0, color=LIGHT, linewidth=0.75)
    ax.set(xlabel="Selected regret", ylabel="Mean-Jaccard gain", xlim=(-0.0005, 0.0106), ylim=(-0.006, max(0.094, banks["representativeness_gain"].max() * 1.10)))
    retained_handle = mpl.lines.Line2D([], [], marker="o", linestyle="none", markersize=4.5, markerfacecolor="white", markeredgecolor=DARK, label="Highest-score candidate")
    changed_handle = mpl.lines.Line2D([], [], marker="D", linestyle="none", markersize=4.8, markerfacecolor=DARK, markeredgecolor=DARK, label="Medoid changed")
    ax.legend(
        handles=[retained_handle, changed_handle],
        frameon=False,
        ncol=2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.23),
        handletextpad=0.35,
        columnspacing=0.8,
    )
    panel_label(ax, "b)", x=-0.10, y=1.02)
    clean_axis(ax)

    ax = axes[1, 0]
    x_positions = [0, 1]
    offsets = {-1: -0.055, 1: 0.055}
    for row in agreement.itertuples(index=False):
        offset = offsets[-1 if row.outer_repeat == 1 else 1]
        values = [row.mean_fold_level_within_bank_seed_jaccard, row.across_outer_fold_locked_jaccard]
        ax.plot([x + offset for x in x_positions], values, color=COLORS[row.branch], linewidth=0.8, alpha=0.75)
        marker = "o" if row.outer_repeat == 1 else "s"
        face = COLORS[row.branch] if row.outer_repeat == 1 else "white"
        ax.scatter([x + offset for x in x_positions], values, marker=marker, s=25, facecolors=face, edgecolors=COLORS[row.branch], linewidths=0.9, zorder=3)
    ax.set_xticks(x_positions, ["Within-bank\nGA seeds", "Across outer\nfolds"])
    ax.set(ylabel="Mean pairwise Jaccard", xlim=(-0.3, 1.3), ylim=(0, max(0.15, agreement["mean_fold_level_within_bank_seed_jaccard"].max() * 1.15)))
    repeat_one = mpl.lines.Line2D([], [], marker="o", linestyle="none", markersize=4.6, markerfacecolor=DARK, markeredgecolor=DARK, label="Repeat 1")
    repeat_two = mpl.lines.Line2D([], [], marker="s", linestyle="none", markersize=4.6, markerfacecolor="white", markeredgecolor=DARK, label="Repeat 2")
    ax.legend(handles=[repeat_one, repeat_two], frameon=False, ncol=2, loc="upper right", handletextpad=0.35, columnspacing=0.8)
    panel_label(ax, "c)", x=-0.10, y=1.055)
    clean_axis(ax)

    ax = axes[1, 1]
    markers = {1: "o", 2: "s"}
    for branch in BRANCHES:
        for repeat in (1, 2):
            subset = outer_pairs.loc[outer_pairs["branch"].eq(branch) & outer_pairs["outer_repeat"].eq(repeat)]
            ax.scatter(subset["cardinality_similarity"], subset["jaccard"], marker=markers[repeat], s=16, facecolors=COLORS[branch] if repeat == 1 else "white", edgecolors=COLORS[branch], linewidths=0.75, alpha=0.70)
            ax.scatter([subset["cardinality_similarity"].median()], [subset["jaccard"].median()], marker=markers[repeat], s=46, facecolors=COLORS[branch] if repeat == 1 else "white", edgecolors=DARK, linewidths=0.8, zorder=4)
    ax.set(xlabel="Cardinality similarity", ylabel="Feature-set Jaccard", xlim=(0.57, 1.02), ylim=(-0.01, 0.31))
    pair_one = mpl.lines.Line2D([], [], marker="o", linestyle="none", markersize=4.2, markerfacecolor=DARK, markeredgecolor=DARK, label="Repeat 1 pair")
    pair_two = mpl.lines.Line2D([], [], marker="s", linestyle="none", markersize=4.2, markerfacecolor="white", markeredgecolor=DARK, label="Repeat 2 pair")
    median_handle = mpl.lines.Line2D([], [], marker="o", linestyle="none", markersize=6.0, markerfacecolor="white", markeredgecolor=DARK, markeredgewidth=1.2, label="Median")
    ax.legend(handles=[pair_one, pair_two, median_handle], frameon=False, ncol=1, loc="upper left", handletextpad=0.35, labelspacing=0.3)
    panel_label(ax, "d)", x=-0.10, y=1.055)
    clean_axis(ax)
    fig.legend(handles=branch_handles(), frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 0.012), handletextpad=0.35, columnspacing=1.0)
    save_figure(fig, output / "figure_4_strengthened", manifest)


def supplementary_locking_audit(candidates: pd.DataFrame, output: Path, manifest: list[dict]) -> None:
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    pdf_path = output / "candidate_supplementary_figure_S25_full_locking_audit.pdf"
    metadata = {"Creator": "WrapEvoFS reproducible TCGA v1/v2 analysis", "CreationDate": None, "ModDate": None}
    page_paths = []
    png_paths = []
    for repeat in (1, 2):
        fig, axes = plt.subplots(3, 5, figsize=(FIGURE_WIDTH_IN, 7.2), sharex=True, sharey=True)
        fig.subplots_adjust(left=0.09, right=0.99, bottom=0.09, top=0.89, hspace=0.42, wspace=0.23)
        for row_index, branch in enumerate(BRANCHES):
            for fold in range(1, 6):
                ax = axes[row_index, fold - 1]
                subset = candidates.loc[candidates["outer_repeat"].eq(repeat) & candidates["outer_fold"].eq(fold) & candidates["branch"].eq(branch)]
                ax.axvspan(0, DELTA, color=PALE, zorder=0)
                ax.scatter(subset["absolute_regret"], subset["jaccard_distance_to_highest"], color=COLORS[branch], s=18, alpha=0.65, edgecolors="none")
                chosen = subset.loc[subset["selected"]]
                highest = subset.sort_values(["locking_score", "feature_count", "stable_mask_hash"], ascending=[False, True, True]).iloc[[0]]
                ax.scatter(highest["absolute_regret"], highest["jaccard_distance_to_highest"], marker="o", s=32, facecolors="white", edgecolors=DARK, linewidths=0.8, zorder=3)
                ax.scatter(chosen["absolute_regret"], chosen["jaccard_distance_to_highest"], marker="D", s=29, facecolors="white", edgecolors=COLORS[branch], linewidths=0.9, zorder=4)
                ax.axvline(DELTA, color=MID, linestyle="--", linewidth=0.65)
                ax.set_title(f"Fold {fold}", fontsize=7.0, pad=4)
                if fold == 1:
                    ax.set_ylabel(f"{BRANCH_LABELS[branch]}\nJaccard distance")
                if row_index == 2:
                    ax.set_xlabel("Empirical regret")
                clean_axis(ax)
        candidate_handle = mpl.lines.Line2D([], [], marker="o", linestyle="none", markersize=4.2, markerfacecolor=DARK, markeredgecolor="none", alpha=0.65, label="Saved candidate")
        highest_handle = mpl.lines.Line2D([], [], marker="o", linestyle="none", markersize=5.2, markerfacecolor="white", markeredgecolor=DARK, label="Highest score")
        selected_handle = mpl.lines.Line2D([], [], marker="D", linestyle="none", markersize=5.0, markerfacecolor="white", markeredgecolor=MID, label="Selected medoid")
        fig.legend(handles=[candidate_handle, highest_handle, selected_handle], loc="upper center", bbox_to_anchor=(0.5, 0.94), ncol=3, frameon=False)
        fig.suptitle(f"Repeat {repeat}", fontsize=8.3, y=0.965)
        png_path = output / f"candidate_supplementary_figure_S25_repeat_{repeat}.png"
        page_path = output / f"candidate_supplementary_figure_S25_repeat_{repeat}.pdf"
        fig.savefig(png_path, dpi=600, metadata={"Software": "WrapEvoFS"})
        page_paths.append(page_path)
        png_paths.append(png_path)
        plt.close(fig)
    page_size = (FIGURE_WIDTH_IN * 72.0, 7.2 * 72.0)
    for png_path, page_path in zip(png_paths, page_paths):
        page_canvas = canvas.Canvas(str(page_path), pagesize=page_size, pageCompression=1, invariant=1)
        page_canvas.drawImage(ImageReader(str(png_path)), 0, 0, width=page_size[0], height=page_size[1])
        page_canvas.showPage()
        page_canvas.save()
    combined_canvas = canvas.Canvas(str(pdf_path), pagesize=page_size, pageCompression=1, invariant=1)
    combined_canvas.setCreator("WrapEvoFS reproducible TCGA v1/v2 analysis")
    for png_path in png_paths:
        combined_canvas.drawInlineImage(str(png_path), 0, 0, width=page_size[0], height=page_size[1])
        combined_canvas.showPage()
    combined_canvas.save()
    manifest.append({"file": pdf_path.name, "sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(), "bytes": pdf_path.stat().st_size})
    for page_path in page_paths:
        manifest.append({"file": page_path.name, "sha256": hashlib.sha256(page_path.read_bytes()).hexdigest(), "bytes": page_path.stat().st_size})


def supplementary_stability(selected: pd.DataFrame, agreement: pd.DataFrame, outer_pairs: pd.DataFrame, output: Path, manifest: list[dict]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(FIGURE_WIDTH_IN, 2.65))
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.20, top=0.86, wspace=0.48)
    ax = axes[0]
    x = np.arange(2)
    for repeat in (1, 2):
        for branch in BRANCHES:
            row = agreement.loc[agreement["branch"].eq(branch) & agreement["outer_repeat"].eq(repeat)].iloc[0]
            values = [
                row["mean_fold_level_within_bank_seed_jaccard"],
                row["mean_fold_level_within_bank_nogueira_stability"],
            ]
            ax.scatter(
                x,
                values,
                marker="o" if repeat == 1 else "s",
                facecolors=COLORS[branch] if repeat == 1 else "white",
                edgecolors=COLORS[branch],
                s=25,
                linewidths=0.9,
                zorder=3,
            )
    ax.set_xticks(x, ["Jaccard", "Nogueira"])
    ax.set_ylabel("Agreement")
    ax.axhline(0, color=LIGHT, linewidth=0.7)
    repeat_one = mpl.lines.Line2D([], [], marker="o", linestyle="none", markersize=4.5, markerfacecolor=DARK, markeredgecolor=DARK, label="Repeat 1")
    repeat_two = mpl.lines.Line2D([], [], marker="s", linestyle="none", markersize=4.5, markerfacecolor="white", markeredgecolor=DARK, label="Repeat 2")
    ax.legend(handles=[repeat_one, repeat_two], frameon=False, ncol=2, loc="lower left", handletextpad=0.35, columnspacing=0.7)
    panel_label(ax, "a)", y=1.06)
    clean_axis(ax)

    ax = axes[1]
    positions = np.arange(3)
    for index, branch in enumerate(BRANCHES):
        values = outer_pairs.loc[outer_pairs["branch"].eq(branch), "jaccard"].to_numpy(float)
        ax.boxplot(values, positions=[index], widths=0.48, showfliers=False, patch_artist=True, boxprops={"facecolor": COLORS[branch], "alpha": 0.22, "edgecolor": COLORS[branch]}, medianprops={"color": DARK}, whiskerprops={"color": COLORS[branch]}, capprops={"color": COLORS[branch]})
        jitter = np.linspace(-0.10, 0.10, len(values))
        ax.scatter(index + jitter, values, s=9, color=COLORS[branch], alpha=0.45, edgecolors="none")
    ax.set_xticks(positions, [BRANCH_LABELS[b] for b in BRANCHES], rotation=20, ha="right")
    ax.set_ylabel("Locked-set Jaccard")
    panel_label(ax, "b)", y=1.06)
    clean_axis(ax)

    ax = axes[2]
    for branch in BRANCHES:
        subset = selected.loc[selected["branch"].eq(branch)]
        fractions = subset["scnv_count"] / subset["feature_count"]
        ax.scatter(subset["feature_count"], fractions, color=COLORS[branch], s=22, alpha=0.70, label=BRANCH_LABELS[branch])
    ax.set(xlabel="Feature count", ylabel="SCNV fraction", ylim=(-0.01, max(0.13, (selected["scnv_count"] / selected["feature_count"]).max() * 1.10)))
    ax.legend(handles=branch_handles(), frameon=False, loc="upper right", handletextpad=0.35)
    panel_label(ax, "c)", y=1.06)
    clean_axis(ax)
    save_figure(fig, output / "candidate_supplementary_figure_S26_feature_stability", manifest)


def supplementary_performance(aggregate: Path, output: Path, manifest: list[dict]) -> None:
    metrics = pd.read_csv(aggregate / "oof_metrics.csv", float_precision="round_trip")
    differences = pd.read_csv(aggregate / "paired_current_minus_comparator.csv", float_precision="round_trip")
    counts = pd.read_csv(aggregate / "feature_counts_by_condition.csv", float_precision="round_trip")
    fig, axes = plt.subplots(1, 3, figsize=(FIGURE_WIDTH_IN, 3.55))
    fig.subplots_adjust(left=0.145, right=0.99, bottom=0.29, top=0.84, wspace=0.58)
    offsets = {"svm_l1": -0.16, "xgboost": 0, "boruta_rf": 0.16}
    ax = axes[0]
    subset = metrics.loc[metrics["metric"].eq("macro_ovr_auroc")]
    y = np.arange(len(METHODS))[::-1]
    for branch in BRANCHES:
        rows = subset.loc[subset["branch"].eq(branch)].set_index("method").loc[list(METHODS)]
        yy = y + offsets[branch]
        ax.errorbar(rows["estimate"], yy, xerr=[rows["estimate"] - rows["ci_low"], rows["ci_high"] - rows["estimate"]], fmt="o", color=COLORS[branch], markersize=3.6, elinewidth=0.8, capsize=1.8, label=BRANCH_LABELS[branch])
    ax.set_yticks(y, [METHOD_LABELS[m] for m in METHODS])
    ax.set_xlabel("Macro OVR AUROC")
    panel_label(ax, "a)", y=1.06)
    clean_axis(ax)

    ax = axes[1]
    comps = ["direct", "rfecv_only", "highest_locking_score", "legacy_top3_medoid", "unrestricted_medoid"]
    rows = differences.loc[differences["metric"].eq("macro_ovr_auroc")]
    y = np.arange(len(comps))[::-1]
    for branch in BRANCHES:
        branch_rows = rows.loc[rows["branch"].eq(branch)].set_index("comparator").loc[comps]
        yy = y + offsets[branch]
        ax.errorbar(branch_rows["difference"], yy, xerr=[branch_rows["difference"] - branch_rows["ci_low"], branch_rows["ci_high"] - branch_rows["difference"]], fmt="o", color=COLORS[branch], markersize=3.6, elinewidth=0.8, capsize=1.8)
    ax.axvline(0, color=LIGHT, linewidth=0.8)
    ax.set_yticks(y, [METHOD_LABELS[m] for m in comps])
    ax.set_xlabel("Regret medoid - comparator")
    panel_label(ax, "b)", y=1.06)
    clean_axis(ax)

    ax = axes[2]
    positions = np.arange(len(METHODS))[::-1]
    for branch in BRANCHES:
        means = counts.loc[counts["branch"].eq(branch)].groupby("method")["feature_count"].mean().reindex(METHODS)
        ax.scatter(means, positions + offsets[branch], color=COLORS[branch], s=19, alpha=0.90, label=BRANCH_LABELS[branch])
    ax.set_yticks(positions, [METHOD_LABELS[m] for m in METHODS])
    ax.set_xlabel("Mean feature count")
    ax.set_xlim(-2, max(105, float(counts["feature_count"].max()) * 1.05))
    panel_label(ax, "c)", y=1.06)
    clean_axis(ax)
    handles, labels = axes[2].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 0.015), handletextpad=0.4, columnspacing=1.2)
    save_figure(fig, output / "candidate_supplementary_figure_S27_nested_comparator_audit", manifest)


def summary_json(candidates: pd.DataFrame, banks: pd.DataFrame, selected: pd.DataFrame, agreement: pd.DataFrame, outer_pairs: pd.DataFrame, aggregate: Path) -> dict:
    changed = banks.loc[banks["selected_differs_highest"]]
    selected_scnv = int(selected["scnv_count"].sum())
    selected_total = int(selected["feature_count"].sum())
    oof = pd.read_csv(aggregate / "oof_metrics.csv", float_precision="round_trip")
    differences = pd.read_csv(aggregate / "paired_current_minus_comparator.csv", float_precision="round_trip")
    return {
        "candidate_banks": len(banks),
        "saved_ga_candidates": len(candidates),
        "eligible_pool_size_counts": {str(int(key)): int(value) for key, value in banks["eligible_pool_size"].value_counts().sort_index().items()},
        "maximum_selected_regret": float(banks["selected_regret"].max()),
        "all_selected_regrets_within_delta": bool((banks["selected_regret"] <= DELTA + 1e-12).all()),
        "medoid_differs_from_highest_count": int(len(changed)),
        "changed_banks_positive_gain_count": int((changed["representativeness_gain"] > 0).sum()),
        "changed_bank_gain_mean": float(changed["representativeness_gain"].mean()),
        "changed_bank_gain_median": float(changed["representativeness_gain"].median()),
        "within_bank_seed_jaccard_mean": float(agreement["mean_fold_level_within_bank_seed_jaccard"].mean()),
        "across_outer_fold_jaccard_mean": float(outer_pairs["jaccard"].mean()),
        "across_outer_fold_jaccard_median": float(outer_pairs["jaccard"].median()),
        "cardinality_similarity_mean": float(outer_pairs["cardinality_similarity"].mean()),
        "cardinality_similarity_median": float(outer_pairs["cardinality_similarity"].median()),
        "outer_pairs_q_ge_0.9": int((outer_pairs["cardinality_similarity"] >= 0.9).sum()),
        "outer_pairs_q_ge_0.9_and_j_le_0.05": int(((outer_pairs["cardinality_similarity"] >= 0.9) & (outer_pairs["jaccard"] <= 0.05)).sum()),
        "selected_features_total_with_multiplicity": selected_total,
        "selected_scnv_total_with_multiplicity": selected_scnv,
        "selected_scnv_fraction": selected_scnv / selected_total,
        "duplicate_mask_banks": 0,
        "oof_macro_ovr_auroc": oof.loc[oof["metric"].eq("macro_ovr_auroc")].to_dict("records"),
        "current_minus_comparator_macro_ovr_auroc": differences.loc[differences["metric"].eq("macro_ovr_auroc")].to_dict("records"),
        "claim_boundary": "Repeated internal OOF performance and participant-partition sensitivity in one TCGA-derived cohort; not external validity, biomarker stability, causal biology, clinical utility, or global predictive superiority.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--results-root", type=Path)
    source_group.add_argument("--source-data-dir", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    configure_style()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.results_root is not None:
        data_dir = args.output_dir / "source_data"
        data_dir.mkdir(parents=True, exist_ok=True)
        candidates, banks, selected, agreement, outer_pairs, method_sets = read_analysis(args.results_root)
        save_frame(candidates, data_dir / "candidate_level_geometry.csv")
        save_frame(banks, data_dir / "bank_level_locking_summary.csv")
        save_frame(selected, data_dir / "selected_feature_sets.csv")
        save_frame(agreement, data_dir / "agreement_by_repeat_branch.csv")
        save_frame(outer_pairs, data_dir / "outer_fold_pairwise_stability.csv")
        save_frame(method_sets, data_dir / "method_feature_sets.csv")
        aggregate = args.results_root / "aggregate"
        for name in ("oof_metrics.csv", "paired_current_minus_comparator.csv", "feature_counts_by_condition.csv", "repeat_oof_metrics.csv", "fold_metrics.csv"):
            frame = pd.read_csv(aggregate / name)
            save_frame(frame, data_dir / name)
    else:
        data_dir = args.source_data_dir
        candidates = pd.read_csv(data_dir / "candidate_level_geometry.csv", dtype={"canonical_mask": str, "stable_mask_hash": str, "candidate_universe_sha256": str}, float_precision="round_trip")
        banks = pd.read_csv(data_dir / "bank_level_locking_summary.csv", float_precision="round_trip")
        selected = pd.read_csv(data_dir / "selected_feature_sets.csv", float_precision="round_trip")
        agreement = pd.read_csv(data_dir / "agreement_by_repeat_branch.csv", float_precision="round_trip")
        outer_pairs = pd.read_csv(data_dir / "outer_fold_pairwise_stability.csv", float_precision="round_trip")
        aggregate = data_dir
    manifest: list[dict] = []
    figure_6(candidates, banks, agreement, outer_pairs, args.output_dir, manifest)
    supplementary_locking_audit(candidates, args.output_dir, manifest)
    supplementary_stability(selected, agreement, outer_pairs, args.output_dir, manifest)
    supplementary_performance(aggregate, args.output_dir, manifest)
    summary = summary_json(candidates, banks, selected, agreement, outer_pairs, aggregate)
    (args.output_dir / "ANALYSIS_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "FIGURE_SHA256_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
