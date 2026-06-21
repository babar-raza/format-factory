"""
test_plan_lock_gate.py — Formal regression tests for check_continuation.py Check 1b
(Plan Lock Gate).

Scenarios covered:
  T1: No lock file present                     → CONTINUE (gate transparent)
  T2: Lock file with status=IN_PROGRESS        → STOP/ACTIVE_PLAN_INCOMPLETE
  T3: Lock file with status=COMPLETE           → CONTINUE (gate clears)
  T4: Lock file with corrupt JSON              → STOP/ACTIVE_PLAN_LOCK_CORRUPT
  T5: Lock file missing 'status' key           → STOP/ACTIVE_PLAN_INCOMPLETE
  T6: Lock file with unknown status value      → STOP/ACTIVE_PLAN_INCOMPLETE
  T7: STOP detail includes plan_path           → detail message contains plan_path
  T8: STOP detail includes last_taskcard       → detail message contains last_taskcard
"""
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

from check_continuation import check


def _write_lock(mock_repo, content: dict | None = None, raw: str | None = None):
    """Write .local/supervisor/active-plan-lock.json in the mock repo."""
    lock_path = mock_repo / ".local" / "supervisor" / "active-plan-lock.json"
    if raw is not None:
        lock_path.write_text(raw, encoding="utf-8")
    else:
        lock_path.write_text(json.dumps(content, indent=2), encoding="utf-8")
    return lock_path


class TestT1_NoLockFile:
    """T1: No lock file → gate is transparent; CONTINUE if other conditions allow."""

    def test_no_lock_file_does_not_block(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id="session-aaa")
        lock_path = mock_repo / ".local" / "supervisor" / "active-plan-lock.json"
        assert not lock_path.exists(), "pre-condition: lock file must not exist"
        result = check(mock_repo, session_id="session-aaa")
        assert result["verdict"] == "CONTINUE"


class TestT2_LockInProgress:
    """T2: Lock file with status=IN_PROGRESS → STOP with ACTIVE_PLAN_INCOMPLETE."""

    def test_in_progress_lock_blocks_continuation(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id="session-aaa")
        _write_lock(mock_repo, {
            "plan_path": "C:/Users/prora/.claude/plans/my-plan.md",
            "status": "IN_PROGRESS",
            "last_taskcard": "TC-001",
            "updated_at": "2026-06-17T00:00:00+00:00",
        })
        result = check(mock_repo, session_id="session-aaa")
        assert result["verdict"] == "STOP"
        assert result["reason"] == "ACTIVE_PLAN_INCOMPLETE"


class TestT3_LockComplete:
    """T3: Lock file with status=COMPLETE → gate clears; CONTINUE if other conditions allow."""

    def test_complete_lock_does_not_block(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id="session-aaa")
        _write_lock(mock_repo, {
            "plan_path": "C:/Users/prora/.claude/plans/my-plan.md",
            "status": "COMPLETE",
            "last_taskcard": None,
            "updated_at": "2026-06-17T00:00:00+00:00",
        })
        result = check(mock_repo, session_id="session-aaa")
        assert result["verdict"] == "CONTINUE"


class TestT4_LockCorruptJson:
    """T4: Lock file is corrupt JSON → STOP with ACTIVE_PLAN_LOCK_CORRUPT."""

    def test_corrupt_json_blocks_continuation(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id="session-aaa")
        _write_lock(mock_repo, raw="{not valid json :::}")
        result = check(mock_repo, session_id="session-aaa")
        assert result["verdict"] == "STOP"
        assert result["reason"] == "ACTIVE_PLAN_LOCK_CORRUPT"


class TestT5_LockMissingStatusKey:
    """T5: Lock file has no 'status' key → treated as not-COMPLETE → STOP."""

    def test_missing_status_key_blocks_continuation(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id="session-aaa")
        _write_lock(mock_repo, {
            "plan_path": "C:/Users/prora/.claude/plans/my-plan.md",
            "last_taskcard": "TC-001",
        })
        result = check(mock_repo, session_id="session-aaa")
        assert result["verdict"] == "STOP"
        assert result["reason"] == "ACTIVE_PLAN_INCOMPLETE"


class TestT6_UnknownStatusValue:
    """T6: Lock file has unrecognized status value → treated as not-COMPLETE → STOP."""

    def test_unknown_status_value_blocks_continuation(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id="session-aaa")
        _write_lock(mock_repo, {
            "plan_path": "C:/Users/prora/.claude/plans/my-plan.md",
            "status": "WHATEVER",
            "last_taskcard": "TC-001",
        })
        result = check(mock_repo, session_id="session-aaa")
        assert result["verdict"] == "STOP"
        assert result["reason"] == "ACTIVE_PLAN_INCOMPLETE"


class TestT7_DetailContainsPlanPath:
    """T7: STOP detail message includes the plan_path from the lock file."""

    def test_detail_contains_plan_path(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id="session-aaa")
        plan_path = "C:/Users/prora/.claude/plans/some-specific-plan.md"
        _write_lock(mock_repo, {
            "plan_path": plan_path,
            "status": "IN_PROGRESS",
            "last_taskcard": "TC-XYZ",
        })
        result = check(mock_repo, session_id="session-aaa")
        assert result["verdict"] == "STOP"
        assert plan_path in result.get("detail", "")


class TestT8_DetailContainsLastTaskcard:
    """T8: STOP detail message includes the last_taskcard from the lock file."""

    def test_detail_contains_last_taskcard(self, mock_repo, full_continue_setup):
        full_continue_setup(session_id="session-aaa")
        _write_lock(mock_repo, {
            "plan_path": "C:/Users/prora/.claude/plans/my-plan.md",
            "status": "IN_PROGRESS",
            "last_taskcard": "TC-PROD-007-04",
        })
        result = check(mock_repo, session_id="session-aaa")
        assert result["verdict"] == "STOP"
        assert "TC-PROD-007-04" in result.get("detail", "")
