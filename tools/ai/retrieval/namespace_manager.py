"""Retrieval namespace manager — format-segregated vector store management.

Each format gets its own namespace. Cross-format queries are rejected.
Stale index detection via chunk hash and model fingerprint tracking.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class IndexManifest:
    """Manifest for a format's vector store index."""
    format_id: str
    embedding_model_id: str = ""
    embedding_model_fingerprint: str = ""
    chunk_count: int = 0
    chunk_hashes: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    manifest_hash: str = ""

    def compute_hash(self) -> str:
        raw = f"{self.format_id}|{self.embedding_model_fingerprint}|{'|'.join(sorted(self.chunk_hashes))}"
        self.manifest_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return self.manifest_hash

    def to_dict(self) -> dict[str, Any]:
        return {
            "format_id": self.format_id,
            "embedding_model_id": self.embedding_model_id,
            "embedding_model_fingerprint": self.embedding_model_fingerprint,
            "chunk_count": self.chunk_count,
            "chunk_hashes": self.chunk_hashes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "manifest_hash": self.manifest_hash,
        }


@dataclass
class RetrievalAuditEntry:
    """Audit log entry for a retrieval operation."""
    timestamp: str = ""
    format_id: str = ""
    query_hash: str = ""
    results_count: int = 0
    model_id: str = ""
    status: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "format_id": self.format_id,
            "query_hash": self.query_hash,
            "results_count": self.results_count,
            "model_id": self.model_id,
            "status": self.status,
        }


class CrossNamespaceError(Exception):
    """Raised when a cross-format retrieval is attempted without authorization."""
    pass


class StaleIndexError(Exception):
    """Raised when an index is detected as stale."""
    pass


class MissingEmbeddingModelError(Exception):
    """Raised when no embedding model is available."""
    pass


_SAFE_FORMAT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$")


def validate_format_id(format_id: str) -> None:
    """Validate format_id is safe for filesystem use. Raises ValueError if not."""
    if not format_id:
        raise ValueError("format_id must not be empty")
    if ".." in format_id or "/" in format_id or "\\" in format_id:
        raise ValueError(f"format_id contains path traversal characters: {format_id!r}")
    if not _SAFE_FORMAT_ID_PATTERN.match(format_id):
        raise ValueError(f"format_id contains unsafe characters: {format_id!r}")


class NamespaceManager:
    """Manages format-segregated vector store namespaces."""

    def __init__(self, store_root: Path | None = None):
        self._store_root = store_root or Path(".local/ai/vector-stores")
        self._manifests: dict[str, IndexManifest] = {}
        self._audit_log: list[RetrievalAuditEntry] = []

    def get_namespace_path(self, format_id: str) -> Path:
        validate_format_id(format_id)
        return self._store_root / format_id

    def namespace_exists(self, format_id: str) -> bool:
        ns_path = self.get_namespace_path(format_id)
        return ns_path.exists() and (ns_path / "manifest.json").exists()

    def create_namespace(self, format_id: str, manifest: IndexManifest) -> Path:
        ns_path = self.get_namespace_path(format_id)
        ns_path.mkdir(parents=True, exist_ok=True)
        manifest.created_at = datetime.now(timezone.utc).isoformat()
        manifest.updated_at = manifest.created_at
        manifest.compute_hash()
        self._manifests[format_id] = manifest
        manifest_path = ns_path / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest.to_dict(), f, indent=2)
        return ns_path

    def load_manifest(self, format_id: str) -> IndexManifest | None:
        if format_id in self._manifests:
            return self._manifests[format_id]
        manifest_path = self.get_namespace_path(format_id) / "manifest.json"
        if not manifest_path.exists():
            return None
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        manifest = IndexManifest(**data)
        self._manifests[format_id] = manifest
        return manifest

    def detect_stale_index(
        self,
        format_id: str,
        current_chunk_hashes: list[str],
        current_model_fingerprint: str,
    ) -> tuple[bool, str]:
        """Check if a namespace's index is stale.

        Returns (is_stale, reason).
        """
        manifest = self.load_manifest(format_id)
        if manifest is None:
            return True, "no_manifest"
        if set(manifest.chunk_hashes) != set(current_chunk_hashes):
            return True, "chunk_hashes_changed"
        if manifest.embedding_model_fingerprint != current_model_fingerprint:
            return True, "embedding_model_changed"
        return False, "up_to_date"

    def query(
        self,
        format_id: str,
        query_text: str,
    ) -> list[dict[str, Any]]:
        """Query a format's vector store.

        Cross-format queries are always forbidden (use reject_cross_namespace_query).
        This is a stub — real implementation requires LanceDB.
        """
        if not self.namespace_exists(format_id):
            raise MissingEmbeddingModelError(
                f"No vector store index for format '{format_id}'"
            )

        query_hash = hashlib.sha256(query_text.encode()).hexdigest()[:16]

        entry = RetrievalAuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            format_id=format_id,
            query_hash=query_hash,
            results_count=0,
            status="fixture_mode",
        )
        self._audit_log.append(entry)

        return []

    def reject_cross_namespace_query(
        self,
        source_format: str,
        target_format: str,
    ) -> None:
        """Reject a cross-namespace query attempt."""
        raise CrossNamespaceError(
            f"Cross-format retrieval from '{source_format}' to '{target_format}' "
            f"is forbidden without explicit authorization."
        )

    def get_audit_log(self) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self._audit_log]
