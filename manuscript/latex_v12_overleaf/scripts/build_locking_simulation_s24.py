"""Build Supplementary Figure S24 (SVG) and Table S25 from frozen summaries.

Only compact, equal-scenario aggregates from the completed 4,995,000-bank run
are read. This standard-library builder performs no simulation, candidate
generation, GA, classifier fit, or empirical analysis. PDF and PNG rendering is
handled by ``render_locking_simulation_s24.ps1``.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
V12 = HERE.parent
DATA = V12 / "supplementary_data" / "locking_rule_simulation"
FIGURES = V12 / "figures"
TABLES = V12 / "tables"

COLORS = {
    "aligned": "#0072B2",
    "competing": "#009E73",
    "misleading": "#D55E00",
    "highest_score": "#0072B2",
    "legacy_top3_medoid": "#777777",
    "full_bank_medoid": "#E69F00",
}
LABELS = {
    "aligned": "Aligned",
    "competing": "Competing",
    "misleading": "Misleading",
    "highest_score": "Highest score",
    "legacy_top3_medoid": "Legacy top-3 medoid",
    "full_bank_medoid": "Full-bank medoid",
}


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f(value: str | float) -> float:
    return float(value)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_text(x: float, y: float, value: object, *, size: int = 22, anchor: str = "middle", weight: str = "normal", rotate: float | None = None, fill: str = "#222222") -> str:
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{fill}"{transform}>{esc(value)}</text>'


def line(x1: float, y1: float, x2: float, y2: float, *, color: str = "#263746", width: float = 2.0, dash: str | None = None, opacity: float = 1.0) -> str:
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}" opacity="{opacity}"{extra}/>'


def circle(x: float, y: float, *, radius: float = 7.0, color: str = "#222222", fill: str | None = None) -> str:
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" stroke="{color}" stroke-width="2.4" fill="{fill or color}"/>'


def square(x: float, y: float, *, radius: float = 6.5, color: str = "#222222") -> str:
    return f'<rect x="{x-radius:.2f}" y="{y-radius:.2f}" width="{2*radius:.2f}" height="{2*radius:.2f}" stroke="{color}" stroke-width="2.2" fill="{color}"/>'


def diamond(x: float, y: float, *, radius: float = 8.0, color: str = "#222222") -> str:
    points = f"{x:.2f},{y-radius:.2f} {x+radius:.2f},{y:.2f} {x:.2f},{y+radius:.2f} {x-radius:.2f},{y:.2f}"
    return f'<polygon points="{points}" stroke="{color}" stroke-width="2.2" fill="{color}"/>'


def polyline(points: list[tuple[float, float]], *, color: str, width: float = 3.2, fill: str = "none", opacity: float = 1.0) -> str:
    value = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return f'<polyline points="{value}" stroke="{color}" stroke-width="{width}" fill="{fill}" opacity="{opacity}" stroke-linejoin="round" stroke-linecap="round"/>'


def axes(parts: list[str], *, x0: float, x1: float, y0: float, y1: float, xticks: list[tuple[float, str]], yticks: list[tuple[float, str]], xlabel: str, ylabel: str) -> None:
    parts.extend([line(x0, y1, x1, y1, width=2.2), line(x0, y0, x0, y1, width=2.2)])
    for x, label in xticks:
        parts.append(line(x, y1, x, y1 + 9, width=1.8))
        parts.append(svg_text(x, y1 + 31, label, size=20))
    for y, label in yticks:
        parts.append(line(x0 - 9, y, x0, y, width=1.8))
        parts.append(svg_text(x0 - 16, y + 7, label, size=20, anchor="end"))
    parts.append(svg_text((x0 + x1) / 2, y1 + 67, xlabel, size=22))
    parts.append(svg_text(x0 - 77, (y0 + y1) / 2, ylabel, size=22, rotate=-90))


def map_linear(value: float, source_min: float, source_max: float, target_min: float, target_max: float) -> float:
    return target_min + (value - source_min) * (target_max - target_min) / (source_max - source_min)


def build_figure() -> str:
    panel_a = read_csv("figure_s24_panel_a.csv")
    panel_b = sorted(read_csv("figure_s24_panel_b.csv"), key=lambda row: f(row["delta"]))
    panel_c = read_csv("figure_s24_panel_c.csv")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="170mm" height="67mm" viewBox="0 0 1700 670">',
        '<rect width="1700" height="670" fill="white"/>',
        '<g font-family="Arial, Helvetica, DejaVu Sans, sans-serif">',
    ]

    # Panel a: primary topology-by-noise interaction.
    parts.extend([svg_text(45, 48, "a)", size=34, anchor="start", weight="bold"), svg_text(330, 59, "Score noise and topology", size=26)])
    ax_a = (130.0, 590.0, 115.0, 545.0)
    x0, x1, y0, y1 = ax_a
    mx = lambda value: map_linear(value, 0.0, 4.0, x0, x1)
    my = lambda value: map_linear(value, -1.4, 5.5, y1, y0)
    axes(
        parts,
        x0=x0,
        x1=x1,
        y0=y0,
        y1=y1,
        xticks=[(mx(v), str(v)) for v in (0, 0.5, 1, 2, 4)],
        yticks=[(my(v), str(v)) for v in (-1, 0, 1, 2, 3, 4, 5)],
        xlabel="Locking-score noise ratio",
        ylabel="Current - highest oracle regret (0.001 units)",
    )
    parts.append(line(x0, my(0), x1, my(0), color="#555555", width=1.8))
    for topology in ("aligned", "competing", "misleading"):
        rows = sorted((row for row in panel_a if row["topology"] == topology), key=lambda row: f(row["score_noise_ratio"]))
        upper = [(mx(f(row["score_noise_ratio"])), my(1000 * f(row["q75"]))) for row in rows]
        lower = [(mx(f(row["score_noise_ratio"])), my(1000 * f(row["q25"]))) for row in reversed(rows)]
        polygon = " ".join(f"{x:.2f},{y:.2f}" for x, y in upper + lower)
        parts.append(f'<polygon points="{polygon}" fill="{COLORS[topology]}" opacity="0.10" stroke="none"/>')
        points = [(mx(f(row["score_noise_ratio"])), my(1000 * f(row["mean_current_minus_highest"]))) for row in rows]
        parts.append(polyline(points, color=COLORS[topology]))
        parts.extend(circle(x, y, radius=6.5, color=COLORS[topology]) for x, y in points)
    legend_x = [164, 302, 445]
    for x, topology in zip(legend_x, ("aligned", "competing", "misleading")):
        parts.extend([line(x, 90, x + 28, 90, color=COLORS[topology], width=3), circle(x + 14, 90, radius=5.5, color=COLORS[topology]), svg_text(x + 37, 97, LABELS[topology], size=18, anchor="start")])

    # Panel b: tolerance trade-off in the matched 27-scenario subset.
    parts.extend([svg_text(630, 48, "b)", size=34, anchor="start", weight="bold"), svg_text(844, 59, "Tolerance trade-off", size=26)])
    ax_b = (720.0, 1040.0, 115.0, 545.0)
    x0, x1, y0, y1 = ax_b
    mx = lambda value: map_linear(value, -0.2, 5.15, x0, x1)
    my = lambda value: map_linear(value, 0.414, 0.4625, y1, y0)
    axes(
        parts,
        x0=x0,
        x1=x1,
        y0=y0,
        y1=y1,
        xticks=[(mx(v), str(v)) for v in (0, 1, 2, 3, 4, 5)],
        yticks=[(my(v), f"{v:.2f}") for v in (0.42, 0.43, 0.44, 0.45, 0.46)],
        xlabel="Mean empirical regret (0.001 units)",
        ylabel="Mean full-bank Jaccard",
    )
    points = [(mx(1000 * f(row["empirical_regret"])), my(f(row["full_bank_mean_jaccard"]))) for row in panel_b]
    parts.append(polyline(points, color="#2F5D7C", width=3.4))
    label_offsets = [(10, 23), (10, -13), (10, -12), (-8, -15)]
    for row, (x, y), (dx, dy) in zip(panel_b, points, label_offsets):
        parts.append(circle(x, y, radius=7.0, color="#2F5D7C"))
        delta = f(row["delta"])
        label = "0" if delta == 0 else f"{delta:.3f}".rstrip("0")
        parts.append(svg_text(x + dx, y + dy, f"delta={label}", size=18, anchor="end" if dx < 0 else "start"))

    # Panel c: matched candidate-bank-size sensitivity.
    parts.extend([svg_text(1080, 48, "c)", size=34, anchor="start", weight="bold"), svg_text(1400, 59, "Candidate-bank size", size=26)])
    ax_c = (1190.0, 1665.0, 115.0, 545.0)
    x0, x1, y0, y1 = ax_c
    mx = lambda value: map_linear(math.log10(value), math.log10(3), math.log10(100), x0, x1)
    my = lambda value: map_linear(value, -0.62, 0.25, y1, y0)
    axes(
        parts,
        x0=x0,
        x1=x1,
        y0=y0,
        y1=y1,
        xticks=[(mx(v), str(v)) for v in (3, 5, 10, 20, 50, 100)],
        yticks=[(my(v), f"{v:.1f}") for v in (-0.6, -0.4, -0.2, 0, 0.2)],
        xlabel="Retained candidates, R",
        ylabel="Current - comparator oracle regret (0.001 units)",
    )
    parts.append(line(x0, my(0), x1, my(0), color="#555555", width=1.8))
    for comparator in ("highest_score", "legacy_top3_medoid", "full_bank_medoid"):
        rows = sorted((row for row in panel_c if row["comparator"] == comparator), key=lambda row: f(row["candidate_count"]))
        points = [(mx(f(row["candidate_count"])), my(1000 * f(row["mean_current_minus_comparator"]))) for row in rows]
        parts.append(polyline(points, color=COLORS[comparator]))
        for x, y in points:
            if comparator == "highest_score":
                parts.append(circle(x, y, radius=6.0, color=COLORS[comparator]))
            elif comparator == "legacy_top3_medoid":
                parts.append(square(x, y, radius=5.8, color=COLORS[comparator]))
            else:
                parts.append(diamond(x, y, radius=7.0, color=COLORS[comparator]))
    legend_y = [89, 111, 133]
    for y, comparator in zip(legend_y, ("highest_score", "legacy_top3_medoid", "full_bank_medoid")):
        parts.append(line(1242, y, 1270, y, color=COLORS[comparator], width=3))
        if comparator == "highest_score":
            parts.append(circle(1256, y, radius=5.5, color=COLORS[comparator]))
        elif comparator == "legacy_top3_medoid":
            parts.append(square(1256, y, radius=5.0, color=COLORS[comparator]))
        else:
            parts.append(diamond(1256, y, radius=6.0, color=COLORS[comparator]))
        parts.append(svg_text(1280, y + 6, LABELS[comparator], size=17, anchor="start"))

    parts.extend(["</g>", "</svg>"])
    output = FIGURES / "figure_s24.svg"
    output.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")
    return sha256(output)


def rule_label(rule: str) -> str:
    return {
        "highest_score": "Highest score",
        "legacy_top3_medoid": "Legacy top-3 medoid",
        "full_bank_medoid": "Full-bank medoid",
        "regret_medoid": "Regret-constrained medoid",
    }[rule]


def build_table() -> str:
    primary = read_csv("table_s25_primary_summary.csv")
    audit = read_csv("table_s25_regret_audit.csv")
    decisions = read_csv("table_s25_decision_paths.csv")
    rows_a = [
        f"{rule_label(row['rule'])} & {f(row['oracle_regret']):.4f} & {f(row['group_aware_recovery']):.3f} & {f(row['exact_feature_recovery']):.3f} & {f(row['full_bank_mean_jaccard']):.3f} & {f(row['score_optimism']):.4f} & {100*f(row['oracle_regret_failure_probability']):.3f} \\\\"
        for row in primary
    ]
    status = {"highest_score": "0 by definition", "legacy_top3_medoid": "Not constrained", "full_bank_medoid": "Not constrained", "regret_medoid": "0 / 4,995,000"}
    rows_b = [
        f"{rule_label(row['rule'])} & {f(row['mean_empirical_regret']):.4f} & {int(f(row['scenarios_mean_gt_delta']))} / 162 & {f(row['max_scenario_q95']):.4f} & {status[row['rule']]} \\\\"
        for row in audit
    ]
    decision_labels = {"singleton": "Singleton eligible pool", "unique_jaccard": "Unique Jaccard medoid", "higher_locking_score": "Higher locking score", "smaller_feature_count": "Smaller feature count", "stable_mask_hash": "Stable mask hash", "exact_duplicate_provenance": "Exact-duplicate provenance", "hash_stage_probability": "Hash stage reached (inclusive)"}
    rows_c = []
    for row in decisions:
        precision = 5 if row["decision_metric"] == "smaller_feature_count" else 3
        rows_c.append(f"{decision_labels[row['decision_metric']]} & {100*f(row['mean_probability']):.{precision}f} \\\\"
        )

    latex = """\\begin{table}[p]
\\centering
\\caption{Controlled synthetic candidate-bank locking simulation under the primary $R=5$ and $\\delta=0.01$ design.}
\\label{tab:supp25}
\\scriptsize
\\textit{Panel A. Equal-scenario primary operating characteristics}\\par\\smallskip
\\setlength{\\tabcolsep}{3.2pt}
\\begin{tabular}{lrrrrrr}
\\toprule
Rule & Oracle regret & Group recovery & Exact recovery & Full-bank Jaccard & Score optimism & Failure (\\%) \\\\
\\midrule
""" + "\n".join(rows_a) + """
\\bottomrule
\\end{tabular}

\\medskip
\\textit{Panel B. Primary empirical-regret audit}\\par\\smallskip
\\setlength{\\tabcolsep}{4.0pt}
\\begin{tabular}{lrrrp{31mm}}
\\toprule
Rule & Mean regret & Scenario means $>0.01$ & Maximum scenario q95 & Individual guarantee audit \\\\
\\midrule
""" + "\n".join(rows_b) + """
\\bottomrule
\\end{tabular}

\\medskip
\\textit{Panel C. Current-rule primary decision paths}\\par\\smallskip
\\begin{tabular}{lr}
\\toprule
Decision stage & Probability (\\%) \\\\
\\midrule
""" + "\n".join(rows_c) + """
\\bottomrule
\\end{tabular}

\\begin{minipage}{0.98\\linewidth}\\scriptsize\\vspace{0.35em}
Primary entries are equal-scenario means across 162 prespecified scenarios with 10,000 banks each (1,620,000 banks); the complete sensitivity workload comprised 4,995,000 banks across 513 scenarios. Hidden oracle utility $T$ is not AUROC. Lower values are preferable for oracle regret and score optimism; higher values are preferable for recovery and Jaccard. Failure denotes oracle regret $>0.02$; q95 denotes the within-scenario 95th percentile. The current rule had no configured empirical-regret violation in the complete workload. Highest-score selection has zero empirical regret by definition, whereas the two medoid comparators have no metric-scale regret constraint. Panel C probabilities are mutually exclusive except for the inclusive hash-stage row. Exact duplicate masks retained their multiplicity as voting candidates. No GA, classifier, or participant-level dataset was simulated or fitted.
\\end{minipage}
\\end{table}
"""
    output = TABLES / "table_47.tex"
    output.write_text(latex, encoding="utf-8", newline="\n")
    return sha256(output)


def validate_sources() -> None:
    primary = {row["rule"]: row for row in read_csv("table_s25_primary_summary.csv")}
    audit = {row["rule"]: row for row in read_csv("table_s25_regret_audit.csv")}
    deltas = {f(row["delta"]) for row in read_csv("figure_s24_panel_b.csv")}
    if set(primary) != {"highest_score", "legacy_top3_medoid", "full_bank_medoid", "regret_medoid"}:
        raise RuntimeError("Primary source table is incomplete")
    if any(int(f(row["n_scenarios"])) != 162 for row in primary.values()):
        raise RuntimeError("Primary source table must contain 162 scenarios per rule")
    if abs(f(primary["regret_medoid"]["empirical_regret"]) - 0.00130458463951) > 1e-14:
        raise RuntimeError("Current-rule empirical regret does not match the frozen summary")
    if int(f(audit["regret_medoid"]["scenarios_mean_gt_delta"])) != 0 or f(audit["regret_medoid"]["max_scenario_q95"]) >= 0.01:
        raise RuntimeError("Current-rule feasibility summary failed validation")
    if deltas != {0.0, 0.005, 0.01, 0.02}:
        raise RuntimeError("Tolerance source rows are incomplete")


def main() -> None:
    validate_sources()
    svg_hash = build_figure()
    table_hash = build_table()
    manifest = {
        "protocol_sha256": "6bb91ec337c331aa4b69646f5166831503405d2721a40d16be75718179418d6f",
        "builder": "scripts/build_locking_simulation_s24.py",
        "source_sha256": {path.name: sha256(path) for path in sorted(DATA.glob("*.csv"))},
        "figure_s24_svg_sha256": svg_hash,
        "table_47_sha256": table_hash,
        "figure_width_mm": 170,
        "figure_height_mm": 67,
        "grid": False,
        "panels": ["a", "b", "c"],
    }
    (DATA / "BUILD_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
