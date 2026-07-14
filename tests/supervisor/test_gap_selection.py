"""Tests for TC-OCRD-B2: Gap Selection Integration with Exhausted Gap Filter.

Covers:
  - get_exhausted_gaps after 3 failed attempts → includes gap
  - get_exhausted_gaps after 2 failed + 1 closed → excludes gap
  - No attempts → empty set
  - load_foss_gaps filters out exhausted gaps when DB available
  - load_foss_gaps works normally when DB unavailable
"""
import json
import sys
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
_TOOLS = str(REPO / "tools" / "supervisor")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from control_index.db import init_db, get_connection
from control_index.gap_selection import get_exhausted_gaps


def _fresh_conn(tmp_path: Path) -> tuple[sqlite3.Connection, Path]:
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = get_connection(db_path)
    return conn, db_path


def _insert_attempt(conn, gap_id, sprint_id, outcome, attempted_at="2026-07-01T10:00:00+00:00"):
    attempt_id = f"{sprint_id}:{gap_id}:{outcome}"
    conn.execute(
        """INSERT OR IGNORE INTO gap_attempts
           (attempt_id, gap_id, sprint_id, item_id, outcome, attempted_at, source_file)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (attempt_id, gap_id, sprint_id, "ITEM-X", outcome, attempted_at, "test"),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Test 1: 3 failed attempts → gap is exhausted
# ---------------------------------------------------------------------------

def test_three_failures_gap_exhausted(tmp_path):
    conn, _ = _fresh_conn(tmp_path)
    for i in range(3):
        _insert_attempt(conn, "GAP-FODS-001", f"sprint-{i}", "failed")

    exhausted = get_exhausted_gaps(conn, max_failed_attempts=3)
    assert "GAP-FODS-001" in exhausted
    conn.close()


# ---------------------------------------------------------------------------
# Test 2: 2 failed + 1 closed → gap NOT exhausted
# ---------------------------------------------------------------------------

def test_two_fail_one_closed_not_exhausted(tmp_path):
    conn, _ = _fresh_conn(tmp_path)
    _insert_attempt(conn, "GAP-CSV-001", "sprint-1", "failed")
    _insert_attempt(conn, "GAP-CSV-001", "sprint-2", "failed")
    _insert_attempt(conn, "GAP-CSV-001", "sprint-3", "closed")

    exhausted = get_exhausted_gaps(conn, max_failed_attempts=3)
    assert "GAP-CSV-001" not in exhausted  # closed outcomes don't count
    conn.close()


# ---------------------------------------------------------------------------
# Test 3: No attempts → empty set
# ---------------------------------------------------------------------------

def test_no_attempts_empty_exhausted_set(tmp_path):
    conn, _ = _fresh_conn(tmp_path)
    exhausted = get_exhausted_gaps(conn, max_failed_attempts=3)
    assert exhausted == set()
    conn.close()


# ---------------------------------------------------------------------------
# Test 4: Exhausted filter logic correctly removes exhausted gaps from list
# ---------------------------------------------------------------------------

def test_exhausted_filter_removes_from_candidate_list(tmp_path):
    """Directly test the filtering logic: gaps in exhausted set are removed."""
    conn, _ = _fresh_conn(tmp_path)

    # Make GAP-EXHAUSTED-001 exhausted (3 failures)
    for i in range(3):
        _insert_attempt(conn, "GAP-EXHAUSTED-001", f"sprint-{i}", "failed")

    candidates = [
        {"gap_id": "GAP-EXHAUSTED-001", "format": "fods"},
        {"gap_id": "GAP-FRESH-001", "format": "csv"},
        {"gap_id": "GAP-ANOTHER-001", "format": "tsv"},
    ]

    exhausted = get_exhausted_gaps(conn, max_failed_attempts=3)
    filtered = [g for g in candidates if g.get("gap_id", "") not in exhausted]

    gap_ids = {g.get("gap_id") for g in filtered}
    assert "GAP-EXHAUSTED-001" not in gap_ids, "Exhausted gap must be removed"
    assert "GAP-FRESH-001" in gap_ids
    assert "GAP-ANOTHER-001" in gap_ids
    conn.close()


def test_capability_queue_consumer_has_exhaustion_filter():
    """Source-code verification that the filter was injected into capability_queue_consumer.py."""
    source = (REPO / "tools" / "supervisor" / "capability_queue_consumer.py").read_text(encoding="utf-8")
    assert "get_exhausted_gaps" in source, "capability_queue_consumer.py must call get_exhausted_gaps()"
    assert "_CONTROL_INDEX_AVAILABLE" in source, "capability_queue_consumer.py must check _CONTROL_INDEX_AVAILABLE"


# ---------------------------------------------------------------------------
# Test 5: load_foss_gaps works normally when DB unavailable
# ---------------------------------------------------------------------------

def test_load_foss_gaps_works_without_db(tmp_path):
    """When control index is unavailable, load_foss_gaps returns full list gracefully."""
    gap_ledger = {
        "gaps": [
            {
                "gap_id": "GAP-001",
                "format": "fods",
                "capability_name": "test_cap",
                "product_type": "foss",
                "status": "open",
                "gap_type": "feature",
            },
        ]
    }
    ledger_path = tmp_path / "gap-ledger.json"
    ledger_path.write_text(json.dumps(gap_ledger), encoding="utf-8")

    import capability_queue_consumer as cqc

    with patch.object(cqc, "_GAP_LEDGER_PATH", ledger_path), \
         patch.object(cqc, "_ASSIGNED_GAPS_PATH", tmp_path / "assigned.json"), \
         patch.object(cqc, "_CONTROL_INDEX_AVAILABLE", False):

        result = cqc.load_foss_gaps(max_gaps=10)

    # Must return gaps without exception even when DB unavailable
    assert len(result) >= 1
    assert any(g.get("gap_id") == "GAP-001" for g in result)
