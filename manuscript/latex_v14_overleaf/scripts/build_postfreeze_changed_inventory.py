"""Rebuild the post-freeze changed-file inventory from the current files.

The inventory deliberately excludes itself and V12_CHANGED_FILE_INVENTORY.md to
avoid circular hashes. Existing analysis-path classifications are preserved;
new manuscript integration files are classified as public V12 materials.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


V12 = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[3]
OUTPUT = V12 / "POSTFREEZE_CHANGED_FILE_INVENTORY.csv"

EXPLICIT_V12_FILES = {
    "README.md",
    "main.tex",
    "main.pdf",
    "supplementary_information.tex",
    "supplementary_information.pdf",
    "sections/main_text.tex",
    "sections/supplementary.tex",
    "figures/figure_4.png",
    "figures/figure_4.svg",
    "figures/figure_4_v11_source.svg",
    "figures/figure_1.pdf",
    "figures/figure_1.png",
    "figures/figure_1.svg",
    "figures/figure_1_editable_source_v2.svg",
    "figures/figure_3_panel_label_source.svg",
    "figures/figure_5.pdf",
    "figures/figure_5.png",
    "figures/figure_5.svg",
    "figures/figure_s9.pdf",
    "figures/figure_s9.png",
    "figures/figure_s9.svg",
    "figures/figure_s19_ab.png",
    "figures/figure_s19_cd.png",
    "figures/figure_s21.pdf",
    "figures/figure_s21.png",
    "figures/figure_s21.svg",
    "figures/figure_s22.pdf",
    "figures/figure_s22.png",
    "figures/figure_s22.svg",
    "figures/figure_s23.pdf",
    "figures/figure_s23.png",
    "figures/figure_s23.svg",
    "tables/table_44.tex",
    "tables/table_45.tex",
    "tables/table_46.tex",
    "scripts/build_gridfree_figure4_svg.py",
    "scripts/render_v12_figure4_from_svg.ps1",
    "scripts/figure4_render_wrapper.html",
    "scripts/build_cgga_figure5.py",
    "scripts/validate_cgga_figure5_provenance.py",
    "scripts/build_postfreeze_results.py",
    "scripts/build_cgga_s9_clean.py",
    "scripts/build_postfreeze_changed_inventory.py",
    "scripts/normalize_main_panel_labels.py",
    "scripts/validate_main_panel_labels.py",
    "scripts/figure_1_render_wrapper.html",
    "scripts/render_v12_figure1_from_svg.ps1",
    "scripts/prepare_170mm_figure_assets.py",
    "scripts/build_v12_submission_archive.ps1",
    "revision_outputs/FIGURE4_GRID_REMOVAL_PROVENANCE.json",
    "POSTFREEZE_ANALYSIS_FIGURE_MANIFEST.json",
    "POSTFREEZE_ANALYSIS_REPORT.md",
    "POSTFREEZE_VALIDATION_REPORT.md",
    "MAIN_SUPPLEMENTARY_FIGURE_MAP.md",
    "FIGURE_SOURCE_DATA_MANIFEST.csv",
    "FIGURE_180MM_STYLE_SOURCE_MANIFEST.md",
    "FIGURE_GRID_REMOVAL_REPORT.md",
    "FINAL_QA_REPORT.md",
    "MAIN_FIGURE_PANEL_LABEL_AUDIT.md",
    "FIGURE_170MM_STYLE_SOURCE_MANIFEST.csv",
    "FIGURE_170MM_STYLE_SOURCE_MANIFEST.md",
    "FIGURE_180MM_STYLE_SOURCE_MANIFEST.md",
    "FIGURE_GRIDFREE_REPRODUCIBILITY_MANIFEST.json",
    "SUPPLEMENTARY_GRAPHIC_CLEANUP_REPORT.md",
    "V12_CHANGELOG.md",
    "V12_DISPLAY_CITATION_AUDIT.md",
    "V12_PROVENANCE_AND_SCOPE.md",
    "V12_VALIDATION_REPORT.md",
    "V12_WORD_AND_DISPLAY_COUNTS.md",
}

PUBLIC_DATA_DIRS = (
    "supplementary_data/postfreeze_ampad",
    "supplementary_data/cgga_coherent_benchmark",
    "supplementary_data/cgga_nested_relock",
    "supplementary_data/cgga_tuned_rf_s9",
)

EXCLUDED_RELATIVE = {
    "manuscript/latex_v12_overleaf/POSTFREEZE_CHANGED_FILE_INVENTORY.csv",
    "manuscript/latex_v12_overleaf/V12_CHANGED_FILE_INVENTORY.md",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    previous: dict[str, tuple[str, str]] = {}
    if OUTPUT.exists():
        with OUTPUT.open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                previous[row["relative_path"]] = (row["category"], row["scope"])

    paths = {key for key in previous if key not in EXCLUDED_RELATIVE}
    prefix = "manuscript/latex_v12_overleaf/"
    paths.update(prefix + value for value in EXPLICIT_V12_FILES)
    for directory in PUBLIC_DATA_DIRS:
        for path in (V12 / directory).rglob("*"):
            if path.is_file():
                paths.add(path.relative_to(ROOT).as_posix())

    rows = []
    for relative in sorted(paths, key=str.casefold):
        path = ROOT / Path(relative)
        if not path.is_file():
            continue
        category, scope = previous.get(
            relative, ("V12 integration", "manuscript/public")
        )
        rows.append(
            {
                "relative_path": relative,
                "category": category,
                "scope": scope,
                "bytes": path.stat().st_size,
                "sha256": digest(path),
            }
        )

    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("relative_path", "category", "scope", "bytes", "sha256"),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"rows={len(rows)}")
    print(f"sha256={digest(OUTPUT)}")


if __name__ == "__main__":
    main()
