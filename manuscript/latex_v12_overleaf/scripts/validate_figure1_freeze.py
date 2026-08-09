from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
V11 = HERE.parent
ROOT = V11.parents[1]
MANIFEST = V11 / "FIGURE1_FREEZE.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = manifest["sha256"]
    authority = ROOT / manifest["authority"]
    frozen = ROOT / manifest["frozen_v11_path"]
    observed = {
        "authority": sha256(authority),
        "frozen_v11": sha256(frozen),
    }
    failures = {name: value for name, value in observed.items() if value != expected}
    if failures:
        raise SystemExit(
            "Figure 1 freeze validation failed: "
            + json.dumps(failures, sort_keys=True)
        )
    print(json.dumps({"status": "PASS", "sha256": expected}, sort_keys=True))


if __name__ == "__main__":
    main()
