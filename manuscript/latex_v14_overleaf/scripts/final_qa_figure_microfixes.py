"""Apply submission-QA-only figure text corrections without recomputing results."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIGURES = ROOT / "figures"
OUT = ROOT / "revision_outputs"
S9_SOURCE = FIGURES / "figure_s9_prefinalqa_source.png"
S9_DESTINATION = FIGURES / "figure_s9.png"
S16_SOURCE = FIGURES / "figure_s16_prefinalqa_source.pdf"
S16_DESTINATION = FIGURES / "figure_s16.pdf"
EXPECTED_S9_SOURCE_SHA256 = (
    "6d1e869e28c6a066f7c7216d647819b33176e7b0eea44488b622f17203475d3d"
)
EXPECTED_S16_SOURCE_SHA256 = (
    "398ad0397ac6ccb6fe722d0fc06a9ad87b3dc16ae2afe6dc33947b5a7ff354e9"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fix_s9_label() -> dict[str, object]:
    if sha256(S9_SOURCE) != EXPECTED_S9_SOURCE_SHA256:
        raise RuntimeError("Unexpected Supplementary Figure S9 source hash")
    with Image.open(S9_SOURCE) as source:
        image = source.convert("RGB")
        dpi = source.info.get("dpi", (600, 600))
    if image.size != (4016, 3425):
        raise RuntimeError(f"Unexpected Supplementary Figure S9 dimensions: {image.size}")

    draw = ImageDraw.Draw(image)
    correction_box = (3350, 1340, 3910, 1495)
    draw.rectangle(correction_box, fill="white")
    font_path = Path("C:/WINDOWS/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 43)
    draw.text(
        (3630, 1420),
        "Balanced accuracy",
        fill="#263746",
        font=font,
        anchor="mm",
    )
    image.save(S9_DESTINATION, dpi=dpi, optimize=True)
    return {
        "source": str(S9_SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(S9_SOURCE),
        "output": str(S9_DESTINATION.relative_to(ROOT)).replace("\\", "/"),
        "output_sha256": sha256(S9_DESTINATION),
        "operation": "Corrected 'Balancedaccuracy' to 'Balanced accuracy' only",
        "scientific_recomputation": False,
    }


def fix_s16_annotation() -> dict[str, object]:
    if sha256(S16_SOURCE) != EXPECTED_S16_SOURCE_SHA256:
        raise RuntimeError("Unexpected Supplementary Figure S16 source hash")
    renderer = HERE / "render_v12_figure_s16_from_svg.ps1"
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(renderer),
        ],
        check=True,
    )
    builder_path = HERE / "build_v11_revision_figures.py"
    return {
        "builder": str(builder_path.relative_to(ROOT)).replace("\\", "/"),
        "builder_sha256": sha256(builder_path),
        "renderer": str(renderer.relative_to(ROOT)).replace("\\", "/"),
        "renderer_sha256": sha256(renderer),
        "source": str(S16_SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(S16_SOURCE),
        "outputs": {
            "pdf": sha256(S16_DESTINATION),
            "png": sha256(FIGURES / "figure_s16.png"),
            "svg": sha256(FIGURES / "figure_s16.svg"),
        },
        "operation": "Removed caption-duplicated singleton-pool sentence only",
        "scientific_recomputation": False,
    }


def main() -> None:
    record = {
        "scope": "final pre-submission figure text micro-fixes",
        "scientific_recomputation": False,
        "figure_s9": fix_s9_label(),
        "figure_s16": fix_s16_annotation(),
    }
    output = OUT / "FINAL_QA_FIGURE_MICROFIX_HASHES.json"
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
