"""Create the approved AMP-AD Figure 4 without background plot grids.

The preserved editable SVG remains authoritative. This deterministic cleanup
removes only Matplotlib grid-line groups and the empty annotation box left
after the redundant in-panel sentence was removed. Scientific marks, axes,
labels, values, and legends are unchanged.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "figures" / "figure_4_source.svg"
OUTPUT = ROOT / "figures" / "figure_4.svg"
PROVENANCE = ROOT / "revision_outputs" / "FIGURE4_GRID_REMOVAL_PROVENANCE.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source_text = SOURCE.read_text(encoding="utf-8")
    grid_pattern = re.compile(
        r'\s*<g id="line2d_\d+">\s*'
        r'<path[^>]+stroke: #(?:d9d9d9|e0e0e0)[^>]*/>\s*'
        r'</g>',
        flags=re.DOTALL,
    )
    cleaned, grid_count = grid_pattern.subn("", source_text)
    empty_box_pattern = re.compile(
        r'\s*<g id="text_43">\s*<g id="patch_8">.*?</g>\s*</g>',
        flags=re.DOTALL,
    )
    cleaned, empty_box_count = empty_box_pattern.subn("", cleaned)

    if grid_count != 63:
        raise AssertionError(f"Expected 63 grid-line groups, removed {grid_count}")
    if empty_box_count != 1:
        raise AssertionError(f"Expected one empty annotation box, removed {empty_box_count}")
    if "stroke: #d9d9d9" in cleaned or "stroke: #e0e0e0" in cleaned:
        raise AssertionError("A targeted grid stroke remains")

    OUTPUT.write_text(cleaned, encoding="utf-8")
    provenance = {
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(SOURCE),
        "output": str(OUTPUT.relative_to(ROOT)).replace("\\", "/"),
        "output_sha256": sha256(OUTPUT),
        "removed_grid_line_groups": grid_count,
        "removed_empty_annotation_boxes": empty_box_count,
        "scientific_values_changed": False,
    }
    PROVENANCE.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(provenance, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
