from __future__ import annotations

import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "revision_outputs"
TABLES = ROOT / "tables"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def f(value: str, digits: int = 4) -> str:
    return f"{float(value):.{digits}f}"


def build_robust_summary() -> str:
    data = rows("S16_ROBUST_STRESS_EXCLUDED_SUMMARY.csv")
    labels = {
        "all_24_conditions": "All 24 conditions",
        "excluding_rush_svm_l1_small": "Excluding Rush/SVM-L1/Small",
        "absolute_target_deviation": "Absolute target deviation",
        "all_zero_generations": "All-zero generations",
    }
    body = []
    for row in data:
        body.append(
            f"{labels[row['scope']]} & {labels[row['metric']]} & {row['conditions']} & "
            f"{int(float(row['original_total']))} & {int(float(row['updated_total']))} & "
            f"{int(float(row['absolute_reduction']))} ({f(row['percent_reduction'], 1)}\\%) & "
            f"{f(row['median_condition_improvement'], 1)} & {row['updated_better']}/{row['unchanged']}/{row['updated_worse']} \\\\"
        )
    return r"""\begin{table}[p]
\centering
\caption{Robust development-only summary of the 24-condition AMP-AD original-versus-updated configuration comparison.}
\label{tab:supp2}
\scriptsize
\setlength{\tabcolsep}{2.8pt}
\renewcommand{\arraystretch}{1.08}
\resizebox{\linewidth}{!}{%
\begin{tabular}{llrrrrrl}
\toprule
Scope & Diagnostic & $n$ & Original & Updated & Reduction (\%) & Median improvement & Better/unchanged/worse \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\par\smallskip
\parbox{0.98\linewidth}{\scriptsize\textit{Note.} The excluded prespecified stress condition is Rush/SVM-L1/Small. Positive improvement denotes a lower updated value. The stress condition accounts for 56/79 (70.9\%) of the aggregate target-deviation reduction and 179/340 (52.6\%) of the all-zero-generation reduction; both diagnostics remain lower after exclusion. Held-out outcomes were not accessed.}
\end{table}
"""


def build_cross_lock() -> str:
    data = rows("CROSS_LOCK_2X2_SUMMARY.csv")
    bank = {
        "original_objective": "Original-objective bank",
        "updated_objective": "Updated-objective bank",
    }
    rule = {
        "original_top_three": "Original top-three",
        "regret_constrained": "Regret-constrained",
    }
    body = []
    for row in data:
        body.append(
            f"{bank[row['candidate_bank']]} & {rule[row['locking_rule']]} & {row['conditions']} & "
            f"{int(float(row['total_target_deviation']))} & {f(row['mean_selected_count'], 2)} & "
            f"{f(row['mean_locking_score'], 5)} & {f(row['mean_selected_regret'], 5)} & "
            f"{f(row['maximum_selected_regret'], 5)} & {row['selected_mask_changes_between_rules']} \\\\"
        )
    return r"""\begin{table}[p]
\centering
\caption{Existing-artifact 2 by 2 candidate-bank and locking-rule comparison for matched AMP-AD development conditions.}
\label{tab:supp3}
\scriptsize
\setlength{\tabcolsep}{2.6pt}
\renewcommand{\arraystretch}{1.08}
\resizebox{\linewidth}{!}{%
\begin{tabular}{llrrrrrrr}
\toprule
Candidate bank & Locking rule & $n$ & Total target deviation & Mean selected $n$ & Mean score & Mean regret & Maximum regret & Mask changes \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}}
\par\smallskip
\parbox{0.98\linewidth}{\scriptsize\textit{Note.} No candidate generation or held-out evaluation was rerun. All 24 original-objective banks and all 24 updated-objective banks were complete after recovery of the 30 Rush run-best feature lists from the authoritative Drive source folder. ``Mask changes'' is the within-bank number of conditions for which the two locking rules selected different masks. The regret-constrained rule improved the configured development-CV score-gap summaries in both bank sets but did not universally improve target fidelity.}
\end{table}
"""


def build_tie_duplicate() -> str:
    return r"""\begin{table}[p]
\centering
\caption{Eligible-pool decision paths and duplicate-mask sensitivity for the 24 updated AMP-AD development-only conditions at absolute $\delta=0.01$.}
\label{tab:supp4}
\scriptsize
\setlength{\tabcolsep}{4.2pt}
\renewcommand{\arraystretch}{1.08}
\textit{A. Eligible-pool and decision-path audit}\par\smallskip
\begin{tabular}{lrr@{\hspace{1.2cm}}lrr}
\toprule
Pool category & Conditions & Percent & Decision stage & Conditions & Percent \\
\midrule
Singleton & 2 & 8.3\% & Singleton direct & 2 & 8.3\% \\
Two candidates & 6 & 25.0\% & Unique Jaccard & 13 & 54.2\% \\
Three or more & 16 & 66.7\% & Higher score & 9 & 37.5\% \\
 & & & Smaller feature count & 0 & 0.0\% \\
 & & & Stable mask hash & 0 & 0.0\% \\
\bottomrule
\end{tabular}

\vspace{0.8em}
\textit{B. Duplicate-retained versus deduplicated sensitivity}\par\smallskip
\begin{tabular}{lrrrl}
\toprule
Candidate bank & Audited conditions & Banks with duplicates & Selected-mask changes & Status \\
\midrule
Original-objective & 24 & 0 & 0 & Complete \\
Updated-objective & 24 & 0 & 0 & Complete after Rush recovery \\
\bottomrule
\end{tabular}
\par\smallskip
\parbox{0.98\linewidth}{\scriptsize\textit{Note.} Exact duplicate masks are retained as multiple voting candidates by the package. No duplicates occurred in the 48 complete banks, so deduplication did not change a selected mask in this empirical sensitivity. The 30 Rush run-best feature lists were recovered from the authoritative Drive source folder; all six current selections matched both the archived summary and the frozen one-time evaluation. Source-run provenance is distinct from input-row order and is used only after scientific feature-set selection when exact duplicates require a provenance representative.}
\end{table}
"""


def main() -> None:
    outputs = {
        "table_40.tex": build_robust_summary(),
        "table_41.tex": build_cross_lock(),
        "table_42.tex": build_tie_duplicate(),
    }
    for name, content in outputs.items():
        (TABLES / name).write_text(content, encoding="utf-8")
    print(f"PASS: wrote {len(outputs)} revision tables")


if __name__ == "__main__":
    main()
