"""
spec_source_registry.py — Specification source registration and management.

Manages the canonical list of specification sources for all product formats.
Each source has: source_id, format_id, title, source_type, url_or_path,
sha256_snapshot, registered_at, status, fetch_policy.

Storage: .local/spec-source-registry/sources.jsonl (append-only)

Anti-bypass rules:
  - A source must be registered before its URL can be cited in claims.
  - Memory-only sources are not allowed.
  - Raw AI summaries without source_refs are not allowed.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Source types ──────────────────────────────────────────────────────────────
SOURCE_TYPES = [
    "public_spec",          # Official public specification document
    "public_domain_spec",   # Public domain spec (e.g., Netpbm)
    "odf_standard",         # OASIS ODF standard
    "rfc",                  # IETF RFC
    "format_documentation", # Community / vendor documentation
    "local_sample_file",    # Local sample file used for empirical analysis
    "empirical_observation",# Empirical reverse-engineering observation
    "product_policy",       # Internal product policy decision
]

# ── Fetch policies ────────────────────────────────────────────────────────────
FETCH_POLICIES = [
    "fetch_on_register",    # Fetch during registration
    "deferred_local_fixture", # Use local fixture, defer external fetch
    "local_only",           # Local file, no external fetch
    "policy_document",      # Internal policy, no external fetch
]

# ── Source statuses ────────────────────────────────────────────────────────────
SOURCE_STATUSES = [
    "registered",           # Registered, snapshot not yet fetched
    "snapshot_available",   # Snapshot fetched and stored
    "stale",                # Source changed since snapshot
    "fetch_deferred",       # External fetch deferred, local fixture used
    "parse_ready",          # Snapshot parsed
    "index_ready",          # Snapshot indexed
    "digest_ready",         # Digest computed
    "archived",             # Source retired/archived
]


@dataclass
class SpecSource:
    source_id: str
    format_id: str
    title: str
    source_type: str
    url_or_path: str
    registered_at: str
    status: str = "registered"
    sha256_snapshot: Optional[str] = None
    snapshot_path: Optional[str] = None
    fetch_policy: str = "deferred_local_fixture"
    local_fixture_path: Optional[str] = None
    sections_indexed: int = 0
    requirements_extracted: int = 0
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SpecSource":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _registry_path(registry_dir: Optional[str] = None) -> Path:
    base = Path(registry_dir) if registry_dir else Path(".local/spec-source-registry")
    base.mkdir(parents=True, exist_ok=True)
    return base / "sources.jsonl"


def register_source(
    source_id: str,
    format_id: str,
    title: str,
    source_type: str,
    url_or_path: str,
    fetch_policy: str = "deferred_local_fixture",
    local_fixture_path: Optional[str] = None,
    registry_dir: Optional[str] = None,
) -> SpecSource:
    """
    Register a new specification source.
    Appends to the sources.jsonl registry (append-only).
    Returns the created SpecSource.
    """
    if source_type not in SOURCE_TYPES:
        raise ValueError(f"Unknown source_type: {source_type!r}. Valid: {SOURCE_TYPES}")
    if fetch_policy not in FETCH_POLICIES:
        raise ValueError(f"Unknown fetch_policy: {fetch_policy!r}. Valid: {FETCH_POLICIES}")

    source = SpecSource(
        source_id=source_id,
        format_id=format_id,
        title=title,
        source_type=source_type,
        url_or_path=url_or_path,
        registered_at=_now_iso(),
        status="registered",
        fetch_policy=fetch_policy,
        local_fixture_path=local_fixture_path,
    )

    path = _registry_path(registry_dir)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(source.to_dict()) + "\n")

    return source


def load_registry(registry_dir: Optional[str] = None) -> List[SpecSource]:
    """Load all registered sources from the registry."""
    path = _registry_path(registry_dir)
    if not path.exists():
        return []
    sources = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    sources.append(SpecSource.from_dict(json.loads(line)))
                except Exception:
                    pass
    return sources


def get_source(source_id: str, registry_dir: Optional[str] = None) -> Optional[SpecSource]:
    """Look up a source by ID."""
    for s in load_registry(registry_dir):
        if s.source_id == source_id:
            return s
    return None


def list_sources_for_format(format_id: str, registry_dir: Optional[str] = None) -> List[SpecSource]:
    """Return all registered sources for a given format."""
    return [s for s in load_registry(registry_dir) if s.format_id == format_id]


def is_source_registered(source_id: str, registry_dir: Optional[str] = None) -> bool:
    """Check if a source_id exists in the registry."""
    return get_source(source_id, registry_dir) is not None


def validate_citation(source_id: str, registry_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Anti-bypass: validate that a source_id cited in a claim is registered.
    Returns {"valid": True/False, "reason": ...}.
    """
    if not source_id:
        return {"valid": False, "reason": "Empty source_id — memory-only citation not allowed."}
    source = get_source(source_id, registry_dir)
    if source is None:
        return {"valid": False, "reason": f"Source {source_id!r} not found in registry."}
    if source.status == "archived":
        return {"valid": False, "reason": f"Source {source_id!r} is archived."}
    return {"valid": True, "reason": f"Source {source_id!r} is registered ({source.status})."}
