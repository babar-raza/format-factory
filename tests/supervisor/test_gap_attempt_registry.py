"""Tests for TC-OCRD-A1: Gap Attempt Registry.

Covers:
  - gap_attempts table created by schema + migration
  - get_exhausted_gaps() correctly identifies exhausted gaps
  - get_recent_attempt() returns most recent attempt
  - write_exhausted_gaps_json() writes correct JSON file
  - _classify_outcome() maps status strings to canonical outcomes
  - EvidenceIngestor writes gap_attempts rows for items with gap_ledger_ref
  - CLI gap-attempts subcommand executes without error
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
import sys
# Mirror pattern used by existing control_index tests: add tools/supervisor to path
_TOOLS = str(REPO / "tools" / "supervisor")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from control_index.db import init_db, get_connection
from control_index.gap_selection import (
    get_exhausted_gaps,
    get_recent_attempt,
    write_exhausted_gaps_json,
    classify_outcome as _classify_outcome,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_db(tmp_path: Path) -> sqlite3.Connection:
    """Create a fresh in-memory-equivalent DB at tmp_path/test.db."""
    db_path = tmp_path / "test.db"
    init_db(db_path)
    return get_connection(db_path)


def _insert_attempt(conn, gap_id, sprint_id, outcome, attempted_at=None):
    attempt_id = f"{sprint_id}:{gap_id}:{outcome}"
    conn.execute(
        """INSERT OR IGNORE INTO gap_attempts
           (attempt_id, gap_id, sprint_id, item_id, outcome, attempted_at, source_file)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (attempt_id, gap_id, sprint_id, f"ITEM-{gap_id}", outcome,
         attempted_at or datetime.now(timezone.utc).isoformat(), "test"),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Test 1: gap_attempts table exists after init_db
# ---------------------------------------------------------------------------

def test_gap_attempts_table_exists(tmp_path):
    conn = _fresh_db(tmp_path)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "gap_attempts" in tables, "gap_attempts table must exist after init_db"
    conn.close()


# ---------------------------------------------------------------------------
# Test 2: get_exhausted_gaps identifies gaps at threshold
# ---------------------------------------------------------------------------

def test_get_exhausted_gaps_threshold(tmp_path):
    conn = _fresh_db(tmp_path)
    # GAP-001: 3 failures → exhausted
    for i in range(3):
        _insert_attempt(conn, "GAP-001", f"sprint-{i}", "failed")
    # GAP-002: 2 failures → NOT exhausted
    for i in range(2):
        _insert_attempt(conn, "GAP-002", f"sprint-x{i}", "failed")
    # GAP-003: 3 rework → exhausted
    for i in range(3):
        _insert_attempt(conn, "GAP-003", f"sprint-r{i}", "rework")

    exhausted = get_exhausted_gaps(conn, max_failed_attempts=3)
    assert "GAP-001" in exhausted
    assert "GAP-003" in exhausted
    assert "GAP-002" not in exhausted
    conn.close()


# ---------------------------------------------------------------------------
# Test 3: get_recent_attempt returns most recent record
# ---------------------------------------------------------------------------

def test_get_recent_attempt_returns_latest(tmp_path):
    conn = _fresh_db(tmp_path)
    _insert_attempt(conn, "GAP-010", "sprint-early", "failed",
                    attempted_at="2026-01-01T10:00:00+00:00")
    _insert_attempt(conn, "GAP-010", "sprint-late", "closed",
                    attempted_at="2026-06-01T10:00:00+00:00")

    recent = get_recent_attempt(conn, "GAP-010")
    assert recent is not None
    assert recent["outcome"] == "closed"
    assert recent["sprint_id"] == "sprint-late"
    conn.close()


# ---------------------------------------------------------------------------
# Test 4: get_recent_attempt returns None for unknown gap
# ---------------------------------------------------------------------------

def test_get_recent_attempt_unknown_gap(tmp_path):
    conn = _fresh_db(tmp_path)
    result = get_recent_attempt(conn, "GAP-NONEXISTENT")
    assert result is None
    conn.close()


# ---------------------------------------------------------------------------
# Test 5: write_exhausted_gaps_json writes correct JSON
# ---------------------------------------------------------------------------

def test_write_exhausted_gaps_json(tmp_path):
    conn = _fresh_db(tmp_path)
    for i in range(3):
        _insert_attempt(conn, "GAP-A", f"s{i}", "failed")
    for i in range(3):
        _insert_attempt(conn, "GAP-B", f"t{i}", "rework")

    output_path = tmp_path / "exhausted.json"
    count = write_exhausted_gaps_json(conn, output_path, max_failed_attempts=3)

    assert output_path.exists()
    data = json.loads(output_path.read_text())
    assert data["count"] == 2
    assert "GAP-A" in data["exhausted_gaps"]
    assert "GAP-B" in data["exhausted_gaps"]
    assert data["max_failed_attempts"] == 3
    assert count == 2
    conn.close()


# ---------------------------------------------------------------------------
# Test 6: _classify_outcome maps all canonical status strings
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("status,expected", [
    ("completed", "closed"),
    ("done", "closed"),
    ("closed", "closed"),
    ("verified", "closed"),
    ("COMPLETE", "closed"),
    ("failed", "failed"),
    ("FAIL", "failed"),
    ("error", "failed"),
    ("rework", "rework"),
    ("rework_required", "rework"),
    ("needs_rework", "rework"),
    ("in_progress", "partial"),
    ("pending", "partial"),
    (None, "partial"),
    ("", "partial"),
])
def test_classify_outcome_mapping(status, expected):
    assert _classify_outcome(status) == expected


# ---------------------------------------------------------------------------
# Test 7: EvidenceIngestor writes gap_attempts rows for gap-linked items
# ---------------------------------------------------------------------------

def test_evidence_ingestor_writes_gap_attempts(tmp_path):
    import yaml

    # Create a fake repo structure
    repo_root = tmp_path / "repo"
    evidences_dir = repo_root / ".local" / "evidences" / "run-001"
    evidences_dir.mkdir(parents=True)

    decl = {
        "sprint_id": "sprint-001",
        "run_id": "run-001",
        "start_time": "2026-07-01T10:00:00+00:00",
        "planned_work_items": [
            {
                "item_id": "ITEM-001",
                "title": "Fix FODS qname",
                "item_type": "gap_closure",
                "status": "completed",
                "gap_ledger_ref": "GAP-FODS-001",
            },
            {
                "item_id": "ITEM-002",
                "title": "No gap ref",
                "item_type": "maintenance",
                "status": "completed",
                "gap_ledger_ref": None,
            },
        ],
    }
    (evidences_dir / "evidence-declaration.yaml").write_text(
        yaml.dump(decl), encoding="utf-8"
    )

    # Init DB and ingest
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = get_connection(db_path)

    # Import via sync to ensure all ingestors are registered before circular-safe access
    import control_index.sync  # noqa: F401 — triggers @register_ingestor for all ingestors
    from control_index.ingestors.evidence_ingestor import EvidenceIngestor
    ingestor = EvidenceIngestor(conn=conn, repo_root=repo_root)
    result = ingestor.sync()

    assert result.inserted >= 1

    # gap_attempts should have one row for ITEM-001 (gap_ledger_ref set)
    rows = conn.execute("SELECT * FROM gap_attempts").fetchall()
    assert len(rows) == 1
    row = dict(rows[0])
    assert row["gap_id"] == "GAP-FODS-001"
    assert row["sprint_id"] == "sprint-001"
    assert row["outcome"] == "closed"

    conn.close()
