"""Staleness and contradiction detection for the control index."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def check_staleness(conn: sqlite3.Connection, repo_root: Path) -> list[dict]:
    """Check source_manifest entries against current file state.

    Returns list of stale sources with details.
    """
    stale = []
    rows = conn.execute("SELECT * FROM source_manifest").fetchall()
    now = datetime.now(timezone.utc)
    for row in rows:
        source_path = row["source_path"]
        abs_path = repo_root / source_path
        if not abs_path.exists():
            stale.append({
                "source_path": source_path,
                "entity_type": row["entity_type"],
                "issue": "file_missing",
                "last_ingested": row["last_ingested"],
            })
            continue

        try:
            import hashlib
            current_hash = hashlib.sha256(abs_path.read_bytes()).hexdigest()
            if current_hash != row["last_hash"]:
                stale.append({
                    "source_path": source_path,
                    "entity_type": row["entity_type"],
                    "issue": "hash_mismatch",
                    "last_ingested": row["last_ingested"],
                })
        except OSError:
            pass
    return stale


def detect_contradictions(conn: sqlite3.Connection) -> list[dict]:
    """Detect logical contradictions across entity tables.

    Returns list of {type, entity_id, description}.
    """
    contradictions = []

    # Gaps closed without any sprint work items referencing them
    rows = conn.execute("""
        SELECT g.gap_id FROM gaps g
        WHERE g.status = 'closed'
          AND g.gap_id NOT IN (SELECT gap_ledger_ref FROM sprint_work_items WHERE gap_ledger_ref IS NOT NULL)
    """).fetchall()
    for r in rows:
        contradictions.append({
            "type": "closed_gap_no_evidence",
            "entity_id": r["gap_id"],
            "description": f"Gap {r['gap_id']} is closed but has no sprint work items referencing it",
        })

    # Unresolved failures with high occurrence count
    rows = conn.execute("""
        SELECT failure_id, occurrence_count FROM failures
        WHERE resolved = 0 AND occurrence_count > 5
    """).fetchall()
    for r in rows:
        contradictions.append({
            "type": "recurring_unresolved_failure",
            "entity_id": r["failure_id"],
            "description": f"Failure {r['failure_id']} is unresolved with {r['occurrence_count']} occurrences",
        })

    return contradictions


def detect_orphans(conn: sqlite3.Connection) -> list[dict]:
    """Detect orphaned references across tables."""
    orphans = []

    # sprint_work_items referencing non-existent gaps
    rows = conn.execute("""
        SELECT DISTINCT swi.gap_ledger_ref FROM sprint_work_items swi
        WHERE swi.gap_ledger_ref IS NOT NULL
          AND swi.gap_ledger_ref NOT IN (SELECT gap_id FROM gaps)
    """).fetchall()
    for r in rows:
        orphans.append({
            "type": "orphan_gap_ref",
            "entity_id": r["gap_ledger_ref"],
            "description": f"Sprint work item references non-existent gap {r['gap_ledger_ref']}",
        })

    return orphans
