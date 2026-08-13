"""Normalize panel-label sizes within each V12 main figure.

Only Figure 1 required a mechanical source edit: its supplied SVG encoded a)
at 37.795 px and b) at 37.5 px.  Both are normalized to 37.5 px without
changing panel geometry or scientific content.  The editable provenance copy
is kept byte-consistent with the publication SVG.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    ROOT / "figures" / "figure_1.svg",
    ROOT / "figures" / "figure_1_editable_source_v2.svg",
)
OLD = "font-weight:700;font-size:37.795px;fill:#25313a;\">a)</text>"
NEW = "font-weight:700;font-size:37.5px;fill:#25313a;\">a)</text>"


def main() -> None:
    for path in TARGETS:
        source = path.read_text(encoding="utf-8")
        count = source.count(OLD)
        if count == 1:
            path.write_text(source.replace(OLD, NEW), encoding="utf-8", newline="")
        elif source.count(NEW) != 1:
            raise RuntimeError(f"Unexpected Figure 1 panel-label encoding in {path}")
        print(f"{path.name}: a)=37.5 px; b)=37.5 px")


if __name__ == "__main__":
    main()
