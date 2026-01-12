# dist output structure

Compiled artifacts in `dist/` are static JSON designed for downstream consumption.

```
dist/
  manifest.json           # spec identifier/version, builder version, build timestamp, dataset path, counts, and person index
  persons.json            # person id -> person object (verbatim)
  assertions.json         # assertions array (verbatim)
  assertions_by_person.json  # person id -> assertion ids (subject + object)
  assertions_by_id.json   # assertion id -> assertion object (verbatim)
  assertions_by_layer.json  # layer id -> assertion ids
  assertions_by_person_by_layer.json  # person id -> layer id -> assertion ids
  layers.json             # layer ids (sorted)
  layers_meta.json        # optional layer metadata (sorted by order/id)
  layer_stats.json        # layer diagnostics + statistics
```

Notes:

- File names are stable to keep consumer integration simple.
- Export flows can be implemented as client-side joins across these artifacts
  (for example, using `layers.json`, `assertions_by_layer.json`, and
  `assertions_by_id.json` together).
- `manifest.json` includes `spec.identifier`, `spec.version`, `builder_version`,
  `build_timestamp`, `dataset_path`, `counts`, and `person_index` (person id → name).
  `build_timestamp` comes from `PSELLOS_BUILD_TIMESTAMP`, defaulting to
  `1970-01-01T00:00:00Z` when unset.
- Manifest person index uses best-effort display name resolution (name/label/names/id).
- `persons.json` is an object keyed by person id containing the validated person objects
  from the input dataset (no enrichment).
- `assertions.json` is the validated assertions array from the input dataset (no enrichment).
- `assertions.json` uses flat endpoint IDs; person labels are resolved via persons.json.
- `assertions_by_person.json` is an adjacency index for O(1) lookup of assertions for a person,
  keyed by person id and populated from both subject and object endpoints.
- `assertions_by_id.json` is an adjacency index for O(1) lookup of assertions by id, reusing the
  same normalized assertion shape as `assertions.json`. All other assertion fields (including
  `predicate`, `extensions.psellos.rel`, and any source/citation fields) are preserved unchanged.
- `assertions_by_layer.json` indexes assertion IDs by narrative layer, defaulting to `canon` when
  the `extensions.psellos.layer` field is missing for an assertion.
- `assertions_by_person_by_layer.json` indexes assertion IDs by person and layer, combining subject
  and object endpoints, and defaulting to `canon` when the `extensions.psellos.layer` field is missing.
- `layers.json` lists available narrative layers, derived from `assertions_by_layer.json` keys
  (including `canon` only when present in assertions).
- `layers_meta.json` is emitted when a `layers_meta.source.json` file is present alongside the
  dataset input; it contains curated layer metadata sorted by `order` then `id`.
- `layer_stats.json` contains deterministic diagnostics, including assertion/person counts by
  layer, relationship type distributions (missing rels counted as `(none)`), top persons by layer,
  and optional canon comparisons.
- Adjacency indices are rebuilt on every run and are authoritative for downstream consumers.
