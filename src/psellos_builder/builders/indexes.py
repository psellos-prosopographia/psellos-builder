"""Index generation for compiled datasets."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class IndexBundle:
    """Placeholder index container for compiled artifacts."""

    by_person: dict[str, list[str]]
    by_place: dict[str, list[str]]
    by_relation: dict[str, list[str]]


def build_indexes(assertions: Iterable[dict]) -> IndexBundle:
    """Stub for generating indexes from filtered assertions."""
    return IndexBundle(by_person={}, by_place={}, by_relation={})
