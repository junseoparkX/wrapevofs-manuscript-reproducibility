"""Build v11 Supplementary Figure S18 and Table S16 from frozen summaries.

This is a presentation-only builder.  It does not run GA, RFECV, Direct
selection, locking-score estimation, held-out evaluation, or any other model.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import shutil

import matplotlib
from matplotlib.colors import PowerNorm
from matplotlib.patches import Patch
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


CENTERS = ["Emory", "Mayo", "Mount Sinai", "Rush"]
CONDITIONS = [
    ("SVM-L1", "Small-cap", "SVM-L1\nSmall"),
    ("SVM-L1", "Reference-cap", "SVM-L1\nReference"),
    ("XGBoost", "Small-cap", "XGBoost\nSmall"),
    ("XGBoost", "Reference-cap", "XGBoost\nReference"),
    ("Boruta-RF", "Small-cap", "Boruta-RF\nSmall"),
    ("Boruta-RF", "Reference-cap", "Boruta-RF\nReference"),
]

LEGACY = "#707070"
RECOMMENDED = "#4F7188"
GRID = "#D8DEE4"
TEXT = "#263746"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def integer(row: dict[str, str], field: str) -> int:
    return int(float(row[field]))


def number(row: dict[str, str], field: str) -> float:
    return float(row[field])


def format_number(value: str | float, digits: int = 4) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "NA"
    if not math.isfinite(numeric):
        return "NA"
    return f"{numeric:.{digits}f}"


def annotate_heatmap(axis: plt.Axes, values: np.ndarray, maximum: float) -> None:
    for row_index in range(values.shape[0]):
        for column_index in range(values.shape[1]):
            value = values[row_index, column_index]
            color = "white" if value > maximum * 0.43 else TEXT
            axis.text(
                column_index,
                row_index,
                f"{int(value)}",
                ha="center",
                va="center",
                color=color,
                fontsize=7.2,
                fontweight="normal",
            )


def heatmap_pair(
    fig: plt.Figure,
    spec,
    legacy_values: np.ndarray,
    recommended_values: np.ndarray,
    colorbar_label: str,
    show_rows: bool,
) -> tuple[plt.Axes, plt.Axes]:
    grid = spec.subgridspec(1, 3, width_ratios=[1, 1, 0.045], wspace=0.18)
    maximum = float(max(legacy_values.max(), recommended_values.max(), 1))
    norm = PowerNorm(gamma=0.52, vmin=0, vmax=maximum)
    axes = [fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1])]
    image = None
    for axis_index, (axis, values, title) in enumerate(zip(
        axes,
        [legacy_values, recommended_values],
        ["Original configuration", "Updated configuration"],
    )):
        image = axis.imshow(values, cmap="YlGnBu", norm=norm, aspect="auto")
        annotate_heatmap(axis, values, maximum)
        axis.set_title(title, fontsize=8.4, pad=4)
        axis.set_xticks(range(len(CONDITIONS)), [item[2] for item in CONDITIONS], fontsize=6.2)
        axis.tick_params(axis="x", length=0, pad=3)
        axis.tick_params(axis="y", length=0)
        axis.set_yticks(range(len(CENTERS)))
        axis.set_yticklabels(
            CENTERS if show_rows and axis_index == 0 else [""] * len(CENTERS),
            fontsize=7.4,
        )
        axis.set_xlabel("Branch-cap condition", fontsize=7.2, labelpad=5)
        if show_rows and axis_index == 0:
            axis.set_ylabel("Center", fontsize=7.2, labelpad=8)
        for spine in axis.spines.values():
            spine.set_linewidth(0.55)
            spine.set_color("#B7C1C9")
    color_axis = fig.add_subplot(grid[0, 2])
    colorbar = fig.colorbar(image, cax=color_axis)
    colorbar.ax.tick_params(labelsize=6.7, width=0.5)
    colorbar.outline.set_linewidth(0.5)
    colorbar.set_label(colorbar_label, fontsize=7.2)
    return axes[0], axes[1]


def grouped_bars(
    axis: plt.Axes,
    labels: list[str],
    legacy_values: list[int],
    recommended_values: list[int],
    title: str,
    show_legend: bool = False,
    y_label: str | None = None,
) -> None:
    positions = np.arange(len(labels))
    width = 0.36
    axis.bar(positions - width / 2, legacy_values, width, color=LEGACY, label="Original")
    axis.bar(
        positions + width / 2,
        recommended_values,
        width,
        color=RECOMMENDED,
        label="Updated",
    )
    axis.set_title(title, fontsize=8.1, pad=4, loc="left")
    if y_label is not None:
        axis.set_ylabel(y_label, fontsize=7.2, labelpad=4)
    axis.set_xticks(positions, labels, fontsize=6.8, rotation=18, ha="right")
    axis.tick_params(axis="x", length=0)
    axis.tick_params(axis="y", labelsize=6.8, width=0.5)
    axis.grid(False)
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_linewidth(0.55)
    if show_legend:
        axis.legend(
            frameon=False,
            fontsize=7.0,
            ncol=2,
            handlelength=1.2,
            loc="lower right",
            bbox_to_anchor=(1.0, 1.02),
            borderaxespad=0,
        )


def tex_escape(value: str) -> str:
    return value.replace("&", r"\&").replace("%", r"\%")


def build_table_tex(rows: list[dict[str, str]]) -> str:
    lookup = {(row["Center"], row["Branch"], row["Cap"]): row for row in rows}
    ordered = [lookup[(center, branch, cap)] for center in CENTERS for branch, cap, _ in CONDITIONS]

    center_summary = []
    for center in CENTERS:
        subset = [row for row in ordered if row["Center"] == center]
        center_summary.append(
            (
                center,
                sum(integer(row, "Legacy abs. target deviation") for row in subset),
                sum(integer(row, "Recommended abs. target deviation") for row in subset),
                sum(integer(row, "Legacy all-zero generations") for row in subset),
                sum(integer(row, "Recommended diagnostic all-zero generations") for row in subset),
            )
        )
    branch_summary = []
    for branch in ["SVM-L1", "XGBoost", "Boruta-RF"]:
        subset = [row for row in ordered if row["Branch"] == branch]
        branch_summary.append(
            (
                branch,
                sum(integer(row, "Legacy abs. target deviation") for row in subset),
                sum(integer(row, "Recommended abs. target deviation") for row in subset),
                sum(integer(row, "Legacy all-zero generations") for row in subset),
                sum(integer(row, "Recommended diagnostic all-zero generations") for row in subset),
            )
        )

    lines = [
        r"\begin{table}[p]",
        r"\centering",
        r"\caption{Development-only AMP-AD comparison of the original configuration (zero-truncated objective and top-three Jaccard-medoid locking) with the updated configuration (untruncated objective and regret-constrained medoid locking at absolute $\delta=0.01$) across 24 center--branch--cap conditions.}",
        r"\label{tab:supp16}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2.6pt}",
        r"\renewcommand{\arraystretch}{1.03}",
        r"\textit{A. Aggregate target fidelity and flattening diagnostics}\par\smallskip",
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Group & \multicolumn{2}{c}{Absolute target deviation} & \multicolumn{2}{c}{All-zero generations} \\",
        r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}",
        r" & Orig. & Upd. & Orig. & Upd. \\",
        r"\midrule",
    ]
    for name, legacy_dev, rec_dev, legacy_zero, rec_zero in center_summary:
        lines.append(f"{tex_escape(name)} & {legacy_dev} & {rec_dev} & {legacy_zero} & {rec_zero} \\\\")
    lines.append(r"\midrule")
    for name, legacy_dev, rec_dev, legacy_zero, rec_zero in branch_summary:
        lines.append(f"{tex_escape(name)} & {legacy_dev} & {rec_dev} & {legacy_zero} & {rec_zero} \\\\")
    lines.extend(
        [
            r"\midrule",
            r"Overall & 216 & 137 & 673 & 333 \\",
            r"\bottomrule",
            r"\end{tabular}\par",
            r"\vspace{0.75em}",
            r"\textit{B. Complete condition-level target and flattening results}\par\smallskip",
            r"\resizebox{\linewidth}{!}{%",
            r"\begin{tabular}{lllrrrrrrrrrr}",
            r"\toprule",
            r"Center & Branch & Cap & $k^*$ & \multicolumn{2}{c}{Locked $n$} & \multicolumn{2}{c}{$\lvert n-k^*\rvert$} & \multicolumn{2}{c}{Zero run-best, $n/5$} & \multicolumn{2}{c}{All-zero generations} & Upd. regret \\",
            r"\cmidrule(lr){5-6}\cmidrule(lr){7-8}\cmidrule(lr){9-10}\cmidrule(lr){11-12}",
            r" & & & & Orig. & Upd. & Orig. & Upd. & Orig. & Upd. & Orig. & Upd. & \\",
            r"\midrule",
        ]
    )
    previous_center = None
    for row in ordered:
        if previous_center is not None and row["Center"] != previous_center:
            lines.append(r"\addlinespace[2pt]")
        previous_center = row["Center"]
        lines.append(
            " & ".join(
                [
                    tex_escape(row["Center"]),
                    tex_escape(row["Branch"]),
                    "Small" if row["Cap"] == "Small-cap" else "Reference",
                    row["RFECV target"],
                    row["Legacy locked n"],
                    row["Recommended locked n"],
                    row["Legacy abs. target deviation"],
                    row["Recommended abs. target deviation"],
                    row["Legacy zero run-best fitness, n/5"],
                    row["Recommended diagnostic zero legacy fitness, n/5"],
                    row["Legacy all-zero generations"],
                    row["Recommended diagnostic all-zero generations"],
                    format_number(row["Recommended selected empirical regret"]),
                ]
            )
            + r" \\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}}",
            r"\end{table}",
            "",
            r"\begin{table}[p]",
            r"\ContinuedFloat",
            r"\centering",
            r"\caption[]{Development-only AMP-AD configuration comparison (continued).}",
            r"\scriptsize",
            r"\setlength{\tabcolsep}{3.0pt}",
            r"\renewcommand{\arraystretch}{1.04}",
            r"\textit{C. Fixed development-CV locking score, eligibility, and agreement}\par\smallskip",
            r"\resizebox{\linewidth}{!}{%",
            r"\begin{tabular}{lllrrrrrr}",
            r"\toprule",
            r"Center & Branch & Cap & \multicolumn{2}{c}{Locking score} & Difference & Eligible $E$ & Upd. regret & Upd. mean Jaccard \\",
            r"\cmidrule(lr){4-5}",
            r" & & & Orig. & Upd. & Upd. -- original & & & \\",
            r"\midrule",
        ]
    )
    previous_center = None
    for row in ordered:
        if previous_center is not None and row["Center"] != previous_center:
            lines.append(r"\addlinespace[2pt]")
        previous_center = row["Center"]
        lines.append(
            " & ".join(
                [
                    tex_escape(row["Center"]),
                    tex_escape(row["Branch"]),
                    "Small" if row["Cap"] == "Small-cap" else "Reference",
                    format_number(row["Legacy lock score"]),
                    format_number(row["Recommended lock score"]),
                    format_number(row["Score difference"]),
                    row["Recommended eligible pool size"],
                    format_number(row["Recommended selected empirical regret"]),
                    format_number(row["Recommended selected mean Jaccard"]),
                ]
            )
            + r" \\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}}",
            r"\vspace{0.55em}",
            r"\parbox{0.98\linewidth}{\scriptsize\textit{Note.} Orig., original configuration; Upd., updated configuration. The original configuration used the zero-truncated objective and top-three Jaccard-medoid locking. Updated values were obtained from 120 newly executed full GPU GA runs (five seeds per condition) at the Small and Reference caps using the untruncated objective and regret-constrained medoid locking; High-cap conditions were not rerun. The updated all-zero column is the zero-truncation diagnostic evaluated along each untruncated search history. Actual updated-mode parent-sampling fallbacks were zero. Final updated locking used fixed development-CV scores, absolute regret tolerance 0.01, strict eligible-only pools, and no fallback expansion. Because both candidate generation and locking differ, between-column differences are configuration-level comparisons rather than isolated causal effects of either component. The two Rush singleton pools have undefined mean Jaccard (NA); all 18 newly completed pools contained two to five candidates. Held-out outcomes were not accessed or evaluated. Mean Jaccard was reduced in canonical mask-hash order. In Mount Sinai/SVM-L1/Reference, runs 3 and 5 had the same exact peer-Jaccard multiset but differed by one IEEE-754 unit in the last place under historical versus canonical reduction order; the authoritative package selected run 5 (17 features; regret 0.0037), whereas the older helper selected run 3 (17 features; regret 0). Both were eligible, and target-count summaries were unchanged.}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-table", required=True, type=Path)
    parser.add_argument("--authoritative-manifest", required=True, type=Path)
    parser.add_argument("--manuscript-dir", required=True, type=Path)
    args = parser.parse_args()

    source_table = args.source_table.resolve()
    manifest_path = args.authoritative_manifest.resolve()
    manuscript = args.manuscript_dir.resolve()
    figures = manuscript / "figures"
    data_dir = manuscript / "supplementary_data"
    tables = manuscript / "tables"
    figures.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    rows = read_rows(source_table)
    if len(rows) != 24:
        raise RuntimeError(f"Expected 24 condition rows, found {len(rows)}")
    if any(row["Held-out inputs used"].strip().lower() != "false" for row in rows):
        raise RuntimeError("A condition reports held-out input use")

    lookup = {(row["Center"], row["Branch"], row["Cap"]): row for row in rows}
    missing = [
        key
        for key in [(center, branch, cap) for center in CENTERS for branch, cap, _ in CONDITIONS]
        if key not in lookup
    ]
    if missing:
        raise RuntimeError(f"Missing expected conditions: {missing}")

    def matrix(field: str) -> np.ndarray:
        return np.asarray(
            [
                [integer(lookup[(center, branch, cap)], field) for branch, cap, _ in CONDITIONS]
                for center in CENTERS
            ],
            dtype=float,
        )

    legacy_dev = matrix("Legacy abs. target deviation")
    rec_dev = matrix("Recommended abs. target deviation")
    legacy_zero = matrix("Legacy all-zero generations")
    rec_zero = matrix("Recommended diagnostic all-zero generations")
    zero_run_legacy = sum(
        int(row["Legacy zero run-best fitness, n/5"].split("/")[0]) for row in rows
    )
    zero_run_rec = sum(
        int(row["Recommended diagnostic zero legacy fitness, n/5"].split("/")[0])
        for row in rows
    )
    fallbacks = sum(integer(row, "Recommended uniform fallbacks") for row in rows)
    regrets = np.asarray([number(row, "Recommended selected empirical regret") for row in rows])
    score_differences = np.asarray([number(row, "Score difference") for row in rows])

    assert int(legacy_dev.sum()) == 216
    assert int(rec_dev.sum()) == 137
    assert int(legacy_zero.sum()) == 673
    assert int(rec_zero.sum()) == 333
    assert zero_run_legacy == 4 and zero_run_rec == 0
    assert fallbacks == 0
    assert float(regrets.max()) <= 0.01
    assert math.isclose(float(score_differences.mean()), 0.0009751739552135932, abs_tol=1e-15)

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
            "font.size": 8,
            "axes.edgecolor": TEXT,
            "axes.labelcolor": TEXT,
            "xtick.color": TEXT,
            "ytick.color": TEXT,
            "text.color": TEXT,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
        }
    )
    width_in = 170.0 / 25.4
    fig = plt.figure(figsize=(width_in, 7.7), facecolor="white")
    outer = fig.add_gridspec(3, 1, height_ratios=[1.0, 1.0, 1.18], hspace=0.62)

    heatmap_pair(fig, outer[0], legacy_dev, rec_dev, "Absolute target deviation", True)
    heatmap_pair(fig, outer[1], legacy_zero, rec_zero, "All-zero generations", True)

    bottom = outer[2].subgridspec(2, 2, hspace=1.02, wspace=0.36)
    center_legacy_dev = legacy_dev.sum(axis=1).astype(int).tolist()
    center_rec_dev = rec_dev.sum(axis=1).astype(int).tolist()
    center_legacy_zero = legacy_zero.sum(axis=1).astype(int).tolist()
    center_rec_zero = rec_zero.sum(axis=1).astype(int).tolist()
    branch_labels = ["SVM-L1", "XGBoost", "Boruta-RF"]
    condition_branch_indices = [[0, 1], [2, 3], [4, 5]]
    branch_legacy_dev = [int(legacy_dev[:, indices].sum()) for indices in condition_branch_indices]
    branch_rec_dev = [int(rec_dev[:, indices].sum()) for indices in condition_branch_indices]
    branch_legacy_zero = [int(legacy_zero[:, indices].sum()) for indices in condition_branch_indices]
    branch_rec_zero = [int(rec_zero[:, indices].sum()) for indices in condition_branch_indices]

    grouped_bars(
        fig.add_subplot(bottom[0, 0]),
        CENTERS,
        center_legacy_dev,
        center_rec_dev,
        "Aggregated by center",
        show_legend=False,
        y_label="Absolute target deviation",
    )
    grouped_bars(
        fig.add_subplot(bottom[0, 1]),
        branch_labels,
        branch_legacy_dev,
        branch_rec_dev,
        "Aggregated by GA branch",
    )
    grouped_bars(
        fig.add_subplot(bottom[1, 0]),
        CENTERS,
        center_legacy_zero,
        center_rec_zero,
        "Aggregated by center",
        y_label="All-zero generations",
    )
    grouped_bars(
        fig.add_subplot(bottom[1, 1]),
        branch_labels,
        branch_legacy_zero,
        branch_rec_zero,
        "Aggregated by GA branch",
    )

    fig.legend(
        handles=[Patch(facecolor=LEGACY), Patch(facecolor=RECOMMENDED)],
        labels=["Original", "Updated"],
        frameon=False,
        fontsize=7.0,
        ncol=2,
        handlelength=1.2,
        loc="upper center",
        bbox_to_anchor=(0.52, 0.348),
        borderaxespad=0,
    )

    fig.text(0.025, 0.974, "a)", fontsize=10.5, fontweight="bold")
    fig.text(0.025, 0.666, "b)", fontsize=10.5, fontweight="bold")
    fig.text(0.025, 0.357, "c)", fontsize=10.5, fontweight="bold")
    fig.subplots_adjust(left=0.135, right=0.925, top=0.955, bottom=0.045)

    stem = figures / "figure_s18"
    fig.savefig(stem.with_suffix(".svg"), format="svg", facecolor="white")
    fig.savefig(stem.with_suffix(".pdf"), format="pdf", facecolor="white")
    fig.savefig(stem.with_suffix(".png"), format="png", dpi=600, facecolor="white")
    plt.close(fig)

    destination_csv = data_dir / "Table_S16_AMPAD_FourCenter_Objective_Sensitivity.csv"
    shutil.copyfile(source_table, destination_csv)
    fields = list(rows[0])
    markdown = [
        "| " + " | ".join(fields) + " |",
        "| " + " | ".join(["---"] * len(fields)) + " |",
    ]
    markdown.extend("| " + " | ".join(row[field] for field in fields) + " |" for row in rows)
    (data_dir / "Table_S16_AMPAD_FourCenter_Objective_Sensitivity.md").write_text(
        "\n".join(markdown) + "\n", encoding="utf-8"
    )
    (tables / "table_38.tex").write_text(build_table_tex(rows), encoding="utf-8")

    authoritative_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    provenance = {
        "schema": "WrapEvoFS-v10-S18-S16-four-center-v1",
        "analysis_scope": (
            "development-only AMP-AD comparison of original and updated configurations "
            "across four center-specific development partitions"
        ),
        "presentation_builder_only": True,
        "ga_rerun_performed_by_builder": False,
        "rfecv_or_direct_rerun_performed_by_builder": False,
        "held_out_evaluation_performed_by_builder": False,
        "held_out_inputs_used": False,
        "conditions": 24,
        "full_ga_runs": 120,
        "caps": ["Small-cap", "Reference-cap"],
        "high_cap_rerun": False,
        "display_terminology": {
            "legacy_source_fields": "original configuration",
            "recommended_source_fields": "updated configuration",
        },
        "verified_aggregates": {
            "absolute_target_deviation": {"legacy": 216, "recommended": 137},
            "condition_direction": {"improved": 12, "unchanged": 6, "worsened": 6},
            "zero_run_best": {"legacy": 4, "recommended": 0},
            "all_zero_generations": {"legacy": 673, "recommended": 333},
            "uniform_sampling_fallbacks": 0,
            "maximum_selected_empirical_regret": float(regrets.max()),
            "mean_score_difference": float(score_differences.mean()),
            "median_score_difference": float(np.median(score_differences)),
            "score_difference_range": [
                float(score_differences.min()),
                float(score_differences.max()),
            ],
        },
        "finite_precision_disclosure": {
            "condition": "Mount Sinai/SVM-L1/Reference-cap",
            "authoritative_package_selected_run": 5,
            "older_bundle_helper_selected_run": 3,
            "both_feature_counts": 17,
            "authoritative_selected_regret": 0.003702196570253058,
            "target_count_summaries_changed": False,
        },
        "authoritative_lock_manifest": str(manifest_path),
        "authoritative_lock_manifest_sha256": sha256_file(manifest_path),
        "authoritative_lock_all_empirical_permutations_invariant": (
            authoritative_manifest["all_empirical_candidate_permutations_invariant"]
        ),
        "source_table": str(source_table),
        "source_table_sha256": sha256_file(source_table),
        "outputs": {},
    }
    output_paths = [
        stem.with_suffix(".svg"),
        stem.with_suffix(".pdf"),
        stem.with_suffix(".png"),
        destination_csv,
        data_dir / "Table_S16_AMPAD_FourCenter_Objective_Sensitivity.md",
        tables / "table_38.tex",
    ]
    for path in output_paths:
        provenance["outputs"][path.name] = sha256_file(path)
    (data_dir / "S18_S16_FourCenter_provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
