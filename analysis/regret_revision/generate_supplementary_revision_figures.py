"""Render the revision-only audits as Supplementary Figures S15-S17.

This wrapper deliberately leaves the restored V7 main Figures 1-5 untouched.
It reuses the tested plotting functions and redirects only Figures 2-4 from
the methodological-revision plotter to new supplementary filenames.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from analysis.regret_revision import generate_revision_figures as revision


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "supplementary_figures"
LATEX = ROOT / "manuscript" / "figures"
NUMBER_MAP = {2: 15, 3: 16, 4: 17}


def finish_supplementary(fig, number: int) -> None:
    supplementary_number = NUMBER_MAP[number]
    fig.subplots_adjust(
        left=0.08,
        right=0.985,
        top=0.94,
        bottom=0.12,
        wspace=0.34,
        hspace=0.42,
    )
    OUT.mkdir(parents=True, exist_ok=True)
    LATEX.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"figure_s{supplementary_number}.png", dpi=320)
    fig.savefig(OUT / f"figure_s{supplementary_number}.svg")
    fig.savefig(LATEX / f"figure_s{supplementary_number}.png", dpi=320)
    plt.close(fig)


def main() -> None:
    compression = pd.read_csv(ROOT / "compression_regret_summary.csv")
    sensitivity = pd.read_csv(ROOT / "locking_rule_sensitivity.csv")
    penalty = pd.read_csv(ROOT / "penalty_flattening_audit.csv")
    original_finish = revision.finish
    revision.finish = finish_supplementary
    try:
        revision.figure2(compression)
        revision.figure3(sensitivity)
        revision.figure4(penalty)
    finally:
        revision.finish = original_finish
    print(f"Generated Supplementary Figures S15-S17 in {LATEX}")


if __name__ == "__main__":
    main()
