#!/usr/bin/env python3
"""Validate display numbering and main-text citation coverage."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_TEXT = ROOT / "sections" / "main_text.tex"
SUPPLEMENT_AUX = ROOT / "supplementary_information.aux"
EXPECTED = list(range(1, 29))


def cited_numbers(kind: str, text: str) -> list[int]:
    pattern = re.compile(
        rf"Supplementary {kind}(?:s)?(?:\\)?\.?(?:~)?S(\d+)(?:--S?(\d+))?"
    )
    numbers: list[int] = []
    for match in pattern.finditer(text):
        start = int(match.group(1))
        stop = int(match.group(2) or start)
        numbers.extend(range(start, stop + 1))
    return numbers


def auxiliary_numbers(prefix: str, text: str) -> list[int]:
    pattern = re.compile(rf"\\newlabel\{{{prefix}:supp(\d+)\}}\{{\{{S(\d+)")
    return [int(left) for left, right in pattern.findall(text) if left == right]


def main() -> None:
    main_text = MAIN_TEXT.read_text(encoding="utf-8")
    auxiliary = SUPPLEMENT_AUX.read_text(encoding="utf-8")

    for kind in ("Fig", "Table"):
        observed = sorted(set(cited_numbers(kind, main_text)))
        if observed != EXPECTED:
            missing = sorted(set(EXPECTED) - set(observed))
            raise SystemExit(f"Missing Supplementary {kind} citations: {missing}")
        print(f"PASS: Supplementary {kind}s S1--S28 are cited.")

    for prefix, label in (("fig", "figures"), ("tab", "tables")):
        observed = auxiliary_numbers(prefix, auxiliary)
        if observed != EXPECTED:
            raise SystemExit(f"Nonsequential Supplementary {label}: {observed}")
        print(f"PASS: Supplementary {label} are numbered S1--S28 sequentially.")


if __name__ == "__main__":
    main()
