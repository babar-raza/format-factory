"""Volatile-state registry accessor for the Format Contract Layer (L30).

registry/format-contract-registry.yaml carries everything time- or
run-dependent (timestamps, scores, freshness, review verdicts, blocked
states) so canonical contract bodies stay byte-comparable. This module NEVER
touches shared/format-contracts/{fmt}.yaml bodies.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_PATH = REPO_ROOT / "registry" / "format-contract-registry.yaml"

VALID_STATES = {
    "COMPILED",
    "VALIDATED",
    "REVIEWED",
    "BLOCKED_NEEDS_AUTHORITY",
    "STALE",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_registry() -> dict:
    if not REGISTRY_PATH.is_file():
        return {"schema_version": "1.0", "contracts": []}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    data.setdefault("schema_version", "1.0")
    data.setdefault("contracts", [])
    return data


def get_entry(format_id: str) -> dict | None:
    for entry in read_registry()["contracts"]:
        if entry.get("format_id") == format_id:
            return entry
    return None


def update_entry(format_id: str, **fields) -> dict:
    """Create or update the volatile entry for a format; returns the entry."""
    state = fields.get("state")
    if state is not None and state not in VALID_STATES:
        raise ValueError(f"invalid registry state: {state}")
    data = read_registry()
    entry = None
    for candidate in data["contracts"]:
        if candidate.get("format_id") == format_id:
            entry = candidate
            break
    if entry is None:
        entry = {"format_id": format_id}
        data["contracts"].append(entry)
    entry.update(fields)
    entry["updated_at"] = _now()
    data["contracts"].sort(key=lambda e: e.get("format_id", ""))
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "w", encoding="utf-8", newline="\n") as fh:
        yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True, width=100)
    return entry
