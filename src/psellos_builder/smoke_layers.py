"""Smoke test for narrative layer artifacts."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from psellos_builder.builders.compile import compile_dataset

DEFAULT_SPEC = Path("../psellos-spec/schema.json")
DEFAULT_FIXTURE = Path("../psellos-data/fixture.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="psellos-builder-smoke",
        description="Run a deterministic smoke test for layer artifacts.",
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


def _validate_assertions_by_layer(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError("assertions_by_layer.json was not created.")
    raw = _load_json(path)
    if not isinstance(raw, dict):
        raise TypeError("assertions_by_layer.json must be a JSON object.")

    layers = list(raw.keys())
    _assert_sorted_list(layers, "Layer keys")

    for layer, assertion_ids in raw.items():
        if not isinstance(layer, str):
            raise TypeError("Layer keys must be strings.")
        if not isinstance(assertion_ids, list):
            raise TypeError(f"Layer {layer} assertion ids must be a list.")
        if not all(isinstance(entry, str) for entry in assertion_ids):
            raise TypeError(f"Layer {layer} assertion ids must be strings.")
        _assert_sorted_list(assertion_ids, f"Assertion ids for {layer}")

    return layers


def _validate_layers_json(path: Path, expected_layers: list[str]) -> None:
    if not path.exists():
        raise FileNotFoundError("layers.json was not created.")
    raw = _load_json(path)
    if not isinstance(raw, list):
        raise TypeError("layers.json must be a JSON array.")
    if not all(isinstance(entry, str) for entry in raw):
        raise TypeError("layers.json entries must be strings.")
    _assert_sorted_list(raw, "layers.json entries")
    if raw != expected_layers:
        raise ValueError("layers.json must match assertions_by_layer.json keys.")


def run_smoke(*, input_path: Path, spec_path: Path, dist_path: Path) -> None:
    compile_dataset(spec_path=spec_path, input_path=input_path, dist_path=dist_path)
    layers = _validate_assertions_by_layer(dist_path / "assertions_by_layer.json")
    _validate_layers_json(dist_path / "layers.json", layers)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.dist:
            run_smoke(input_path=args.input, spec_path=args.spec, dist_path=args.dist)
        else:
            with tempfile.TemporaryDirectory() as temp_dir:
                run_smoke(
                    input_path=args.input,
                    spec_path=args.spec,
                    dist_path=Path(temp_dir),
                )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
