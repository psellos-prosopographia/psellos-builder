# psellos-builder

Build pipeline and CLI for validating and compiling prosopographical datasets into static JSON artifacts consumable by psellos-web.

## Overview

psellos-builder treats **psellos-spec v0.1.x** as an immutable source of truth and produces derived artifacts only. It does not provide UI, visualization, or authoring features.

## Project context

psellos-builder is one component in the broader psellos ecosystem, with coordination and planning tracked in `psellos-hub`.

### Inputs

- **Spec:** psellos-spec v0.1.x (immutable), provided as a directory path.
- **Raw data:** a dataset directory containing source JSON (or compatible) files that follow the spec.
- **Expected directories:** the builder expects a spec directory and a dataset root (with raw data files under that root).

### Outputs

- **Compiled assertions:** filtered assertions aligned to the desired narrative layer(s).
- **Indexes:** static JSON indexes that power browsing and lookups in psellos-web.
- **Dist layout:** a consistent `/dist/` tree with JSON artifacts (documented in `dist/README.md`), including `assertions/`, `indexes/`, and `meta.json` at a high level.

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
    indexes.py            # Index generation (stub)
  validators/
    schema.py             # Schema validation (stub)
    assertions.py         # Narrative-layer filtering (stub)
  exporters/
    dist_writer.py        # Dist serialization (stub)
```

Validators, builders, and exporters are intentionally separate to keep contracts explicit.

## CLI

```bash
python -m psellos_builder.cli --spec /path/to/psellos-spec /path/to/dataset
```

The CLI currently orchestrates a stubbed pipeline for validation, filtering, index creation, and dist output.

## Pipeline flow

1. **Schema validation** ensures the raw dataset matches psellos-spec v0.1.x.
2. **Assertion filtering** selects assertions by narrative layer (e.g., `core`).
3. **Index generation** creates lookup maps for person, place, and relation.
4. **Dist export** writes static JSON artifacts to `/dist/`.

## Output structure

See `dist/README.md` for the expected artifact layout.
