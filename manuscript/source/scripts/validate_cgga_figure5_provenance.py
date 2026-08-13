"""Validate the frozen aggregate sources and rendered outputs for Figure 5."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "supplementary_data" / "cgga_figure5" / "figure5_manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_entries(entries: list[dict[str, str]], category: str) -> None:
    for entry in entries:
        path = ROOT / entry["path"]
        if not path.is_file():
            raise FileNotFoundError(f"Missing Figure 5 {category}: {path}")
        observed = sha256_file(path)
        if observed != entry["sha256"]:
            raise AssertionError(
                f"Figure 5 {category} checksum changed for {entry['path']}: {observed}"
            )


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("figure") != "Figure 5" or manifest.get("target_width_mm") != 170:
        raise AssertionError("Figure 5 identity or target width changed")
    if manifest.get("ga_rerun") or manifest.get("model_refit"):
        raise AssertionError("Figure 5 manifest unexpectedly reports a scientific rerun")
    if manifest.get("panel_labels") != ["a)", "b)", "c)"]:
        raise AssertionError("Figure 5 panel-label inventory changed")
    validate_entries(manifest["source_files"], "aggregate source")
    validate_entries(manifest["outputs"], "rendered output")
    print("Figure 5 provenance checks passed: local aggregate sources and outputs match the frozen manifest.")


if __name__ == "__main__":
    main()
