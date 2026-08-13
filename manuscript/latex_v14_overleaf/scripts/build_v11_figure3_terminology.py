from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

from PIL import Image


HERE = Path(__file__).resolve().parent
V11 = HERE.parent
ROOT = V11.parents[1]
FIGURES = V11 / "figures"
SOURCE = (
    ROOT
    / "outputs"
    / "AMPAD_Figure3_publication_assets_20260731"
    / "figures"
    / "main"
    / "Figure_3_AMPAD_budget_calibration.svg"
)
NODE = Path(
    r"C:\Users\junse\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
)
RENDERER = ROOT / "analysis" / "render_svg_assets.cjs"

sys.path.insert(0, str(ROOT))
from analysis.rebuild_v10_gridfree_figures import erase_redundant_text, remove_grid_strokes  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    tree = ET.parse(SOURCE)
    root = tree.getroot()
    changes: list[dict[str, str]] = []
    for element in root.iter():
        if not element.tag.endswith("text") or element.text is None:
            continue
        old = element.text
        x = float(element.attrib.get("x", "0").split()[0])
        if old == "SVM-L1 / Rush / Low":
            element.text = "SVM-L1 / Rush / Small"
        elif old.startswith("MAE |locked - target|:"):
            element.text = old.replace("Low 15.5", "Small 15.5")
        elif old == "Low" and x > 250:
            element.text = "Small"
        if element.text != old:
            changes.append({"old": old, "new": element.text})

    if len(changes) != 4:
        raise RuntimeError(f"Expected four cap-label changes; observed {changes}")

    svg = FIGURES / "figure_3_v11_source.svg"
    pregrid = FIGURES / "figure_3_v11_pregrid.png"
    tree.write(svg, encoding="utf-8", xml_declaration=True)
    render_manifest = V11 / "revision_outputs" / "V11_FIGURE3_RENDER.json"
    render_manifest.write_text(
        json.dumps(
            [
                {
                    "svg": str(svg.resolve()),
                    "png": str(pregrid.resolve()),
                    "width_mm": 170,
                    "height_mm": 150,
                    "dpi": 600,
                }
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    subprocess.run([str(NODE), str(RENDERER), str(render_manifest)], check=True, cwd=ROOT)

    image = Image.open(pregrid).convert("RGB")
    image, grid_audit = remove_grid_strokes(image)
    masks = erase_redundant_text(image, "figure_3.png")
    output = FIGURES / "figure_3.png"
    image.save(output, dpi=(600, 600), optimize=True)

    provenance = {
        "operation": "terminology-only SVG relabel plus existing deterministic grid-free transform",
        "scientific_values_changed": False,
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(SOURCE),
        "changes": changes,
        "grid_audit": grid_audit,
        "annotation_masks": masks,
        "output": str(output.relative_to(V11)).replace("\\", "/"),
        "output_sha256": sha256(output),
    }
    (V11 / "revision_outputs" / "V11_FIGURE3_TERMINOLOGY_PROVENANCE.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"status": "PASS", "changes": len(changes), "sha256": sha256(output)}))


if __name__ == "__main__":
    main()
