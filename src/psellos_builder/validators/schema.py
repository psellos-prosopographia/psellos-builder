"""Schema validation against psellos-spec v0.1.0."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SPEC_VERSION = "v0.1.0"

MINIMAL_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["persons", "assertions"],
    "properties": {
        "persons": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "name"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                },
                "additionalProperties": True,
            },
        },
        "assertions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id"],
                "properties": {
                    "id": {"type": "string"},
                },
                "additionalProperties": True,
            },
        },
    },
    "additionalProperties": True,
}


def load_dataset(input_path: Path) -> dict[str, Any]:
    """Load the raw dataset JSON file."""
    if not input_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {input_path}")
    if not input_path.is_file():
        raise ValueError(f"Dataset path must be a JSON file: {input_path}")
    try:
        with input_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in dataset file {input_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Dataset root must be a JSON object.")
    return data


def load_schema(spec_path: Path) -> tuple[dict[str, Any], Path | None]:
    """Load a JSON schema from the spec directory or file, if present."""
    if spec_path.is_file():
        with spec_path.open("r", encoding="utf-8") as handle:
            return json.load(handle), spec_path.parent
    if spec_path.is_dir():
        candidate = spec_path / "schema.json"
        if candidate.exists():
            with candidate.open("r", encoding="utf-8") as handle:
                return json.load(handle), spec_path
    return MINIMAL_SCHEMA, None


def _schema_path_for_uri(uri: str, schema_dir: Path) -> Path | None:
    base_uri = uri.split("#", 1)[0]
    if not base_uri:
        return None
    if base_uri.startswith("https://psellos.org/spec/schema/"):
        filename = base_uri.rsplit("/", 1)[-1]
        return schema_dir / filename
    parsed = urlparse(base_uri)
    if not parsed.scheme and base_uri.endswith(".json"):
        return schema_dir / base_uri
    return None


def _format_error_path(error_path: Any) -> str:
    if not error_path:
        return "<root>"
    return "/".join(str(part) for part in error_path)


def _manual_validate(data: dict[str, Any]) -> None:
    if "persons" not in data or "assertions" not in data:
        raise ValueError("Dataset must contain 'persons' and 'assertions' arrays.")
    persons = data["persons"]
    assertions = data["assertions"]
    if not isinstance(persons, list):
        raise ValueError("'persons' must be an array.")
    if not isinstance(assertions, list):
        raise ValueError("'assertions' must be an array.")
    for index, person in enumerate(persons):
        if not isinstance(person, dict):
            raise ValueError(f"persons[{index}] must be an object.")
        if "id" not in person or "name" not in person:
            raise ValueError(f"persons[{index}] requires 'id' and 'name'.")
        if not isinstance(person["id"], str):
            raise ValueError(f"persons[{index}].id must be a string.")
        if not isinstance(person["name"], str):
            raise ValueError(f"persons[{index}].name must be a string.")
    for index, assertion in enumerate(assertions):
        if not isinstance(assertion, dict):
            raise ValueError(f"assertions[{index}] must be an object.")
        if "id" not in assertion:
            raise ValueError(f"assertions[{index}] requires 'id'.")
        if not isinstance(assertion["id"], str):
            raise ValueError(f"assertions[{index}].id must be a string.")


def validate_schema(*, spec_path: Path, input_path: Path) -> dict[str, Any]:
    """Validate the input dataset against the psellos-spec JSON schema."""
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec path not found: {spec_path}")

    data = load_dataset(input_path)
    schema, schema_dir = load_schema(spec_path)

    if importlib.util.find_spec("jsonschema") is None:
        _manual_validate(data)
        return data

    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource

    if schema_dir is not None:
        def retrieve(uri: str) -> Resource:
            candidate = _schema_path_for_uri(uri, schema_dir)
            if candidate is None:
                raise ValueError(f"Unsupported schema reference: {uri}")
            if not candidate.exists():
                if candidate.name == "core.snap.v0.1.json":
                    raise FileNotFoundError(
                        "Missing referenced schema core.snap.v0.1.json at "
                        f"{candidate}"
                    )
                raise FileNotFoundError(f"Referenced schema not found: {candidate}")
            with candidate.open("r", encoding="utf-8") as handle:
                contents = json.load(handle)
            return Resource.from_contents(contents)

        registry = Registry(retrieve=retrieve)
        validator = Draft202012Validator(schema, registry=registry)
    else:
        validator = Draft202012Validator(schema)
    error = next(validator.iter_errors(data), None)
    if error is not None:
        location = _format_error_path(error.path)
        raise ValueError(f"Schema validation error at {location}: {error.message}")
    return data
