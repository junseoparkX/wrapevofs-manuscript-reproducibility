from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FIGURES = ROOT / "figures"
OUT = ROOT / "revision_outputs" / "PRESENTATION_ASSET_HASHES.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tight_white_crop(image: Image.Image, padding: int = 24) -> Image.Image:
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, "white")
    difference = ImageChops.difference(rgb, background).convert("L")
    difference = difference.point(lambda value: 255 if value > 8 else 0)
    box = difference.getbbox()
    if box is None:
        raise ValueError("Cannot crop an all-white image")
    left, top, right, bottom = box
    return rgb.crop(
        (
            max(0, left - padding),
            max(0, top - padding),
            min(rgb.width, right + padding),
            min(rgb.height, bottom + padding),
        )
    )


def save(image: Image.Image, name: str) -> dict[str, object]:
    path = FIGURES / name
    image.save(path, format="PNG", dpi=(600, 600), optimize=True)
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "pixels": list(image.size)}


def main() -> None:
    s8_source = FIGURES / "figure_s8.png"
    s19_source = FIGURES / "figure_s19.png"

    s8 = Image.open(s8_source).convert("RGB")
    s8_split = 2140
    if not (0 < s8_split < s8.height):
        raise ValueError("Invalid S8 split")
    s8_a = tight_white_crop(s8.crop((0, 0, s8.width, s8_split)))
    s8_bc = tight_white_crop(s8.crop((0, s8_split, s8.width, s8.height)))
    s19 = Image.open(s19_source).convert("RGB")
    # Split only in the blank band between panels b and c.  The former 2530-px
    # boundary cut panel b above its condition labels and carried those labels
    # onto the continued page.
    split = 2800
    if not (0 < split < s19.height):
        raise ValueError("Invalid S19 split")
    s19_ab = tight_white_crop(s19.crop((0, 0, s19.width, split)))
    s19_cd = tight_white_crop(s19.crop((0, split, s19.width, s19.height)))

    manifest = {
        "operation": "deterministic white-margin crop and page split only",
        "scientific_values_changed": False,
        "source": {
            "figure_s8.png": digest(s8_source),
            "figure_s19.png": digest(s19_source),
        },
        "outputs": {
            "figure_s8_a.png": save(s8_a, "figure_s8_a.png"),
            "figure_s8_bc.png": save(s8_bc, "figure_s8_bc.png"),
            "figure_s19_ab.png": save(s19_ab, "figure_s19_ab.png"),
            "figure_s19_cd.png": save(s19_cd, "figure_s19_cd.png"),
        },
    }
    OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["outputs"], sort_keys=True))


if __name__ == "__main__":
    main()
