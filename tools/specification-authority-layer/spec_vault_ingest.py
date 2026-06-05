"""
spec_vault_ingest.py — Ingest raw specification snapshots with SHA-256 binding.

Reads a local file (or fixture) and stores a raw snapshot in .local/spec-vault/.
Each snapshot gets a deterministic SHA-256 fingerprint. All downstream artifacts
(parsed content, index, context pack) reference this fingerprint.

If external fetch is unavailable, mark FETCH_DEFERRED_WITH_LOCAL_FIXTURE.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


VAULT_SUBDIR = ".local/spec-vault"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ingest_local_file(
    source_id: str,
    local_path: str,
    vault_dir: Optional[str] = None,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """
    Ingest a local file into the spec vault.
    Returns a snapshot record with sha256, vault_path, ingest status.
    """
    src = Path(local_path)
    if not src.exists():
        return {
            "source_id": source_id,
            "status": "INGEST_FAILED",
            "reason": f"File not found: {local_path}",
        }

    vault = Path(vault_dir) if vault_dir else Path(VAULT_SUBDIR)
    vault.mkdir(parents=True, exist_ok=True)

    sha256 = _sha256_of_file(src)
    snapshot_dir = vault / source_id
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = snapshot_dir / f"{sha256[:16]}{src.suffix or '.bin'}"

    if snapshot_path.exists() and not overwrite:
        return {
            "source_id": source_id,
            "sha256": sha256,
            "vault_path": str(snapshot_path),
            "status": "ALREADY_INGESTED",
            "ingested_at": _now_iso(),
        }

    shutil.copy2(src, snapshot_path)
    meta_path = snapshot_dir / "snapshot-meta.json"
    meta = {
        "source_id": source_id,
        "original_path": str(local_path),
        "sha256": sha256,
        "vault_path": str(snapshot_path),
        "ingested_at": _now_iso(),
        "file_size_bytes": src.stat().st_size,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return {
        "source_id": source_id,
        "sha256": sha256,
        "vault_path": str(snapshot_path),
        "status": "INGESTED",
        "ingested_at": meta["ingested_at"],
    }


def ingest_text_fixture(
    source_id: str,
    content: str,
    label: str = "fixture",
    vault_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Ingest a text fixture (e.g., embedded spec content) into the spec vault.
    Used when external fetch is unavailable.
    Returns snapshot record with sha256.
    """
    data = content.encode("utf-8")
    sha256 = _sha256_of_bytes(data)

    vault = Path(vault_dir) if vault_dir else Path(VAULT_SUBDIR)
    vault.mkdir(parents=True, exist_ok=True)
    snapshot_dir = vault / source_id
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    snapshot_path = snapshot_dir / f"{sha256[:16]}-{label}.txt"
    with open(snapshot_path, "wb") as f:
        f.write(data)

    meta = {
        "source_id": source_id,
        "label": label,
        "sha256": sha256,
        "vault_path": str(snapshot_path),
        "ingested_at": _now_iso(),
        "content_length": len(data),
        "fetch_note": "FETCH_DEFERRED_WITH_LOCAL_FIXTURE",
    }
    meta_path = snapshot_dir / "snapshot-meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    return {
        "source_id": source_id,
        "sha256": sha256,
        "vault_path": str(snapshot_path),
        "status": "INGESTED_FROM_FIXTURE",
        "ingested_at": meta["ingested_at"],
        "fetch_note": "FETCH_DEFERRED_WITH_LOCAL_FIXTURE",
    }


def get_snapshot_meta(source_id: str, vault_dir: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Return snapshot metadata for a source_id, or None if not ingested."""
    vault = Path(vault_dir) if vault_dir else Path(VAULT_SUBDIR)
    meta_path = vault / source_id / "snapshot-meta.json"
    if not meta_path.exists():
        return None
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)


def verify_snapshot_integrity(source_id: str, vault_dir: Optional[str] = None) -> Dict[str, Any]:
    """Re-compute SHA-256 of the stored snapshot and compare to recorded value."""
    meta = get_snapshot_meta(source_id, vault_dir)
    if meta is None:
        return {"source_id": source_id, "status": "NOT_FOUND"}
    vault_path = Path(meta.get("vault_path", ""))
    if not vault_path.exists():
        return {"source_id": source_id, "status": "VAULT_FILE_MISSING", "expected_sha256": meta.get("sha256")}
    actual_sha256 = _sha256_of_file(vault_path)
    expected = meta.get("sha256", "")
    if actual_sha256 == expected:
        return {"source_id": source_id, "status": "INTEGRITY_OK", "sha256": actual_sha256}
    return {
        "source_id": source_id,
        "status": "INTEGRITY_FAIL",
        "expected_sha256": expected,
        "actual_sha256": actual_sha256,
    }
