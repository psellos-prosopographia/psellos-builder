"""Assertion filtering helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable


def filter_assertions_by_layer(*, input_path: Path, layers: Iterable[str]) -> list[dict]:
    """Stub for selecting assertions by narrative layer."""
    _ = input_path
    _ = list(layers)
    return []
