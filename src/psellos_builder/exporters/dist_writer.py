"""Write compiled artifacts into the dist/ directory."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_dist(
    *, dist_path: Path, manifest: dict[str, Any], dataset: dict[str, Any]
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
        json.dump(dataset.get("assertions", []), handle, sort_keys=True, indent=2)
        handle.write("\n")
