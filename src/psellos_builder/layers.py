"""Layer helpers for narrative assertions."""
from __future__ import annotations

from typing import Any


def get_layer(assertion: dict[str, Any]) -> str:
    """Return the narrative layer for an assertion (defaulting to canon)."""
    extensions = assertion.get("extensions")
    if isinstance(extensions, dict):
        psellos = extensions.get("psellos")
        if isinstance(psellos, dict):
            layer = psellos.get("layer")
            if isinstance(layer, str) and layer:
                return layer
    return "canon"


def build_assertions_by_layer(
    assertions: list[dict[str, Any]],
) -> dict[str, list[str]]:
    """Return assertion ids grouped by layer."""
    assertions_by_layer: dict[str, set[str]] = {}
    for assertion in assertions:
        assertion_id = assertion.get("id")
        if not isinstance(assertion_id, str):
            continue
        layer = get_layer(assertion)
        assertions_by_layer.setdefault(layer, set()).add(assertion_id)
    return {
        layer: sorted(assertions_by_layer[layer])
        for layer in sorted(assertions_by_layer)
    }


def build_layer_indexes(
    assertions: list[dict[str, Any]],
) -> tuple[dict[str, list[str]], dict[str, dict[str, list[str]]]]:
    """Return layer and person-by-layer indexes for normalized assertions."""
    assertions_by_layer = build_assertions_by_layer(assertions)
    assertions_by_person_by_layer: dict[str, dict[str, set[str]]] = {}
    for assertion in assertions:
        assertion_id = assertion.get("id")
        if not isinstance(assertion_id, str):
            continue
        layer = get_layer(assertion)
        if "subject" in assertion:
            _add_to_person_layer_index(
                assertions_by_person_by_layer, assertion["subject"], layer, assertion_id
            )
        if "object" in assertion:
            _add_to_person_layer_index(
                assertions_by_person_by_layer, assertion["object"], layer, assertion_id
            )
    sorted_by_person_by_layer = {
        person_id: {
            layer: sorted(assertion_ids)
            for layer, assertion_ids in layers.items()
        }
        for person_id, layers in assertions_by_person_by_layer.items()
    }
    return assertions_by_layer, sorted_by_person_by_layer


def _add_to_person_layer_index(
    index: dict[str, dict[str, set[str]]],
    person_id: str,
    layer: str,
    assertion_id: str,
) -> None:
    index.setdefault(person_id, {}).setdefault(layer, set()).add(assertion_id)
