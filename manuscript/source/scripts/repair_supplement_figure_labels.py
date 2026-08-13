"""Repair numeric figure labels after the one-time first-citation reorder."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "sections" / "supplementary.tex"


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    start = text.index("\\section{Supplementary Figures}")
    end = text.index("\\section{Supplementary Tables}")
    before, figures, after = text[:start], text[start:end], text[end:]

    counter = 0

    def replace_label(match: re.Match[str]) -> str:
        nonlocal counter
        counter += 1
        return f"\\label{{fig:supp{counter}}}"

    figures = re.sub(r"\\label\{fig:supp\d+\}", replace_label, figures)
    if counter != 27:
        raise RuntimeError(f"Expected 27 labelled figure groups, repaired {counter}")

    # Three Supplementary-Methods references are semantic callouts rather than
    # figure-block labels.  Reset them to their new first-citation numbers.
    before = re.sub(
        r"\\Crefrange\{fig:supp\d+\}\{fig:supp\d+\}",
        r"\\Crefrange{fig:supp20}{fig:supp21}",
        before,
        count=1,
    )
    before = re.sub(
        r"The complete candidate audit in \\cref\{fig:supp\d+\}",
        r"The complete candidate audit in \\cref{fig:supp16}",
        before,
    )
    before = re.sub(
        r"Candidate agreement and participant-partition sensitivity are expanded in \\cref\{fig:supp\d+\}",
        r"Candidate agreement and participant-partition sensitivity are expanded in \\cref{fig:supp17}",
        before,
    )
    before = re.sub(
        r"Repeated-OOF metrics and the complete comparator audit are shown in \\cref\{fig:supp\d+\}",
        r"Repeated-OOF metrics and the complete comparator audit are shown in \\cref{fig:supp18}",
        before,
    )

    repaired = before + figures + after
    labels = [int(value) for value in re.findall(r"\\label\{fig:supp(\d+)\}", repaired)]
    if labels != list(range(1, 28)):
        raise RuntimeError(f"Nonsequential repaired labels: {labels}")
    PATH.write_text(repaired, encoding="utf-8")
    print("PASS: Supplementary figure labels S1--S27 repaired")


if __name__ == "__main__":
    main()
