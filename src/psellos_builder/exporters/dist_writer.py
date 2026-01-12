"""Write compiled artifacts into the dist/ directory."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from psellos_builder.layers import build_layer_indexes


def _normalize_endpoint(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and "id" in value:
        return str(value["id"])
    raise ValueError(f"Unexpected assertion endpoint shape: {value!r}")


def _normalize_assertion(assertion: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(assertion)
    if "subject" in normalized:
        normalized["subject"] = _normalize_endpoint(normalized["subject"])
    if "object" in normalized:
        normalized["object"] = _normalize_endpoint(normalized["object"])
    return normalized


def _add_to_index(
    index: dict[str, set[str]], person_id: str, assertion_id: str
) -> None:
    index.setdefault(person_id, set()).add(assertion_id)


def _build_assertion_indexes(
    assertions: list[dict[str, Any]]
) -> tuple[dict[str, list[str]], dict[str, dict[str, Any]]]:
    assertions_by_person: dict[str, set[str]] = {}
    assertions_by_id: dict[str, dict[str, Any]] = {}
    for assertion in assertions:
        assertion_id = assertion.get("id")
        if not isinstance(assertion_id, str):
            continue
        assertions_by_id[assertion_id] = assertion
        if "subject" in assertion:
            _add_to_index(assertions_by_person, assertion["subject"], assertion_id)
        if "object" in assertion:
            _add_to_index(assertions_by_person, assertion["object"], assertion_id)
    sorted_by_person = {
        person_id: sorted(assertion_ids)
        for person_id, assertion_ids in assertions_by_person.items()
    }
    return sorted_by_person, assertions_by_id


def write_dist(
    *, dist_path: Path, manifest: dict[str, Any], dataset: dict[str, Any]
) -> None:
    """Serialize compiled artifacts as static JSON."""
    dist_path.mkdir(parents=True, exist_ok=True)
    manifest_path = dist_path / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, sort_keys=True, indent=2)
        handle.write("\n")

    persons_path = dist_path / "persons.json"
    persons_by_id: dict[str, Any] = {}
    for person in sorted(dataset.get("persons", []), key=lambda entry: entry["id"]):
        person_id = person["id"]
        if person_id in persons_by_id:
            raise ValueError(f"Duplicate person id detected: {person_id}")
        persons_by_id[person_id] = person
    with persons_path.open("w", encoding="utf-8") as handle:
        json.dump(persons_by_id, handle, sort_keys=True, indent=2)
        handle.write("\n")

    assertions_path = dist_path / "assertions.json"
    with assertions_path.open("w", encoding="utf-8") as handle:
        assertions = dataset.get("assertions", [])
        normalized_assertions = [
            _normalize_assertion(assertion) for assertion in assertions
        ]
        json.dump(normalized_assertions, handle, sort_keys=True, indent=2)
        handle.write("\n")

    assertions_by_person, assertions_by_id = _build_assertion_indexes(
        normalized_assertions
    )
    assertions_by_layer, assertions_by_person_by_layer = build_layer_indexes(
        normalized_assertions
    )

    assertions_by_person_path = dist_path / "assertions_by_person.json"
    with assertions_by_person_path.open("w", encoding="utf-8") as handle:
        json.dump(assertions_by_person, handle, sort_keys=True, indent=2)
        handle.write("\n")

    assertions_by_id_path = dist_path / "assertions_by_id.json"
    with assertions_by_id_path.open("w", encoding="utf-8") as handle:
        json.dump(assertions_by_id, handle, sort_keys=True, indent=2)
        handle.write("\n")

    assertions_by_layer_path = dist_path / "assertions_by_layer.json"
    with assertions_by_layer_path.open("w", encoding="utf-8") as handle:
        json.dump(assertions_by_layer, handle, sort_keys=True, indent=2)
        handle.write("\n")

    layers_path = dist_path / "layers.json"
    with layers_path.open("w", encoding="utf-8") as handle:
        json.dump(sorted(assertions_by_layer.keys()), handle, indent=2)
        handle.write("\n")

    assertions_by_person_by_layer_path = (
        dist_path / "assertions_by_person_by_layer.json"
    )
    with assertions_by_person_by_layer_path.open("w", encoding="utf-8") as handle:
        json.dump(
            assertions_by_person_by_layer, handle, sort_keys=True, indent=2
        )
        handle.write("\n")
