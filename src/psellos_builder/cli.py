"""Command-line interface for psellos-builder."""
from __future__ import annotations

import argparse
from pathlib import Path

from psellos_builder.builders.compile import compile_dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="psellos-builder",
        description="Validate and compile prosopographical datasets into static JSON artifacts.",
    )
    parser.add_argument("input", type=Path, help="Path to raw dataset directory.")
    parser.add_argument("--spec", type=Path, required=True, help="Path to psellos-spec v0.1 directory.")
    parser.add_argument(
        "--dist",
        type=Path,
        default=Path("dist"),
        help="Output directory for compiled artifacts.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    compile_dataset(spec_path=args.spec, input_path=args.input, dist_path=args.dist)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
