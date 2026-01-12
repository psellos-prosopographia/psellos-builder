"""Pipeline orchestration for building dataset artifacts."""
from __future__ import annotations

from pathlib import Path

from psellos_builder.exporters.dist_writer import write_dist
from psellos_builder.validators.schema import validate_schema
from psellos_builder.validators.assertions import filter_assertions_by_layer
from psellos_builder.builders.indexes import build_indexes


def compile_dataset(*, spec_path: Path, input_path: Path, dist_path: Path) -> None:
    """Run the scaffolded build pipeline.

    This function wires together validation, filtering, index generation, and
    export of the compiled artifacts.
    """
    validate_schema(spec_path=spec_path, input_path=input_path)
    assertions = filter_assertions_by_layer(input_path=input_path, layers=["core"])
    indexes = build_indexes(assertions)
    write_dist(dist_path=dist_path, assertions=assertions, indexes=indexes)
