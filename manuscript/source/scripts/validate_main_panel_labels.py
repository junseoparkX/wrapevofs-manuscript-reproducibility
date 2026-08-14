"""Validate equal bold panel-label sizes within each main figure."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "Figure 1": (ROOT / "figures" / "figure_1.svg", "ab"),
    "Figure 2": (ROOT / "figures" / "figure_2.svg", "abcd"),
    "Figure 3": (ROOT / "figures" / "figure_3_strengthened.svg", "abcd"),
    "Figure 4": (ROOT / "figures" / "figure_4_strengthened.svg", "abcd"),
    "Figure 5": (ROOT / "figures" / "figure_5_strengthened.svg", "ab"),
}


def label_style(source: str, label: str) -> tuple[float, str]:
    match = re.search(
        rf'<text[^>]*>\s*{re.escape(label)}\)\s*</text>', source
    )
    if match is None:
        raise AssertionError(f"Missing panel label {label})")
    tag = match.group(0)
    size = re.search(r"font-size:\s*([0-9.]+)", tag)
    weight = re.search(r"font-weight:\s*([^;\"']+)", tag)
    if size is None or weight is None:
        raise AssertionError(f"Incomplete style for panel label {label})")
    return float(size.group(1)), weight.group(1).strip()


def main() -> None:
    for figure, (path, labels) in SOURCES.items():
        source = path.read_text(encoding="utf-8")
        styles = {f"{label})": label_style(source, label) for label in labels}
        sizes = {value[0] for value in styles.values()}
        weights = {value[1] for value in styles.values()}
        if len(sizes) != 1:
            raise AssertionError(f"{figure} panel-label sizes differ: {styles}")
        if not weights <= {"700", "bold"}:
            raise AssertionError(f"{figure} panel labels are not uniformly bold: {styles}")
        print(f"{figure}: PASS; labels={','.join(styles)}; size={sizes.pop():g}")


if __name__ == "__main__":
    main()
