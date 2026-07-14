"""Gap selection utilities — query gap_attempts to identify exhausted gaps.

TC-OCRD-A1-03: Provides functions to prevent the loop from re-selecting gaps
that have already failed max_failed_attempts times.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def classify_outcome(status: str | None) -> str:
    """Map work-item status string to a gap_attempts outcome value.

    TC-OCRD-A1-05: Canonical outcome values: closed, failed, partial, rework.
    """
    if not status:
        return "partial"
    s = status.lower()
    if s in ("completed", "done", "closed", "verified", "complete"):
        return "closed"
    if s in ("failed", "fail", "error"):
        return "failed"
    if s in ("rework", "rework_required", "needs_rework"):
        return "rework"
    return "partial"


def get_exhausted_gaps(
    conn: sqlite3.Connection,
    max_failed_attempts: int = 3,
) -> set[str]:
    """Return gap_ids with >= max_failed_attempts 'failed' or 'rework' outcomes.

    Args:
        conn: Open SQLite connection to control-index.db.
        max_failed_attempts: Threshold for exhaustion (default 3, from policies.yaml).

    Returns:
        Set of gap_id strings that have reached the failure threshold.
    """
    rows = conn.execute(
        """SELECT gap_id, COUNT(*) as cnt
           FROM gap_attempts
           WHERE outcome IN ('failed', 'rework')
           GROUP BY gap_id
           HAVING cnt >= ?""",
        (max_failed_attempts,),
    ).fetchall()
    return {row[0] for row in rows}


def get_recent_attempt(conn: sqlite3.Connection, gap_id: str) -> dict | None:
    """Return the most recent attempt record for a gap_id, or None if none exists.

    Args:
        conn: Open SQLite connection.
        gap_id: The gap identifier to query.

    Returns:
        Dict with attempt fields, or None if no attempts recorded.
    """
    row = conn.execute(
        """SELECT * FROM gap_attempts WHERE gap_id = ?
           ORDER BY attempted_at DESC LIMIT 1""",
        (gap_id,),
    ).fetchone()
    if row is None:
        return None
    return dict(row)


def write_exhausted_gaps_json(
    conn: sqlite3.Connection,
    output_path: Path,
    max_failed_attempts: int = 3,
) -> int:
    """Write exhausted gap IDs to a machine-readable JSON file.

    Args:
        conn: Open SQLite connection.
        output_path: Path to write the JSON file (REQ-OCRD-013).
        max_failed_attempts: Failure threshold (from policies.yaml gap_selection section).

    Returns:
        Count of exhausted gaps written.
    """
    exhausted = sorted(get_exhausted_gaps(conn, max_failed_attempts))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "exhausted_gaps": exhausted,
                "max_failed_attempts": max_failed_attempts,
                "count": len(exhausted),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return len(exhausted)
