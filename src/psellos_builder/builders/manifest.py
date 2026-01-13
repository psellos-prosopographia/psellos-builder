"""Manifest generation for compiled datasets."""
from __future__ import annotations

import os
from pathlib import Path
from importlib.metadata import PackageNotFoundError, version
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


def _resolve_builder_version() -> str:
    try:
        return version("psellos-builder")
    except PackageNotFoundError:
        return "unknown"


DEFAULT_BUILD_TIMESTAMP = "1970-01-01T00:00:00Z"


def _resolve_build_timestamp() -> str:
    value = os.environ.get("PSELLOS_BUILD_TIMESTAMP")
    if isinstance(value, str) and value.strip():
        return value
    return DEFAULT_BUILD_TIMESTAMP


def _derive_spec_version(spec_path: Path) -> str:
    filename = spec_path.name
    if not filename.endswith(".json"):
        raise ValueError(
            f"Spec path must end with .json to derive spec_version: {spec_path}"
        )
    spec_version = filename[: -len(".json")]
    if not spec_version:
        raise ValueError(
            f"Spec path must include a filename before .json to derive spec_version: {spec_path}"
        )
    return spec_version


def build_manifest(
    dataset: dict[str, Any], *, spec_path: Path, input_path: Path
) -> dict[str, Any]:
    """Build the deterministic manifest JSON payload."""
    persons = dataset.get("persons", [])
    assertions = dataset.get("assertions", [])

    person_index: dict[str, str] = {}
    for person in sorted(persons, key=lambda entry: entry["id"]):
        person_id = person["id"]
        if person_id in person_index:
            raise ValueError(f"Duplicate person id detected: {person_id}")
        person_index[person_id] = _resolve_person_display_name(person, person_id)

    manifest = {
        "spec_version": _derive_spec_version(spec_path),
        "generated_at": _resolve_build_timestamp(),
        "spec": {
            "identifier": spec_path.as_posix(),
            "version": SPEC_VERSION,
        },
        "builder_version": _resolve_builder_version(),
        "build_timestamp": _resolve_build_timestamp(),
        "dataset_path": input_path.as_posix(),
        "counts": {
            "persons": len(persons),
            "assertions": len(assertions),
        },
        "person_index": person_index,
    }
    return manifest
