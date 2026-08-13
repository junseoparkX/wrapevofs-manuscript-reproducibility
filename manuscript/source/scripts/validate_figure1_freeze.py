from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE_ROOT = HERE.parent
MANIFEST = SOURCE_ROOT / "FIGURE1_FREEZE.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = manifest["sha256"]
    authority = SOURCE_ROOT / manifest["authority"]
    observed = {"authority": sha256(authority)}
    failures = {name: value for name, value in observed.items() if value != expected}
    if failures:
        raise SystemExit(
            "Figure 1 freeze validation failed: "
            + json.dumps(failures, sort_keys=True)
        )
    print(json.dumps({"status": "PASS", "sha256": expected}, sort_keys=True))


if __name__ == "__main__":
    main()
