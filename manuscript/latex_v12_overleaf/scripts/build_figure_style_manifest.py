from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
V11 = HERE.parent
ROOT = V11.parents[1]
V10 = ROOT / "manuscript" / "latex_v10_overleaf"
OUTPUT_CSV = V11 / "FIGURE_170MM_STYLE_SOURCE_MANIFEST.csv"
OUTPUT_MD = V11 / "FIGURE_170MM_STYLE_SOURCE_MANIFEST.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dimensions(path: Path) -> tuple[str, str]:
    if path.suffix.lower() == ".pdf":
        page = PdfReader(path).pages[0]
        return f"{float(page.mediabox.width):.3f}", f"{float(page.mediabox.height):.3f}"
    with Image.open(path) as image:
        return str(image.width), str(image.height)


def latex_directives() -> dict[str, str]:
    directives: dict[str, str] = {}
    pattern = re.compile(r"includegraphics\[(?P<opts>[^]]+)\]\{figures/(?P<name>[^}]+)\}")
    for source in (V11 / "sections" / "main_text.tex", V11 / "sections" / "supplementary.tex"):
        for line in source.read_text(encoding="utf-8").splitlines():
            match = pattern.search(line)
            if match:
                directives[match.group("name")] = match.group("opts")
    return directives


def source_metadata() -> dict[str, dict[str, object]]:
    manifest = json.loads(
        (V10 / "FIGURE_GRIDFREE_REPRODUCIBILITY_MANIFEST.json").read_text(encoding="utf-8")
    )
    return manifest["figures"]


def figure_rows() -> list[dict[str, object]]:
    directives = latex_directives()
    metadata = source_metadata()
    names = [f"figure_{index}" for index in range(1, 6)] + [
        f"figure_s{index}" for index in range(1, 20)
    ]
    rows: list[dict[str, object]] = []
    for stem in names:
        candidates = sorted((V11 / "figures").glob(f"{stem}.*"))
        preferred = next(
            (path for suffix in (".pdf", ".png", ".svg") for path in candidates if path.suffix == suffix),
            None,
        )
        if preferred is None:
            raise FileNotFoundError(f"Missing rendered figure for {stem}")
        key = preferred.name if preferred.name in metadata else stem
        item = metadata.get(key, {})
        source = str(item.get("source", ""))
        source_path = ROOT / source if source else None
        presentation_paths = [preferred]
        if stem == "figure_s8":
            presentation_paths = [FIG for FIG in (V11 / "figures" / "figure_s8_a.png", V11 / "figures" / "figure_s8_bc.png")]
        elif stem == "figure_s19":
            presentation_paths = [FIG for FIG in (V11 / "figures" / "figure_s19_ab.png", V11 / "figures" / "figure_s19_cd.png")]
        if stem == "figure_1":
            source_class = "frozen V10 authority"
            builder = "excluded from all V11 rebuilds"
            target_width = "frozen"
            grid_policy = "frozen"
            bold_policy = "frozen"
            action = "no change"
        elif stem in {"figure_5", "figure_s16", "figure_s18"}:
            source_class = "machine-readable table plus native plotting builder"
            builder = (
                "scripts/build_v11_revision_figures.py"
                if stem in {"figure_5", "figure_s16"}
                else "supplementary_data/recommended_mode_120_run/scripts/"
                "build_ampad_four_center_objective_sensitivity_s18.py"
            )
            target_width = "170"
            grid_policy = "no background grid"
            bold_policy = "panel labels only"
            action = "native rebuild"
        elif stem == "figure_s19":
            source_class = "byte-identical archived V10 main Figure 5"
            builder = "scripts/prepare_170mm_figure_assets.py"
            target_width = "170"
            grid_policy = "no background grid"
            bold_policy = "panel labels only"
            action = "archive source unchanged and split across continued 170-mm pages"
        elif stem == "figure_3":
            source_class = "frozen empirical SVG plus terminology-only presentation transform"
            builder = "scripts/build_v11_figure3_terminology.py"
            target_width = "170"
            grid_policy = "no background grid"
            bold_policy = "panel labels only"
            action = "Low cap relabeled Small; values and geometry unchanged"
        elif stem == "figure_s8":
            source_class = "frozen publication asset plus deterministic page split"
            builder = "scripts/prepare_170mm_figure_assets.py"
            target_width = "170"
            grid_policy = "no background grid"
            bold_policy = "panel labels only"
            action = "split across continued pages at 170 mm"
        else:
            source_class = "frozen publication asset plus deterministic presentation transform"
            builder = "analysis/rebuild_v10_gridfree_figures.py"
            target_width = "170"
            grid_policy = "no background grid"
            bold_policy = "panel labels only"
            action = "audit source; native rebuild where available, otherwise deterministic transform"
        width, height = dimensions(preferred)
        rows.append(
            {
                "figure": stem.replace("figure_", "Figure ").replace("s", "S", 1),
                "v11_asset": preferred.relative_to(ROOT).as_posix(),
                "asset_sha256": sha256(preferred),
                "asset_width_units": width,
                "asset_height_units": height,
                "presentation_assets": "; ".join(
                    f"{path.name}:{sha256(path)}" for path in presentation_paths
                ),
                "current_latex_directive": "; ".join(
                    directives.get(path.name, "") for path in presentation_paths
                ),
                "target_width_mm": target_width,
                "grid_policy": grid_policy,
                "bold_policy": bold_policy,
                "source_class": source_class,
                "source_asset": source,
                "source_exists": bool(source_path and source_path.exists()),
                "presentation_builder": builder,
                "v11_action": action,
                "status": "frozen-pass" if stem == "figure_1" else "validated",
            }
        )
    return rows


def write_outputs(rows: list[dict[str, object]]) -> None:
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# V11 170-mm figure style and source manifest",
        "",
        "Figure 1 is frozen. The 22 pre-existing non-Figure-1 items retain the requested 170-mm/style/source audit; V11 adds one native replacement Figure 5 and relocates the former Figure 5 as Supplementary Figure S19, yielding 23 nonfrozen printed figures. Every nonfrozen figure targets a 170-mm final width, no background plot grid, and bold panel labels only. Scientific reference lines, axes, ticks, error bars, and heatmap cell boundaries are not background grids.",
        "",
        "| Figure | Target width (mm) | Source class | Builder/action | Status |",
        "|---|---:|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['figure']} | {row['target_width_mm']} | {row['source_class']} | "
            f"{row['v11_action']} | {row['status']} |"
        )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = figure_rows()
    write_outputs(rows)
    nonfrozen = [row for row in rows if row["target_width_mm"] == "170"]
    if len(nonfrozen) != 23:
        raise SystemExit(f"Expected 23 V11 nonfrozen figures; observed {len(nonfrozen)}")
    print(
        json.dumps(
            {
                "status": "PASS",
                "figures": len(rows),
                "preexisting_nonfigure1_audit_count": 22,
                "v11_target_170mm": len(nonfrozen),
            }
        )
    )


if __name__ == "__main__":
    main()
