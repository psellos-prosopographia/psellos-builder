# dist output structure

Compiled artifacts in `dist/` are static JSON designed for downstream consumption.

```
dist/
  manifest.json           # spec version, counts, and person index
  persons.json            # person id -> person object (verbatim)
  assertions.json         # assertions array (verbatim)
```

Notes:

- File names are stable to keep consumer integration simple.
- `manifest.json` includes `spec_version`, `counts`, and `person_index` (person id → name).
- Manifest person index uses best-effort display name resolution (name/label/names/id).
- `persons.json` is an object keyed by person id containing the validated person objects
  from the input dataset (no enrichment).
- `assertions.json` is the validated assertions array from the input dataset (no enrichment).
