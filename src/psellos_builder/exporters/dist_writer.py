"""Write compiled artifacts into the dist/ directory."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_dist(*, dist_path: Path, manifest: dict[str, Any]) -> None:
    """Serialize compiled artifacts as static JSON."""
    dist_path.mkdir(parents=True, exist_ok=True)
    manifest_path = dist_path / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, sort_keys=True, indent=2)
        handle.write("\n")
