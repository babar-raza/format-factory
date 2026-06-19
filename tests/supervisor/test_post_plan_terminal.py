"""
Regression tests for check_continuation.py — POST_PLAN_TERMINAL and stale lock expiry.

TC-MH-007: Added 2026-06-19 as part of plan-execution machinery forensic healing sprint.

Tests:
    1. TERMINAL_CLOSED lock → POST_PLAN_TERMINAL STOP
    2. TERMINAL_CLOSED lock >168h old → skipped (stale), does NOT trigger POST_PLAN_TERMINAL
    3. COMPLETE lock → does NOT trigger POST_PLAN_TERMINAL
    4. IN_PROGRESS lock → ACTIVE_PLAN_INCOMPLETE (regression: existing behavior preserved)
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from tools.supervisor.check_continuation import check


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_signal(tmp_path: Path, overrides: dict | None = None) -> None:
    signal = {
        "autonomous_continue": True,
        "iteration": 1,
        "max_iterations": 12,
        "continuation_state": "YES",
        "hard_stops_detected": [],
        "stop_reason": None,
        "rework_items": [],
    }
    if overrides:
        signal.update(overrides)
    sig_dir = tmp_path / ".local" / "supervisor"
    sig_dir.mkdir(parents=True, exist_ok=True)
    (sig_dir / "continuation-signal.json").write_text(json.dumps(signal), encoding="utf-8")


def _write_gates(tmp_path: Path, content: str = "AUTONOMOUS_CONTINUE: YES") -> None:
    gates_dir = tmp_path / "reports" / "supervisor"
    gates_dir.mkdir(parents=True, exist_ok=True)
    (gates_dir / "approval-gates.md").write_text(content, encoding="utf-8")


def _write_work_items(tmp_path: Path) -> None:
    wi_dir = tmp_path / ".local" / "supervisor"
    wi_dir.mkdir(parents=True, exist_ok=True)
    (wi_dir / "next-work-items.json").write_text(
        json.dumps({"items": [{"item_id": "T1", "title": "Test"}]}),
        encoding="utf-8",
    )


def _write_plan_lock(tmp_path: Path, status: str, age_hours: float = 0.0) -> None:
    """Write a plan lock file into tmp_path's plan-locks directory.

    Omits session_id intentionally so the session-scoped filter in check_continuation.py
    (line: 'if lock_session_id and session_id and lock_session_id != session_id: continue')
    does not skip the lock. A lock without session_id is treated as a legacy shared lock
    and is always evaluated.
    """
    locks_dir = tmp_path / ".local" / "supervisor" / "plan-locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    updated_at = datetime.now(timezone.utc) - timedelta(hours=age_hours)
    lock = {
        "plan_path": "plans/test-plan.md",
        "status": status,
        "last_taskcard": None,
        "updated_at": updated_at.isoformat(),
        # No session_id: legacy-style lock, not filtered by session check
    }
    lock_file = locks_dir / "test-mh007-lock.json"
    lock_file.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")


def _setup_base(tmp_path: Path) -> None:
    """Set up signal, gates, and work items (needed for checks that pass through Check 1b)."""
    _write_signal(tmp_path)
    _write_gates(tmp_path)
    _write_work_items(tmp_path)


# ---------------------------------------------------------------------------
# Test 1: TERMINAL_CLOSED lock → POST_PLAN_TERMINAL STOP
# ---------------------------------------------------------------------------

def test_terminal_closed_lock_returns_post_plan_terminal(tmp_path):
    """A current TERMINAL_CLOSED plan lock must cause check() to return POST_PLAN_TERMINAL STOP."""
    _setup_base(tmp_path)
    _write_plan_lock(tmp_path, status="TERMINAL_CLOSED", age_hours=0.5)

    result = check(tmp_path)

    assert result["verdict"] == "STOP", f"Expected STOP, got: {result}"
    assert result["reason"] == "POST_PLAN_TERMINAL", (
        f"Expected POST_PLAN_TERMINAL, got: {result.get('reason')}"
    )


# ---------------------------------------------------------------------------
# Test 2: TERMINAL_CLOSED lock >168h old → skipped (stale), no POST_PLAN_TERMINAL
# ---------------------------------------------------------------------------

def test_stale_lock_over_168h_is_skipped(tmp_path):
    """A TERMINAL_CLOSED lock older than 168 hours must be skipped — no POST_PLAN_TERMINAL."""
    _setup_base(tmp_path)
    _write_plan_lock(tmp_path, status="TERMINAL_CLOSED", age_hours=200.0)

    result = check(tmp_path)

    # Stale lock is skipped — check should NOT return POST_PLAN_TERMINAL.
    # With a valid signal+gates+work-items, it should CONTINUE (no other blocks).
    assert result.get("reason") != "POST_PLAN_TERMINAL", (
        f"Stale lock (200h) must not trigger POST_PLAN_TERMINAL; got: {result}"
    )


# ---------------------------------------------------------------------------
# Test 3: COMPLETE lock → does NOT trigger POST_PLAN_TERMINAL
# ---------------------------------------------------------------------------

def test_complete_lock_does_not_trigger_post_plan_terminal(tmp_path):
    """A COMPLETE plan lock must NOT trigger POST_PLAN_TERMINAL — it only blocks IN_PROGRESS plans."""
    _setup_base(tmp_path)
    _write_plan_lock(tmp_path, status="COMPLETE", age_hours=1.0)

    result = check(tmp_path)

    assert result.get("reason") != "POST_PLAN_TERMINAL", (
        f"COMPLETE lock must not trigger POST_PLAN_TERMINAL; got: {result}"
    )


# ---------------------------------------------------------------------------
# Test 4: IN_PROGRESS lock → ACTIVE_PLAN_INCOMPLETE (regression)
# ---------------------------------------------------------------------------

def test_in_progress_lock_still_returns_active_plan_incomplete(tmp_path):
    """IN_PROGRESS plan lock must still return ACTIVE_PLAN_INCOMPLETE — existing behavior preserved."""
    _setup_base(tmp_path)
    _write_plan_lock(tmp_path, status="IN_PROGRESS", age_hours=0.5)

    result = check(tmp_path)

    assert result["verdict"] == "STOP", f"Expected STOP for IN_PROGRESS lock, got: {result}"
    assert result["reason"] == "ACTIVE_PLAN_INCOMPLETE", (
        f"Expected ACTIVE_PLAN_INCOMPLETE, got: {result.get('reason')}"
    )
