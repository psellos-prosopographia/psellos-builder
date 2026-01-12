"""Write compiled artifacts into the dist/ directory."""
from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Any

from psellos_builder.layers import build_layer_indexes

LAYER_META_SOURCE_NAME = "layers_meta.source.json"
MAX_TOP_PERSONS = 20
MISSING_REL_TYPE = "(none)"


def _normalize_endpoint(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and "id" in value:
        return str(value["id"])
    raise ValueError(f"Unexpected assertion endpoint shape: {value!r}")


def _normalize_assertion(assertion: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(assertion)
    if "subject" in normalized:
        normalized["subject"] = _normalize_endpoint(normalized["subject"])
    if "object" in normalized:
        normalized["object"] = _normalize_endpoint(normalized["object"])
    return normalized


def _add_to_index(
    index: dict[str, set[str]], person_id: str, assertion_id: str
) -> None:
    index.setdefault(person_id, set()).add(assertion_id)


def _build_assertion_indexes(
    assertions: list[dict[str, Any]]
) -> tuple[dict[str, list[str]], dict[str, dict[str, Any]]]:
    assertions_by_person: dict[str, set[str]] = {}
    assertions_by_id: dict[str, dict[str, Any]] = {}
    for assertion in assertions:
        assertion_id = assertion.get("id")
        if not isinstance(assertion_id, str):
            continue
        assertions_by_id[assertion_id] = assertion
        if "subject" in assertion:
            _add_to_index(assertions_by_person, assertion["subject"], assertion_id)
        if "object" in assertion:
            _add_to_index(assertions_by_person, assertion["object"], assertion_id)
    sorted_by_person = {
        person_id: sorted(assertion_ids)
        for person_id, assertion_ids in assertions_by_person.items()
    }
    return sorted_by_person, assertions_by_id


def _load_layers_meta_source(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _normalize_layer_meta(
    *, raw: dict[str, Any], observed_layers: list[str], source_path: Path
) -> dict[str, Any]:
    layers = raw.get("layers")
    if not isinstance(layers, list):
        raise TypeError(
            f"{source_path} must contain a 'layers' array for layer metadata."
        )
    seen_ids: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for entry in layers:
        if not isinstance(entry, dict):
            raise TypeError(f"{source_path} layer entries must be objects.")
        layer_id = entry.get("id")
        if not isinstance(layer_id, str) or not layer_id:
            raise TypeError(f"{source_path} layer entries must include a string id.")
        if layer_id in seen_ids:
            raise ValueError(f"{source_path} contains duplicate layer id {layer_id!r}.")
        seen_ids.add(layer_id)
        order = entry.get("order", 0)
        if not isinstance(order, int):
            raise TypeError(
                f"{source_path} layer entry {layer_id!r} has non-integer order."
            )
        normalized.append(dict(entry))
    extras = sorted(set(seen_ids) - set(observed_layers))
    if extras:
        warnings.warn(
            "Layer metadata includes ids not present in assertions: "
            + ", ".join(extras),
            stacklevel=2,
        )
    normalized.sort(key=lambda item: (item.get("order", 0), item["id"]))
    return {"layers": normalized}


def _load_layers_meta(
    *, input_path: Path | None, observed_layers: list[str]
) -> dict[str, Any] | None:
    if input_path is None:
        return None
    source_path = input_path.parent / LAYER_META_SOURCE_NAME
    if not source_path.exists():
        return None
    raw = _load_layers_meta_source(source_path)
    if not isinstance(raw, dict):
        raise TypeError(f"{source_path} must contain a JSON object.")
    return _normalize_layer_meta(
        raw=raw, observed_layers=observed_layers, source_path=source_path
    )


def _extract_rel_type(assertion: dict[str, Any]) -> str:
    extensions = assertion.get("extensions")
    if isinstance(extensions, dict):
        psellos = extensions.get("psellos")
        if isinstance(psellos, dict):
            rel_type = psellos.get("rel")
            if isinstance(rel_type, str) and rel_type:
                return rel_type
    return MISSING_REL_TYPE


def _increment_rel_counts(
    counts: dict[str, int], assertion: dict[str, Any]
) -> None:
    rel_type = _extract_rel_type(assertion)
    counts[rel_type] = counts.get(rel_type, 0) + 1


def _increment_person_counts(
    counts: dict[str, int], assertion: dict[str, Any]
) -> None:
    subject = assertion.get("subject")
    if isinstance(subject, str):
        counts[subject] = counts.get(subject, 0) + 1
    obj = assertion.get("object")
    if isinstance(obj, str):
        counts[obj] = counts.get(obj, 0) + 1


def _top_persons(counts: dict[str, int]) -> list[dict[str, Any]]:
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [
        {"personId": person_id, "count": count}
        for person_id, count in ranked[:MAX_TOP_PERSONS]
    ]


def _build_layer_stats(
    *,
    assertions_by_layer: dict[str, list[str]],
    assertions_by_person_by_layer: dict[str, dict[str, list[str]]],
    assertions_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    layer_ids = sorted(assertions_by_layer.keys())
    assertion_count_by_layer = {
        layer: len(assertions_by_layer[layer]) for layer in layer_ids
    }
    person_count_by_layer: dict[str, int] = {
        layer: 0 for layer in layer_ids
    }
    persons_by_layer: dict[str, set[str]] = {
        layer: set() for layer in layer_ids
    }
    for person_id, layers in assertions_by_person_by_layer.items():
        for layer in layers:
            if layer in persons_by_layer:
                persons_by_layer[layer].add(person_id)
    for layer in layer_ids:
        person_count_by_layer[layer] = len(persons_by_layer[layer])

    rel_count_by_layer: dict[str, dict[str, int]] = {
        layer: {} for layer in layer_ids
    }
    top_persons_by_layer: dict[str, list[dict[str, Any]]] = {}
    for layer in layer_ids:
        person_counts: dict[str, int] = {}
        for assertion_id in assertions_by_layer[layer]:
            assertion = assertions_by_id.get(assertion_id)
            if not assertion:
                continue
            _increment_rel_counts(rel_count_by_layer[layer], assertion)
            _increment_person_counts(person_counts, assertion)
        top_persons_by_layer[layer] = _top_persons(person_counts)
        rel_count_by_layer[layer] = dict(
            sorted(rel_count_by_layer[layer].items())
        )

    compare_to_canon: dict[str, dict[str, Any]] = {}
    canon_set = set(assertions_by_layer.get("canon", []))
    for layer in layer_ids:
        if layer == "canon":
            continue
        layer_set = set(assertions_by_layer[layer])
        added = sorted(layer_set - canon_set)
        removed = sorted(canon_set - layer_set)
        added_person_counts: dict[str, int] = {}
        removed_person_counts: dict[str, int] = {}
        added_rel_counts: dict[str, int] = {}
        removed_rel_counts: dict[str, int] = {}
        for assertion_id in added:
            assertion = assertions_by_id.get(assertion_id)
            if not assertion:
                continue
            _increment_person_counts(added_person_counts, assertion)
            _increment_rel_counts(added_rel_counts, assertion)
        for assertion_id in removed:
            assertion = assertions_by_id.get(assertion_id)
            if not assertion:
                continue
            _increment_person_counts(removed_person_counts, assertion)
            _increment_rel_counts(removed_rel_counts, assertion)
        compare_to_canon[layer] = {
            "added_count": len(added),
            "removed_count": len(removed),
            "added_persons_topN": _top_persons(added_person_counts),
            "removed_persons_topN": _top_persons(removed_person_counts),
            "added_rel_count_by_type": dict(sorted(added_rel_counts.items())),
            "removed_rel_count_by_type": dict(sorted(removed_rel_counts.items())),
        }

    return {
        "assertion_count_by_layer": assertion_count_by_layer,
        "person_count_by_layer": person_count_by_layer,
        "rel_count_by_layer": rel_count_by_layer,
        "top_persons_by_layer": top_persons_by_layer,
        "compare_to_canon": compare_to_canon,
    }


def write_dist(
    *,
    dist_path: Path,
    manifest: dict[str, Any],
    dataset: dict[str, Any],
    input_path: Path | None = None,
) -> None:
    """Serialize compiled artifacts as static JSON."""
    dist_path.mkdir(parents=True, exist_ok=True)
    manifest_path = dist_path / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, sort_keys=True, indent=2)
        handle.write("\n")

    persons_path = dist_path / "persons.json"
    persons_by_id: dict[str, Any] = {}
    for person in sorted(dataset.get("persons", []), key=lambda entry: entry["id"]):
        person_id = person["id"]
        if person_id in persons_by_id:
            raise ValueError(f"Duplicate person id detected: {person_id}")
        persons_by_id[person_id] = person
    with persons_path.open("w", encoding="utf-8") as handle:
        json.dump(persons_by_id, handle, sort_keys=True, indent=2)
        handle.write("\n")

    assertions_path = dist_path / "assertions.json"
    with assertions_path.open("w", encoding="utf-8") as handle:
        assertions = dataset.get("assertions", [])
        normalized_assertions = [
            _normalize_assertion(assertion) for assertion in assertions
        ]
        json.dump(normalized_assertions, handle, sort_keys=True, indent=2)
        handle.write("\n")

    assertions_by_person, assertions_by_id = _build_assertion_indexes(
        normalized_assertions
    )
    assertions_by_layer, assertions_by_person_by_layer = build_layer_indexes(
        normalized_assertions
    )

    assertions_by_person_path = dist_path / "assertions_by_person.json"
    with assertions_by_person_path.open("w", encoding="utf-8") as handle:
        json.dump(assertions_by_person, handle, sort_keys=True, indent=2)
        handle.write("\n")

    assertions_by_id_path = dist_path / "assertions_by_id.json"
    with assertions_by_id_path.open("w", encoding="utf-8") as handle:
        json.dump(assertions_by_id, handle, sort_keys=True, indent=2)
        handle.write("\n")

    assertions_by_layer_path = dist_path / "assertions_by_layer.json"
    with assertions_by_layer_path.open("w", encoding="utf-8") as handle:
        json.dump(assertions_by_layer, handle, sort_keys=True, indent=2)
        handle.write("\n")

    layers_path = dist_path / "layers.json"
    with layers_path.open("w", encoding="utf-8") as handle:
        json.dump(sorted(assertions_by_layer.keys()), handle, indent=2)
        handle.write("\n")

    layers_meta = _load_layers_meta(
        input_path=input_path, observed_layers=sorted(assertions_by_layer.keys())
    )
    if layers_meta is not None:
        layers_meta_path = dist_path / "layers_meta.json"
        with layers_meta_path.open("w", encoding="utf-8") as handle:
            json.dump(layers_meta, handle, sort_keys=True, indent=2)
            handle.write("\n")

    layer_stats = _build_layer_stats(
        assertions_by_layer=assertions_by_layer,
        assertions_by_person_by_layer=assertions_by_person_by_layer,
        assertions_by_id=assertions_by_id,
    )
    layer_stats_path = dist_path / "layer_stats.json"
    with layer_stats_path.open("w", encoding="utf-8") as handle:
        json.dump(layer_stats, handle, sort_keys=True, indent=2)
        handle.write("\n")

    assertions_by_person_by_layer_path = (
        dist_path / "assertions_by_person_by_layer.json"
    )
    with assertions_by_person_by_layer_path.open("w", encoding="utf-8") as handle:
        json.dump(
            assertions_by_person_by_layer, handle, sort_keys=True, indent=2
        )
        handle.write("\n")
