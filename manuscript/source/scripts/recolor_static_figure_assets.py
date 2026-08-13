"""Apply the submission palette to frozen raster/vector figure assets.

This is a presentation-only transform.  It copies each original asset into
``supplementary_data/figure_palette_sources`` on first use, always rebuilds
from that copy, and changes only pixels/hex tokens that match declared legacy
colors.  Geometry, text, axes, and plotted values are untouched.  Figure 1 is
intentionally absent from every target list.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

from figure_palette import (
    BRANCH_COLORS,
    CURRENT,
    OCHRE,
    SAGE,
    SECONDARY,
    STRESS,
    TERRACOTTA,
)


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
SOURCES = ROOT / "supplementary_data" / "figure_palette_sources"

BRANCH_RASTERS = {
    "figure_3.png",
    "figure_s1.png",
    "figure_s2.png",
    "figure_s7.png",
    "figure_s8.png",
    "figure_s10.png",
    "figure_s11.png",
    "figure_s17.png",
    "figure_s19.png",
}

GENERIC_RASTERS = {
    "figure_4.png",
    "figure_s3.png",
    "figure_s4.png",
    "figure_s5.png",
    "figure_s6.png",
    "figure_s12.png",
    "figure_s13.png",
    "figure_s14.png",
    "figure_s15.png",
}

STATIC_VECTORS = {
    "figure_3_panel_label_source.svg",
    "figure_4.svg",
    "figure_4_source.svg",
}


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


BRANCH_MAP = {
    # Historical SVM-L1 greens.
    "#239B71": BRANCH_COLORS["svm_l1"],
    "#2A9D6F": BRANCH_COLORS["svm_l1"],
    "#009E73": BRANCH_COLORS["svm_l1"],
    "#55B48B": BRANCH_COLORS["svm_l1"],
    "#49A97D": BRANCH_COLORS["svm_l1"],
    "#359F6F": BRANCH_COLORS["svm_l1"],
    "#2C9B68": BRANCH_COLORS["svm_l1"],
    "#349E6E": BRANCH_COLORS["svm_l1"],
    "#5FB592": BRANCH_COLORS["svm_l1"],
    "#8BC8AC": "#7EB2BD",
    # Historical XGBoost oranges.
    "#E69500": BRANCH_COLORS["xgboost"],
    "#E49A17": BRANCH_COLORS["xgboost"],
    "#E69F00": BRANCH_COLORS["xgboost"],
    "#F0AD35": BRANCH_COLORS["xgboost"],
    "#E9AD2E": BRANCH_COLORS["xgboost"],
    "#E79700": BRANCH_COLORS["xgboost"],
    "#E5A00D": BRANCH_COLORS["xgboost"],
    "#E6A418": BRANCH_COLORS["xgboost"],
    "#ECB03F": BRANCH_COLORS["xgboost"],
    "#F1CB7A": "#DDBB74",
    # Historical Boruta-RF reds.
    "#D95C4A": BRANCH_COLORS["boruta_rf"],
    "#D45A4C": BRANCH_COLORS["boruta_rf"],
    "#D55E00": BRANCH_COLORS["boruta_rf"],
    "#E97868": BRANCH_COLORS["boruta_rf"],
    "#DC6E61": BRANCH_COLORS["boruta_rf"],
    "#D95C4B": BRANCH_COLORS["boruta_rf"],
    "#D85E50": BRANCH_COLORS["boruta_rf"],
    "#D65748": BRANCH_COLORS["boruta_rf"],
    "#E28477": BRANCH_COLORS["boruta_rf"],
    "#E9A39A": "#B88CA9",
}

GENERIC_MAP = {
    "#0072B2": CURRENT,
    "#1F77B4": CURRENT,
    "#2F6FB0": CURRENT,
    "#2B6CB0": CURRENT,
    "#56B4E9": "#7697AA",
    "#009E73": SAGE,
    "#2CA02C": SAGE,
    "#E69F00": OCHRE,
    "#FF7F0E": OCHRE,
    "#D55E00": STRESS,
    "#D62728": TERRACOTTA,
    "#C05621": TERRACOTTA,
    "#7B3294": SECONDARY,
    "#6A51A3": SECONDARY,
    "#9467BD": SECONDARY,
    "#CC79A7": "#8B5E83",
    "#E377C2": "#9C718F",
    "#8C564B": "#8A6B63",
    "#17BECF": "#5F8E98",
    "#BCBD22": "#82906A",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_for(name: str) -> Path:
    SOURCES.mkdir(parents=True, exist_ok=True)
    source = SOURCES / name
    target = FIGURES / name
    if not source.exists():
        shutil.copy2(target, source)
    return source


_LUT_CACHE: dict[tuple[tuple[str, str], ...], np.ndarray] = {}


def color_lut(mapping: dict[str, str]) -> np.ndarray:
    """Return a 24-bit RGB lookup table including white-background antialias blends."""
    key = tuple(mapping.items())
    if key in _LUT_CACHE:
        return _LUT_CACHE[key]
    lut = np.arange(1 << 24, dtype=np.uint32)
    for old_hex, new_hex in mapping.items():
        old = np.asarray(rgb(old_hex), dtype=np.float64)
        new = np.asarray(rgb(new_hex), dtype=np.float64)
        for alpha_byte in range(20, 256):
            alpha = alpha_byte / 255.0
            old_blend = np.rint(255.0 - alpha * (255.0 - old)).astype(np.uint32)
            new_blend = np.rint(255.0 - alpha * (255.0 - new)).astype(np.uint32)
            old_code = int((old_blend[0] << 16) | (old_blend[1] << 8) | old_blend[2])
            new_code = int((new_blend[0] << 16) | (new_blend[1] << 8) | new_blend[2])
            lut[old_code] = new_code
    _LUT_CACHE[key] = lut
    return lut


def recolor_raster(name: str, mapping: dict[str, str]) -> dict[str, object]:
    source = source_for(name)
    target = FIGURES / name
    image = Image.open(source).convert("RGBA")
    array = np.asarray(image).copy()
    flat = array[:, :, :3].reshape(-1, 3).astype(np.uint32)
    packed = (flat[:, 0] << 16) | (flat[:, 1] << 8) | flat[:, 2]
    mapped = color_lut(mapping)[packed]
    changed = mapped != packed
    flat[:, 0] = (mapped >> 16) & 255
    flat[:, 1] = (mapped >> 8) & 255
    flat[:, 2] = mapped & 255
    array[:, :, :3] = flat.astype(np.uint8).reshape(array[:, :, :3].shape)
    Image.fromarray(array, mode="RGBA").save(target, dpi=image.info.get("dpi", (600, 600)))
    return {
        "asset": name,
        "source_sha256": sha256(source),
        "output_sha256": sha256(target),
        "changed_pixels": int(changed.sum()),
        "total_pixels": int(changed.size),
    }


def recolor_vector(name: str, mapping: dict[str, str]) -> dict[str, object]:
    source = source_for(name)
    target = FIGURES / name
    text = source.read_text(encoding="utf-8")
    replacements = 0
    for old_hex, new_hex in mapping.items():
        for token in (old_hex.lower(), old_hex.upper()):
            count = text.count(token)
            text = text.replace(token, new_hex.lower())
            replacements += count
    target.write_text(text, encoding="utf-8")
    return {
        "asset": name,
        "source_sha256": sha256(source),
        "output_sha256": sha256(target),
        "replacements": replacements,
    }


def main() -> None:
    records: list[dict[str, object]] = []
    branch_then_generic = {**GENERIC_MAP, **BRANCH_MAP}
    for name in sorted(BRANCH_RASTERS):
        records.append(recolor_raster(name, branch_then_generic))
    for name in sorted(GENERIC_RASTERS):
        records.append(recolor_raster(name, GENERIC_MAP))
    for name in sorted(STATIC_VECTORS):
        records.append(recolor_vector(name, GENERIC_MAP))

    manifest = {
        "figure_1_excluded": True,
        "scientific_values_changed": False,
        "transform": "declared legacy-color substitution with antialias preservation",
        "branch_colors": BRANCH_COLORS,
        "assets": records,
    }
    manifest_path = SOURCES / "palette_transform_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "assets": len(records), "manifest": str(manifest_path)}, sort_keys=True))


if __name__ == "__main__":
    main()
