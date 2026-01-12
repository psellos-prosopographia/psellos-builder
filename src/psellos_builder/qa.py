"""Quality checks for layer indexing output."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from psellos_builder.builders.manifest import build_manifest
from psellos_builder.exporters.dist_writer import write_dist
from psellos_builder.validators.schema import validate_schema

DEFAULT_SPEC = Path("../psellos-spec/schema.json")
DEFAULT_FIXTURE = Path("../psellos-data/fixture.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="psellos-builder-qa",
        description="Run QA checks against compiled layer artifacts.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=DEFAULT_FIXTURE,
        help="Path to fixture dataset JSON file.",
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=DEFAULT_SPEC,
        help="Path to psellos-spec v0.1.0 schema.",
    )
    parser.add_argument(
        "--dist",
        type=Path,
        help="Optional dist output directory (defaults to a temp directory).",
    )
    return parser


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _assert_sorted_list(items: list[str], label: str) -> None:
    if items != sorted(items):
        raise ValueError(f"{label} must be sorted lexicographically.")


def _expected_layer_for_assertion(assertion: dict[str, Any]) -> str:
    extensions = assertion.get("extensions")
    if isinstance(extensions, dict):
        psellos = extensions.get("psellos")
        if isinstance(psellos, dict):
            layer = psellos.get("layer")
            if isinstance(layer, str) and layer:
                return layer
    return "canon"


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


def _build_expected_assertions_by_layer(
    assertions: list[dict[str, Any]],
) -> dict[str, list[str]]:
    assertions_by_layer: dict[str, set[str]] = {}
    for assertion in assertions:
        assertion_id = assertion.get("id")
        if not isinstance(assertion_id, str):
            continue
        layer = _expected_layer_for_assertion(assertion)
        assertions_by_layer.setdefault(layer, set()).add(assertion_id)
    return {
        layer: sorted(assertions_by_layer[layer])
        for layer in sorted(assertions_by_layer)
    }


def _build_expected_assertions_by_id(
    assertions: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    normalized = [_normalize_assertion(assertion) for assertion in assertions]
    expected: dict[str, dict[str, Any]] = {}
    for assertion in normalized:
        assertion_id = assertion.get("id")
        if not isinstance(assertion_id, str):
            continue
        expected[assertion_id] = assertion
    return expected


def _validate_assertions_by_layer(
    *,
    assertions_by_layer_path: Path,
    expected: dict[str, list[str]],
) -> list[str]:
    if not assertions_by_layer_path.exists():
        raise FileNotFoundError("assertions_by_layer.json was not created.")
    raw = _load_json(assertions_by_layer_path)
    if not isinstance(raw, dict):
        raise TypeError("assertions_by_layer.json must be a JSON object.")

    layers = list(raw.keys())
    _assert_sorted_list(layers, "Layer keys")

    normalized: dict[str, list[str]] = {}
    for layer, assertion_ids in raw.items():
        if not isinstance(layer, str):
            raise TypeError("Layer keys must be strings.")
        if not isinstance(assertion_ids, list):
            raise TypeError(f"Layer {layer} assertion ids must be a list.")
        if not all(isinstance(entry, str) for entry in assertion_ids):
            raise TypeError(f"Layer {layer} assertion ids must be strings.")
        _assert_sorted_list(assertion_ids, f"Assertion ids for {layer}")
        normalized[layer] = assertion_ids

    if normalized != expected:
        raise ValueError(
            "assertions_by_layer.json does not match the expected layer index."
        )
    return layers


def _validate_layers_json(layers_path: Path, expected_layers: list[str]) -> None:
    if not layers_path.exists():
        raise FileNotFoundError("layers.json was not created.")
    raw = _load_json(layers_path)
    if not isinstance(raw, list):
        raise TypeError("layers.json must be a JSON array.")
    if not all(isinstance(entry, str) for entry in raw):
        raise TypeError("layers.json entries must be strings.")
    _assert_sorted_list(raw, "layers.json entries")
    if raw != expected_layers:
        raise ValueError("layers.json must match assertions_by_layer.json keys.")


def _validate_assertions_by_id(
    *, assertions_by_id_path: Path, expected: dict[str, dict[str, Any]]
) -> None:
    if not assertions_by_id_path.exists():
        raise FileNotFoundError("assertions_by_id.json was not created.")
    raw = _load_json(assertions_by_id_path)
    if not isinstance(raw, dict):
        raise TypeError("assertions_by_id.json must be a JSON object.")
    keys = list(raw.keys())
    _assert_sorted_list(keys, "assertions_by_id.json keys")
    if raw != expected:
        raise ValueError("assertions_by_id.json does not match expected assertions.")


def run_check(*, input_path: Path, spec_path: Path, dist_path: Path) -> None:
    dataset = validate_schema(spec_path=spec_path, input_path=input_path)
    manifest = build_manifest(dataset)
    write_dist(dist_path=dist_path, manifest=manifest, dataset=dataset)

    expected_by_id = _build_expected_assertions_by_id(
        dataset.get("assertions", [])
    )
    expected_by_layer = _build_expected_assertions_by_layer(
        dataset.get("assertions", [])
    )
    _validate_assertions_by_id(
        assertions_by_id_path=dist_path / "assertions_by_id.json",
        expected=expected_by_id,
    )
    assertions_by_layer_path = dist_path / "assertions_by_layer.json"
    layers = _validate_assertions_by_layer(
        assertions_by_layer_path=assertions_by_layer_path,
        expected=expected_by_layer,
    )
    _validate_layers_json(dist_path / "layers.json", layers)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.dist:
        run_check(input_path=args.input, spec_path=args.spec, dist_path=args.dist)
        return 0
    with tempfile.TemporaryDirectory() as temp_dir:
        run_check(
            input_path=args.input,
            spec_path=args.spec,
            dist_path=Path(temp_dir),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
