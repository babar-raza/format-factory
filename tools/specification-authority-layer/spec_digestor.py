"""
spec_digestor.py — Compute stable digests/fingerprints for spec artifacts.

Computes a deterministic digest of the full normalized artifact (sections only,
not timestamps) so downstream artifacts can detect spec source changes.

Storage: .local/spec-artifacts/{source_id}-digest.json
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_digest_of_sections(sections: list) -> str:
    """
    Compute a stable SHA-256 digest of the sections list.
    Uses section content only (not timestamps).
    """
    stable_parts = []
    for s in sorted(sections, key=lambda x: x.get("section_id", "")):
        stable_parts.append(f"{s['section_id']}:{s['heading']}:{s['content'][:200]}")
    digest_input = "\n".join(stable_parts).encode("utf-8")
    return hashlib.sha256(digest_input).hexdigest()


@dataclass
class SpecDigest:
    source_id: str
    sha256_snapshot: str
    content_digest: str
    sections_count: int
    digest_path: Optional[str] = None
    digested_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "sha256_snapshot": self.sha256_snapshot,
            "content_digest": self.content_digest,
            "sections_count": self.sections_count,
            "digest_path": self.digest_path,
            "digested_at": self.digested_at,
        }


def compute_digest(
    source_id: str,
    sha256_snapshot: str,
    normalized_artifact: Dict[str, Any],
    artifacts_dir: Optional[str] = None,
) -> SpecDigest:
    """
    Compute and store a stable content digest for a normalized artifact.
    """
    art_root = Path(artifacts_dir) if artifacts_dir else Path(".local/spec-artifacts")
    art_root.mkdir(parents=True, exist_ok=True)

    sections = normalized_artifact.get("sections", [])
    content_digest = _stable_digest_of_sections(sections)

    digest_doc = {
        "source_id": source_id,
        "sha256_snapshot": sha256_snapshot,
        "content_digest": content_digest,
        "sections_count": len(sections),
        "digested_at": _now_iso(),
    }

    digest_path = art_root / f"{source_id}-digest.json"
    with open(digest_path, "w", encoding="utf-8") as f:
        json.dump(digest_doc, f, indent=2)

    return SpecDigest(
        source_id=source_id,
        sha256_snapshot=sha256_snapshot,
        content_digest=content_digest,
        sections_count=len(sections),
        digest_path=str(digest_path),
        digested_at=digest_doc["digested_at"],
    )


def load_digest(source_id: str, artifacts_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Load the stored digest for a source."""
    art_root = Path(artifacts_dir) if artifacts_dir else Path(".local/spec-artifacts")
    digest_path = art_root / f"{source_id}-digest.json"
    if not digest_path.exists():
        return None
    with open(digest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_staleness(
    source_id: str,
    current_sha256: str,
    artifacts_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Check if downstream artifacts are stale (source snapshot changed).
    Returns {"stale": True/False, "reason": ...}.
    """
    digest = load_digest(source_id, artifacts_dir)
    if digest is None:
        return {"stale": True, "reason": "No digest found — not yet processed."}
    stored_sha256 = digest.get("sha256_snapshot", "")
    if stored_sha256 != current_sha256:
        return {
            "stale": True,
            "reason": f"SHA256 changed: stored={stored_sha256[:16]}... current={current_sha256[:16]}...",
        }
    return {"stale": False, "reason": "Digest matches current snapshot."}
