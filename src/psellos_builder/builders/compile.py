"""Pipeline orchestration for building dataset artifacts."""
from __future__ import annotations

from pathlib import Path

from psellos_builder.builders.manifest import build_manifest
from psellos_builder.exporters.dist_writer import write_dist
from psellos_builder.validators.schema import validate_schema


def compile_dataset(*, spec_path: Path, input_path: Path, dist_path: Path) -> None:
    """Run the build pipeline for validation and dist output."""
    dataset = validate_schema(spec_path=spec_path, input_path=input_path)
    manifest = build_manifest(dataset, spec_path=spec_path, input_path=input_path)
    write_dist(
        dist_path=dist_path,
        manifest=manifest,
        dataset=dataset,
        input_path=input_path,
    )
