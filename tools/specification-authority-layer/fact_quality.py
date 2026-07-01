"""Fact quality contract for the Specification Authority Layer.

Defines quality levels (0-3) for spec facts and enforcement thresholds
per declaration item_type. Used by V47 and validate_spec_fact_refs to
enforce that higher-authority declarations cite higher-quality facts.

Quality levels:
  0 — bootstrap_only: source_id is null or unregistered
  1 — source_registered: source_id points to a registered spec source
  2 — text_verified: fact text confirmed against normalized spec text
  3 — normative_verified: Level 2 + RFC 2119 keyword in normative section
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Set

_REPO_ROOT = Path(__file__).resolve().parents[2]

QUALITY_LEVELS = {
    "bootstrap_only": 0,
    "source_registered": 1,
    "verified": 2,
    "text_verified": 2,
    "normative_verified": 3,
}

ITEM_TYPE_THRESHOLDS = {
    "PRODUCT_SOURCE": 0,
    "PRODUCT_TEST": 0,
    "GOVERNANCE_TASKCARD": 0,
    "READINESS": 1,
    "RELEASE_GATE": 2,
}


def quality_level(fact: dict, registered_source_ids: Set[str]) -> int:
    """Return the quality level (0-3) of a fact dict.

    Parameters
    ----------
    fact : dict
        A fact record with at least ``source_id`` and ``fact_status`` keys.
    registered_source_ids : set of str
        Source IDs known to be registered in spec-source-registry/sources.jsonl.
    """
    source_id = fact.get("source_id")
    fact_status = fact.get("fact_status", "bootstrap_only")

    if source_id is None:
        return 0
    if source_id not in registered_source_ids:
        return 0
    level = QUALITY_LEVELS.get(fact_status, 0)
    if level >= 1:
        return level
    # source_id is registered but fact_status is bootstrap_only → Level 1
    return 1


def load_registered_source_ids(
    repo_root: Optional[Path] = None,
) -> Set[str]:
    """Load all source_ids from spec-source-registry/sources.jsonl and committed aliases.

    Merges two sources:
    1. .local/spec-source-registry/sources.jsonl — formal SPEC-* IDs (gitignored, may be absent)
    2. shared/sal-source-id-aliases.yaml — informal IDs used by the SAL extraction pipeline
       (committed, always present, ensures quality level computation works on fresh checkout)
    """
    root = repo_root or _REPO_ROOT
    ids: Set[str] = set()

    # Source 1: gitignored formal registry (SPEC-FODS-1_3, SPEC-ZST-RFC8878, etc.)
    sources_path = root / ".local" / "spec-source-registry" / "sources.jsonl"
    if sources_path.exists():
        try:
            for line in sources_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                sid = entry.get("source_id", "")
                if sid:
                    ids.add(sid)
        except Exception:
            pass

    # Source 2: committed aliases (odf-1.3-part3, fods-normalized, etc.)
    aliases_path = root / "shared" / "sal-source-id-aliases.yaml"
    if aliases_path.exists():
        try:
            import yaml as _yaml  # type: ignore[import]
            data = _yaml.safe_load(aliases_path.read_text(encoding="utf-8")) or {}
            for sid in data.get("source_ids", []):
                if sid:
                    ids.add(str(sid))
        except Exception:
            pass

    return ids


def build_fact_quality_index(
    sal_facts_path: Optional[Path] = None,
    repo_root: Optional[Path] = None,
) -> Dict[str, dict]:
    """Build a {qname: {quality, fact_status, source_id}} index from sal-facts-latest.json.

    This is the single-point-of-truth index used by V47 and V13 to evaluate
    fact quality for governance enforcement.
    """
    root = repo_root or _REPO_ROOT
    path = sal_facts_path or (root / ".local" / "sal-output" / "sal-facts-latest.json")
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    registered = load_registered_source_ids(repo_root=root)
    index: Dict[str, dict] = {}
    for result in data.get("results", []):
        for fact in result.get("spec_facts", []):
            qname = fact.get("qname")
            if not qname:
                continue
            index[qname] = {
                "quality": quality_level(fact, registered),
                "fact_status": fact.get("fact_status", "bootstrap_only"),
                "source_id": fact.get("source_id"),
                "format_id": result.get("format_id", ""),
            }
    return index


def check_fact_quality_for_item(
    spec_fact_refs: list,
    item_type: str,
    fact_index: Dict[str, dict],
) -> list:
    """Check whether cited facts meet the quality threshold for the given item_type.

    Returns a list of violation strings (empty = all OK).
    """
    threshold = ITEM_TYPE_THRESHOLDS.get(item_type, 0)
    violations = []
    for ref in spec_fact_refs:
        entry = fact_index.get(ref)
        if entry is None:
            violations.append(f"{ref}: not found in sal-facts-latest.json")
        elif entry["quality"] < threshold:
            violations.append(
                f"{ref}: quality={entry['quality']} < {threshold} "
                f"required for {item_type} "
                f"(fact_status={entry['fact_status']})"
            )
    return violations
