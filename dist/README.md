# dist output structure

Compiled artifacts in `dist/` are static JSON designed for downstream consumption.

```
dist/
  manifest.json           # spec version, counts, and person index
```

Notes:

- File names are stable to keep consumer integration simple.
- `manifest.json` includes `spec_version`, `counts`, and `person_index` (person id → name).
- Manifest person index uses best-effort display name resolution (name/label/names/id).
