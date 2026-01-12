# psellos-builder

Build pipeline and CLI for validating and compiling prosopographical datasets into static JSON artifacts consumable by psellos-web.

## Overview

psellos-builder treats **psellos-spec v0.1.0** as an immutable source of truth and produces derived artifacts only. It does not provide UI, visualization, or authoring features. Targets psellos-spec v0.1.0.

## Installation

```bash
python -m pip install -e .
```

Example run (using demo dataset paths):

```bash
python -m psellos_builder.cli --spec ../psellos-spec/schema.json ../psellos-data/demo.json
```

## Project context

psellos-builder is one component in the broader psellos ecosystem, with coordination and planning tracked in `psellos-hub`.

### Inputs

- **Spec:** psellos-spec v0.1.0 (immutable), provided as either a JSON Schema file or a directory containing `schema.json`.
- **Raw data:** a single dataset JSON file that follows the spec.

### Outputs

- **Manifest:** `dist/manifest.json` containing the spec version, counts (persons and assertions), and a person index (id → name).

### Non-goals

- No visualization or UI rendering.
- No authoring interface for datasets.
- No mutation of psellos-spec or spec-derived schemas.
- No geography assumptions or rendering logic.

## Project layout

```
src/psellos_builder/
  cli.py                 # CLI entry point
  builders/
    compile.py            # Pipeline orchestration
    manifest.py           # Manifest generation
  validators/
    schema.py             # Schema validation
  exporters/
    dist_writer.py        # Dist serialization
```

Validators, builders, and exporters are intentionally separate to keep contracts explicit.

## CLI

```bash
python -m psellos_builder.cli --spec /path/to/psellos-spec/schema.json /path/to/dataset.json
```

The CLI validates the dataset against psellos-spec v0.1.0 and writes a deterministic manifest to `dist/`.

## Pipeline flow

1. **Schema validation** ensures the raw dataset matches psellos-spec v0.1.0.
2. **Manifest generation** emits a deterministic summary of persons and assertions.

## Output structure

See `dist/README.md` for the expected artifact layout.
