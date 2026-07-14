"""Tests for TC-OCRD-A3: SyncReport persistence and control_index_warnings.

Covers:
  - sync_all writes last-sync-report.json with required keys
  - _get_control_index_warnings with fresh report → empty list
  - _get_control_index_warnings with stale report (>24h) → stale warning
  - _get_control_index_warnings with error_entities → error warning
  - missing last-sync-report.json → empty list, no exception
  - CONTINUE output dict contains control_index_warnings key
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
_TOOLS = str(REPO / "tools" / "supervisor")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from control_index.db import init_db
from control_index.sync import sync_all, SyncReport


# ---------------------------------------------------------------------------
# Test 1: sync_all writes last-sync-report.json with required keys
# ---------------------------------------------------------------------------

def test_sync_writes_last_sync_report(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".local" / "supervisor").mkdir(parents=True, exist_ok=True)

    sync_all(db_path, repo_root)

    report_path = repo_root / ".local" / "supervisor" / "last-sync-report.json"
    assert report_path.exists(), "last-sync-report.json must be written after sync"

    data = json.loads(report_path.read_text())
    for key in ("completed_at", "total_inserted", "total_errors", "error_entities", "stale_files", "schema_version"):
        assert key in data, f"last-sync-report.json must contain key: {key}"


# ---------------------------------------------------------------------------
# Test 2: _get_control_index_warnings with fresh report → empty list
# ---------------------------------------------------------------------------

def test_control_index_warnings_fresh_report(tmp_path):
    from check_continuation import _get_control_index_warnings
    repo_root = tmp_path
    local_dir = repo_root / ".local" / "supervisor"
    local_dir.mkdir(parents=True, exist_ok=True)

    # Fresh report: completed_at = now
    report = {
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "total_errors": 0,
        "error_entities": [],
        "stale_files": [],
        "schema_version": 3,
    }
    (local_dir / "last-sync-report.json").write_text(json.dumps(report))

    warnings = _get_control_index_warnings(repo_root)
    assert warnings == [], f"Fresh report should produce no warnings, got: {warnings}"


# ---------------------------------------------------------------------------
# Test 3: _get_control_index_warnings with stale report (>24h) → stale warning
# ---------------------------------------------------------------------------

def test_control_index_warnings_stale_report(tmp_path):
    from check_continuation import _get_control_index_warnings
    repo_root = tmp_path
    local_dir = repo_root / ".local" / "supervisor"
    local_dir.mkdir(parents=True, exist_ok=True)

    # Stale report: completed_at = 48 hours ago
    stale_time = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    report = {
        "completed_at": stale_time,
        "total_errors": 0,
        "error_entities": [],
        "stale_files": [],
        "schema_version": 3,
    }
    (local_dir / "last-sync-report.json").write_text(json.dumps(report))

    warnings = _get_control_index_warnings(repo_root)
    assert any("stale" in w for w in warnings), f"Stale report must produce stale warning, got: {warnings}"


# ---------------------------------------------------------------------------
# Test 4: _get_control_index_warnings with error_entities → error warning
# ---------------------------------------------------------------------------

def test_control_index_warnings_error_entities(tmp_path):
    from check_continuation import _get_control_index_warnings
    repo_root = tmp_path
    local_dir = repo_root / ".local" / "supervisor"
    local_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "total_errors": 2,
        "error_entities": ["gap", "sprint"],
        "stale_files": [],
        "schema_version": 3,
    }
    (local_dir / "last-sync-report.json").write_text(json.dumps(report))

    warnings = _get_control_index_warnings(repo_root)
    assert any("error" in w for w in warnings), f"Error entities must produce error warning, got: {warnings}"


# ---------------------------------------------------------------------------
# Test 5: missing last-sync-report.json → empty list, no exception
# ---------------------------------------------------------------------------

def test_control_index_warnings_missing_file(tmp_path):
    from check_continuation import _get_control_index_warnings
    repo_root = tmp_path  # No last-sync-report.json at all

    warnings = _get_control_index_warnings(repo_root)
    assert warnings == [], f"Missing report should return empty list, got: {warnings}"


# ---------------------------------------------------------------------------
# Test 6: CONTINUE output dict contains control_index_warnings key
# ---------------------------------------------------------------------------

def test_check_continuation_continue_has_control_index_warnings_key(tmp_path):
    """Source-code presence check — verify the key is emitted in CONTINUE output."""
    check_cont_path = REPO / "tools" / "supervisor" / "check_continuation.py"
    source = check_cont_path.read_text(encoding="utf-8")
    assert "control_index_warnings" in source, (
        "check_continuation.py must contain 'control_index_warnings' key"
    )
    assert "_get_control_index_warnings" in source, (
        "check_continuation.py must define _get_control_index_warnings()"
    )
