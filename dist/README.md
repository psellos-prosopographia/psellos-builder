# dist output structure

Compiled artifacts in `dist/` are static JSON designed for psellos-web consumption.

```
dist/
  assertions/
    core.json            # filtered assertions for the core narrative layer
  indexes/
    by-person.json       # map of person-id -> list of assertion ids
    by-place.json        # map of place-id -> list of assertion ids
    by-relation.json     # map of relation-id -> list of assertion ids
  meta.json              # build metadata (version, timestamps, provenance)
```

Notes:

- File names are stable to keep psellos-web integration simple.
- Additional narrative layers can be added as sibling files under `assertions/`.
- Metadata should include the psellos-spec version used for validation.
