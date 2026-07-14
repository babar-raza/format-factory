"""Pilots 7-11: Taskcard Indexing, Evidence Spot-Check, Gap Attempt History (TC-OCRD-C8-02).

Pilot 7: taskcard indexing — gap_attempts queryable after EvidenceIngestor
Pilot 8: evidence spot-check — test count ratio warning fires at low ratio
Pilot 9: gap attempt history — get_exhausted_gaps returns correct set
Pilot 10: views.get_task_context returns required keys
Pilot 11: views.get_resume_context returns required keys
"""
import sqlite3
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
_TOOLS = str(REPO / "tools" / "supervisor")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from control_index.db import init_db, get_connection


def _fresh_conn(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = get_connection(db_path)
    return conn, db_path


def _insert_attempt(conn, gap_id, sprint_id, outcome):
    attempt_id = f"{sprint_id}:{gap_id}:{outcome}"
    conn.execute(
        """INSERT OR IGNORE INTO gap_attempts
           (attempt_id, gap_id, sprint_id, item_id, outcome, attempted_at, source_file)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (attempt_id, gap_id, sprint_id, "ITEM-X", outcome, "2026-07-01T10:00:00+00:00", "test"),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Pilot 7: gap_attempts queryable
# ---------------------------------------------------------------------------

def test_pilot7_gap_attempts_queryable(tmp_path):
    """Pilot 7: gap_attempts table is queryable and returns filtered results."""
    conn, _ = _fresh_conn(tmp_path)
    _insert_attempt(conn, "GAP-FODS-PILOT7", "sprint-100", "failed")
    _insert_attempt(conn, "GAP-FODS-PILOT7", "sprint-101", "failed")
    _insert_attempt(conn, "GAP-CSV-PILOT7", "sprint-102", "closed")

    failed = conn.execute(
        "SELECT gap_id, outcome FROM gap_attempts WHERE outcome = 'failed'"
    ).fetchall()
    assert len(failed) == 2, f"Pilot 7: expected 2 failed attempts, got {len(failed)}"

    all_rows = conn.execute("SELECT COUNT(*) FROM gap_attempts").fetchone()[0]
    assert all_rows == 3
    conn.close()


# ---------------------------------------------------------------------------
# Pilot 8: evidence spot-check — low ratio triggers warning
# ---------------------------------------------------------------------------

def test_pilot8_evidence_spot_check_warning(tmp_path):
    """Pilot 8: spot_check_test_count() warns when ratio < 0.5."""
    # Write a fake test file with 1 test function
    test_file = tmp_path / "test_fake.py"
    test_file.write_text(
        "def test_only_one():\n    assert True\n",
        encoding="utf-8",
    )

    from evidence_verifier import spot_check_test_count
    result = spot_check_test_count(
        repo_root=tmp_path,
        changed_files=["test_fake.py"],
        declared_passed=10,  # Claiming 10 but only 1 exists
        declared_failed=0,
    )
    assert result["actual_count"] == 1
    assert result["declared_count"] == 10
    assert result["ratio"] < 0.5
    assert result["warning"] is not None
    assert "WARN_TEST_COUNT_MISMATCH" in result["warning"]


# ---------------------------------------------------------------------------
# Pilot 9: get_exhausted_gaps returns correct set
# ---------------------------------------------------------------------------

def test_pilot9_get_exhausted_gaps_correct_set(tmp_path):
    """Pilot 9: get_exhausted_gaps correctly identifies gaps with >= 3 failures."""
    conn, _ = _fresh_conn(tmp_path)

    # GAP-EXHAUST-P9: 3 failures → exhausted
    for i in range(3):
        _insert_attempt(conn, "GAP-EXHAUST-P9", f"sprint-{i}", "failed")

    # GAP-PARTIAL-P9: 2 failures → not exhausted
    _insert_attempt(conn, "GAP-PARTIAL-P9", "sprint-10", "failed")
    _insert_attempt(conn, "GAP-PARTIAL-P9", "sprint-11", "failed")

    # GAP-CLOSED-P9: closed → not exhausted
    _insert_attempt(conn, "GAP-CLOSED-P9", "sprint-20", "closed")

    from control_index.gap_selection import get_exhausted_gaps
    exhausted = get_exhausted_gaps(conn, max_failed_attempts=3)

    assert "GAP-EXHAUST-P9" in exhausted
    assert "GAP-PARTIAL-P9" not in exhausted
    assert "GAP-CLOSED-P9" not in exhausted
    conn.close()


# ---------------------------------------------------------------------------
# Pilot 10: views.get_task_context returns required keys
# ---------------------------------------------------------------------------

def test_pilot10_get_task_context_returns_required_keys(tmp_path):
    """Pilot 10: get_task_context() returns dict with plan, sprint_evidence, linked_gaps, trust_warnings."""
    conn, _ = _fresh_conn(tmp_path)

    from control_index.views import get_task_context
    ctx = get_task_context(conn, "TC-TEST-PILOT10")

    assert "task_id" in ctx
    assert "plan" in ctx
    assert "sprint_evidence" in ctx
    assert "linked_gaps" in ctx
    assert "trust_warnings" in ctx
    assert isinstance(ctx["trust_warnings"], list)
    conn.close()


# ---------------------------------------------------------------------------
# Pilot 11: views.get_resume_context returns required keys
# ---------------------------------------------------------------------------

def test_pilot11_get_resume_context_returns_required_keys(tmp_path):
    """Pilot 11: get_resume_context() returns dict with latest_sprint, active_plan, contradiction_events, trust_warnings."""
    conn, _ = _fresh_conn(tmp_path)

    from control_index.views import get_resume_context
    ctx = get_resume_context(conn, tmp_path)

    assert "latest_sprint" in ctx
    assert "active_plan" in ctx
    assert "contradiction_events" in ctx
    assert "trust_warnings" in ctx
    assert isinstance(ctx["contradiction_events"], list)
    conn.close()
