"""Write compiled artifacts into the dist/ directory."""
from __future__ import annotations

from pathlib import Path

from psellos_builder.builders.indexes import IndexBundle


def write_dist(*, dist_path: Path, assertions: list[dict], indexes: IndexBundle) -> None:
    """Stub for serializing compiled artifacts as static JSON."""
    _ = assertions
    _ = indexes
    dist_path.mkdir(parents=True, exist_ok=True)
