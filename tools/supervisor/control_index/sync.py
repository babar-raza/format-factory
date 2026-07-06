"""Sync orchestrator for the control index.

Manages incremental and full rebuild sync from source files to SQLite.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .db import ensure_db, get_connection, init_db


@dataclass
class IngestResult:
    """Result from a single ingestor sync."""
    entity_type: str
    inserted: int = 0
    deleted: int = 0
    skipped: bool = False
    error: str | None = None

    def to_dict(self) -> dict:
        d = {"entity_type": self.entity_type, "inserted": self.inserted, "deleted": self.deleted}
        if self.skipped:
            d["skipped"] = True
        if self.error:
            d["error"] = self.error
        return d


@dataclass
class SyncReport:
    """Aggregate report from a full sync run."""
    results: list[IngestResult] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""

    def add(self, result: IngestResult):
        self.results.append(result)

    def to_dict(self) -> dict:
        return {
            "action": "sync",
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_inserted": sum(r.inserted for r in self.results),
            "total_skipped": sum(1 for r in self.results if r.skipped),
            "total_errors": sum(1 for r in self.results if r.error),
            "results": [r.to_dict() for r in self.results],
        }


def get_manifest_row(conn, source_path: str) -> dict | None:
    """Query source_manifest for an existing entry."""
    row = conn.execute(
        "SELECT * FROM source_manifest WHERE source_path = ?",
        (source_path,),
    ).fetchone()
    return dict(row) if row else None


def update_manifest(conn, source_path: str, entity_type: str,
                    file_hash: str, row_count: int, file_size: int):
    """Insert or replace a source_manifest entry."""
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """INSERT OR REPLACE INTO source_manifest
           (source_path, entity_type, last_hash, last_ingested, last_modified, row_count, file_size)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (source_path, entity_type, file_hash, now, now, row_count, file_size),
    )


# Registry of all ingestors in dependency order.
# Populated by register_ingestor() calls in ingestor modules.
ALL_INGESTORS: list[type] = []


def register_ingestor(cls):
    """Decorator to register an ingestor class."""
    if cls not in ALL_INGESTORS:
        ALL_INGESTORS.append(cls)
    return cls


# Import all ingestors so @register_ingestor decorators fire.
# Order matters: these are registered in dependency order.
from .ingestors import format_ingestor      # noqa: F401, E402
from .ingestors import capability_ingestor  # noqa: F401, E402
from .ingestors import skill_ingestor       # noqa: F401, E402
from .ingestors import layer_ingestor       # noqa: F401, E402
from .ingestors import failure_ingestor     # noqa: F401, E402
from .ingestors import plan_lock_ingestor   # noqa: F401, E402
from .ingestors import violation_ingestor   # noqa: F401, E402
from .ingestors import gap_ingestor        # noqa: F401, E402
from .ingestors import qname_ingestor      # noqa: F401, E402
from .ingestors import evidence_ingestor   # noqa: F401, E402
from .ingestors import event_ingestor      # noqa: F401, E402
# TC-BF-006: Invocation graph ingestors (subprocess calls, claude commands, skill registry)
from .ingestors import subprocess_calls_ingestor   # noqa: F401, E402
from .ingestors import command_invocations_ingestor  # noqa: F401, E402
from .ingestors import skill_invocations_ingestor   # noqa: F401, E402


def sync_all(db_path: Path, repo_root: Path, *, force: bool = False) -> SyncReport:
    """Run incremental sync for all registered ingestors.

    Args:
        db_path: Path to SQLite database
        repo_root: Repository root directory
        force: If True, re-sync all sources regardless of hash
    """
    report = SyncReport(started_at=datetime.now(timezone.utc).isoformat())
    conn = ensure_db(db_path)
    try:
        for ingestor_cls in ALL_INGESTORS:
            ingestor = ingestor_cls(conn, repo_root)
            try:
                result = ingestor.sync(force=force)
                report.add(result)
            except Exception as e:
                report.add(IngestResult(
                    entity_type=ingestor.entity_type,
                    error=str(e),
                ))
        # Populate FTS5 index if any ingestors actually inserted data
        if any(r.inserted > 0 for r in report.results):
            try:
                from .search import populate_fts
                populate_fts(conn)
            except Exception:
                pass  # FTS population is best-effort
        conn.commit()
    finally:
        report.completed_at = datetime.now(timezone.utc).isoformat()
        conn.close()
    return report


def rebuild(db_path: Path, repo_root: Path) -> SyncReport:
    """Delete and rebuild the database from scratch."""
    if db_path.exists():
        db_path.unlink()
        # Also remove WAL and SHM files if they exist
        wal = db_path.with_suffix(".db-wal")
        shm = db_path.with_suffix(".db-shm")
        if wal.exists():
            wal.unlink()
        if shm.exists():
            shm.unlink()
    init_db(db_path)
    return sync_all(db_path, repo_root, force=True)
