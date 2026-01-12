"""Manifest generation for compiled datasets."""
from __future__ import annotations

from typing import Any

from psellos_builder.validators.schema import SPEC_VERSION


def build_manifest(dataset: dict[str, Any]) -> dict[str, Any]:
    """Build the deterministic manifest JSON payload."""
    persons = dataset.get("persons", [])
    assertions = dataset.get("assertions", [])

    person_index: dict[str, str] = {}
    for person in sorted(persons, key=lambda entry: entry["id"]):
        person_id = person["id"]
        if person_id in person_index:
            raise ValueError(f"Duplicate person id detected: {person_id}")
        person_index[person_id] = person["name"]

    return {
        "spec_version": SPEC_VERSION,
        "counts": {
            "persons": len(persons),
            "assertions": len(assertions),
        },
        "person_index": person_index,
    }
