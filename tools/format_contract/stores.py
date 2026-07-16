"""Committed-store access for the Format Contract Layer (L30).

Loads the hash-bound canonical inputs of contract compilation:
SAL facts, research findings, family packs, shared library contract,
fact-category requirements, and the format registry entry. Computes the
input_digests block that pins a compiled contract to its exact inputs.

The reference contract file (plans/from_chat/...) is DENYLISTED as an input:
it is a comparison oracle only (DEC-038). load-* helpers refuse it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from canonical_io import digest_file, load_yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

SAL_FACTS_DIR = REPO_ROOT / "shared" / "sal-facts"
CONTRACTS_DIR = REPO_ROOT / "shared" / "format-contracts"
RESEARCH_DIR = CONTRACTS_DIR / "research"
POLICY_DIR = CONTRACTS_DIR / "policy"
FAMILY_PACKS_DIR = POLICY_DIR / "family-packs"
FORMAT_REGISTRY = REPO_ROOT / "registry" / "format-registry.yaml"
QNAME_REGISTRY_DIR = REPO_ROOT / "shared" / "qname-registry"

# DEC-038: comparison oracle only; never a generation input.
INPUT_DENYLIST_PARTS = ("plans/from_chat",)


class StoreError(RuntimeError):
    """Raised for missing/invalid stores or denylisted input paths."""


def _check_denylist(path: Path) -> None:
    normalized = str(path).replace("\\", "/")
    for part in INPUT_DENYLIST_PARTS:
        if part in normalized:
            raise StoreError(
                f"DENYLISTED input path (comparison oracle only, DEC-038): {path}"
            )


def sal_facts_path(format_id: str) -> Path:
    return SAL_FACTS_DIR / f"{format_id}.yaml"


def research_path(format_id: str) -> Path:
    return RESEARCH_DIR / f"{format_id}.yaml"


def contract_path(format_id: str) -> Path:
    return CONTRACTS_DIR / f"{format_id}.yaml"


def family_pack_path(family: str) -> Path:
    return FAMILY_PACKS_DIR / f"{family}.yaml"


def load_sal_facts(format_id: str) -> dict:
    path = sal_facts_path(format_id)
    _check_denylist(path)
    data = load_yaml(path)
    if not data or not isinstance(data.get("facts"), list):
        raise StoreError(f"SAL fact store missing or empty: {path}")
    return data


def load_research(format_id: str) -> dict:
    """Research findings store; absent store -> empty findings (valid state)."""
    path = research_path(format_id)
    _check_denylist(path)
    data = load_yaml(path)
    if data is None:
        return {"format_id": format_id, "findings": [], "source_records": []}
    data.setdefault("findings", [])
    data.setdefault("source_records", [])
    return data


def load_family_map() -> dict[str, str]:
    data = load_yaml(POLICY_DIR / "format-family-map.yaml")
    if not data or "map" not in data:
        raise StoreError("format-family-map.yaml missing or invalid")
    return data["map"]


def load_family_pack(family: str) -> dict:
    data = load_yaml(family_pack_path(family))
    if not data or data.get("family") != family:
        raise StoreError(f"family pack missing or family mismatch: {family}")
    return data


def load_shared_contract() -> dict:
    data = load_yaml(POLICY_DIR / "shared-library-contract.yaml")
    if not data or "groups" not in data:
        raise StoreError("shared-library-contract.yaml missing or invalid")
    return data


def load_fact_categories() -> dict:
    data = load_yaml(POLICY_DIR / "fact-category-requirements.yaml")
    if not data or "categories" not in data or "families" not in data:
        raise StoreError("fact-category-requirements.yaml missing or invalid")
    return data


def load_quality_policy() -> dict:
    data = load_yaml(POLICY_DIR / "quality-policy.yaml")
    if not data or "shallow_phrases" not in data:
        raise StoreError("quality-policy.yaml missing or invalid")
    return data


_registry_cache: dict | None = None


def load_format_registry_entry(format_id: str) -> dict:
    """Entry from registry/format-registry.yaml (case-insensitive format_id)."""
    global _registry_cache
    if _registry_cache is None:
        _registry_cache = load_yaml(FORMAT_REGISTRY) or {}
    formats = _registry_cache.get("formats") or []
    for entry in formats:
        if str(entry.get("format_id", "")).lower() == format_id.lower():
            return entry
    return {}


def input_digests(format_id: str, family: str) -> dict:
    """The digest block pinning a contract to its exact committed inputs."""
    qname_path = QNAME_REGISTRY_DIR / f"{format_id}.yaml"
    digests = {
        "sal_facts_sha256": digest_file(sal_facts_path(format_id)),
        "research_sha256": digest_file(research_path(format_id)),
        "family_pack_sha256": digest_file(family_pack_path(family)),
        "shared_contract_sha256": digest_file(POLICY_DIR / "shared-library-contract.yaml"),
        "fact_categories_sha256": digest_file(POLICY_DIR / "fact-category-requirements.yaml"),
    }
    if qname_path.is_file():
        digests["qname_registry_sha256"] = digest_file(qname_path)
    return digests


def resolve_provenance_id(pid: str, format_id: str) -> bool:
    """True if a provenance ID resolves against committed stores."""
    if pid.startswith("SAL-"):
        facts = load_sal_facts(format_id).get("facts", [])
        return any(f.get("fact_id") == pid for f in facts)
    if pid.startswith("RF-"):
        findings = load_research(format_id).get("findings", [])
        return any(f.get("finding_id") == pid for f in findings)
    if pid.startswith("POL-"):
        ids: set[str] = set()
        shared = load_shared_contract()
        for group in shared.get("groups", {}).values():
            for item in group.get("items", []):
                ids.add(item["id"])
        family_map = load_family_map()
        family = family_map.get(format_id)
        if family:
            pack = load_family_pack(family)
            for dom in pack.get("domains", []):
                for item in dom.get("baseline_behavior", []):
                    ids.add(item["id"])
        return pid in ids
    return False
