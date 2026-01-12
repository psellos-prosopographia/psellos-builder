"""Manifest generation for compiled datasets."""
from __future__ import annotations

from typing import Any

from psellos_builder.validators.schema import SPEC_VERSION


def _resolve_person_display_name(person: dict[str, Any], person_id: str) -> str:
    name = person.get("name")
    if isinstance(name, str):
        return name
    label = person.get("label")
    if isinstance(label, str):
        return label
    names = person.get("names")
    if isinstance(names, list) and names:
        first = names[0]
        if isinstance(first, dict):
            value = first.get("value")
            if isinstance(value, str):
                return value
            nested_name = first.get("name")
            if isinstance(nested_name, str):
                return nested_name
        elif isinstance(first, str):
            return first
    return person_id


def build_manifest(dataset: dict[str, Any]) -> dict[str, Any]:
    """Build the deterministic manifest JSON payload."""
    persons = dataset.get("persons", [])
    assertions = dataset.get("assertions", [])

    person_index: dict[str, str] = {}
    for person in sorted(persons, key=lambda entry: entry["id"]):
        person_id = person["id"]
        if person_id in person_index:
            raise ValueError(f"Duplicate person id detected: {person_id}")
        person_index[person_id] = _resolve_person_display_name(person, person_id)

    return {
        "spec_version": SPEC_VERSION,
        "counts": {
            "persons": len(persons),
            "assertions": len(assertions),
        },
        "person_index": person_index,
    }
