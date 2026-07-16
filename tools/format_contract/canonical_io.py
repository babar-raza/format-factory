"""Canonical YAML serialization for Format Contract Layer stores.

Guarantees: identical data -> byte-identical output. No volatile fields are
added here; callers must keep timestamps out of canonical bodies (they belong
in registry/format-contract-registry.yaml). Digests normalize line endings to
LF so CRLF checkouts do not change input_digests.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

# Known-field display order. Unknown keys sort alphabetically after ranked ones.
_KEY_PRIORITY: dict[str, int] = {
    # document top level
    "contract_metadata": 0, "format_identity": 1, "authoritative_sources": 2,
    "scope_policy": 3, "capabilities": 4, "public_api_contract": 5,
    "preservation_contract": 6, "validation_contract": 7, "security_contract": 8,
    "performance_contract": 9, "test_contract": 10, "release_gates": 11,
    "coverage_map": 12,
    # metadata
    "schema_version": 20, "contract_id": 21, "format_id": 22,
    "format_canonical_name": 23, "aliases": 24, "extensions": 25,
    "mime_types": 26, "family": 27, "target_spec_version": 28,
    "compatible_versions": 29, "source_authority_status": 30,
    "generator_version": 31, "lifecycle_status": 32, "confidence": 33,
    "unresolved_questions": 34, "supersedes": 35, "input_digests": 36,
    # capability
    "capability_id": 40, "level": 41, "category": 42, "title": 43,
    "production_meaning": 44, "developer_use_case": 45, "provenance": 46,
    "required_behavior": 47, "normative_rules": 47.5, "required_model_objects": 48,
    "required_operations": 49, "required_invariants": 50,
    "preservation_rules": 51, "validation_rules": 52,
    "security_requirements": 53, "performance_requirements": 54,
    "error_behavior": 55, "compatibility_expectations": 56,
    "depth_required": 57, "depth_rationale": 58, "required_tests": 59,
    "required_oracle_evidence": 60, "release_gates_capability": 61,
    # sources
    "source_id": 70, "organization": 72, "version": 73,
    "publication_date": 74, "local_path": 75, "canonical_url": 76,
    "content_hash": 77, "authority_class": 78, "relevant_sections": 79,
    "licensing": 80, "acquisition_status": 81,
}


def _order(value: Any) -> Any:
    """Recursively impose canonical key order on mappings; keep list order."""
    if isinstance(value, dict):
        keys = sorted(value.keys(), key=lambda k: (_KEY_PRIORITY.get(k, 1000), str(k)))
        return {k: _order(value[k]) for k in keys}
    if isinstance(value, list):
        return [_order(v) for v in value]
    return value


def canonical_dump(data: dict) -> str:
    """Serialize to canonical YAML text (LF endings, ordered keys, no aliases)."""

    class _Dumper(yaml.SafeDumper):
        def ignore_aliases(self, _data: Any) -> bool:  # noqa: D401
            return True

    text = yaml.dump(
        _order(data),
        Dumper=_Dumper,
        sort_keys=False,
        allow_unicode=True,
        width=100,
        default_flow_style=False,
    )
    return text.replace("\r\n", "\n")


def canonical_write(path: Path, data: dict) -> str:
    """Write canonical YAML with LF endings; returns the text written."""
    text = canonical_dump(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return text


def load_yaml(path: Path) -> Any:
    """Load YAML; returns None for a missing file."""
    if not Path(path).is_file():
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def digest_text(text: str) -> str:
    """SHA-256 of LF-normalized text."""
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def digest_file(path: Path) -> str:
    """SHA-256 of a file's LF-normalized text; missing file -> digest of empty."""
    p = Path(path)
    if not p.is_file():
        return hashlib.sha256(b"").hexdigest()
    return digest_text(p.read_text(encoding="utf-8", errors="replace"))
