"""test_machinery_mission_ledger.py — Regression tests for Check 1c (GAP-WHALE-001).

TC-WHALE-LEDGER-001 (2026-06-21): check_continuation.py must enforce machinery
mission-ledger.json stop_status when called with --track machinery.

Tests:
  - MACHINERY_MISSION_COMPLETE fires when stop_status=MISSION_COMPLETE
  - MACHINERY_AUDIT_REQUIRED fires when audit_pending=True and execution_pending=False
  - Product track ignores machinery ledger entirely
  - Missing ledger does not block machinery track (graceful no-op)
  - Ledger with stop_status != MISSION_COMPLETE does not block
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
_CC = _REPO / "tools" / "supervisor" / "check_continuation.py"


def _run_cc(tmp_path: Path, track: str = "machinery") -> dict:
    """Run check_continuation.py with --repo-root tmp_path and parse JSON output."""
    result = subprocess.run(
        [sys.executable, str(_CC), "--repo-root", str(tmp_path), "--track", track],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    try:
        return json.loads(result.stdout)
    except Exception:
        return {"_raw_stdout": result.stdout, "_raw_stderr": result.stderr}


def _write_clean_signal(tmp_path: Path, track: str = "machinery") -> None:
    """Write a minimal clean continuation signal so Check 2 doesn't fire first.

    For --track machinery, the signal must be at .local/supervisor/machinery/continuation-signal.json
    (strict path, no legacy fallback per check_continuation.py lines 45-46).
    """
    if track == "machinery":
        sig_dir = tmp_path / ".local" / "supervisor" / "machinery"
    elif track == "product":
        sig_dir = tmp_path / ".local" / "supervisor" / "product"
    else:
        sig_dir = tmp_path / ".local" / "supervisor"
    sig_dir.mkdir(parents=True, exist_ok=True)
    (sig_dir / "continuation-signal.json").write_text(
        json.dumps({
            "autonomous_continue": True,
            "iteration": 0,
            "max_iterations": 5,
            "rework_items": [],
            "hard_stops_detected": [],
            "safe_lanes_available": True,
        }),
        encoding="utf-8",
    )


def _write_ledger(tmp_path: Path, ledger: dict) -> None:
    ledger_dir = tmp_path / ".local" / "supervisor" / "machinery"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    (ledger_dir / "mission-ledger.json").write_text(
        json.dumps(ledger), encoding="utf-8"
    )


class TestMachineryMissionLedgerCheck1c:
    """Check 1c: machinery mission ledger enforcement in check_continuation.py."""

    def test_mission_complete_returns_stop(self, tmp_path):
        """When stop_status=MISSION_COMPLETE, check_continuation must return STOP."""
        _write_clean_signal(tmp_path, track="machinery")
        _write_ledger(tmp_path, {
            "mission_id": "test-mission-001",
            "stop_status": "MISSION_COMPLETE",
            "open_gaps": [],
            "audit_pending": False,
            "execution_pending": False,
        })
        result = _run_cc(tmp_path, track="machinery")
        assert result.get("verdict") == "STOP", f"Expected STOP, got: {result}"
        assert result.get("reason") == "MACHINERY_MISSION_COMPLETE", (
            f"Expected MACHINERY_MISSION_COMPLETE reason, got: {result.get('reason')}"
        )

    def test_audit_pending_no_execution_returns_stop(self, tmp_path):
        """When audit_pending=True and execution_pending=False, return STOP(MACHINERY_AUDIT_REQUIRED)."""
        _write_clean_signal(tmp_path, track="machinery")
        _write_ledger(tmp_path, {
            "mission_id": "test-mission-002",
            "stop_status": "AUDIT_REQUIRED",
            "open_gaps": ["GAP-001"],
            "audit_pending": True,
            "execution_pending": False,
        })
        result = _run_cc(tmp_path, track="machinery")
        assert result.get("verdict") == "STOP", f"Expected STOP, got: {result}"
        assert result.get("reason") == "MACHINERY_AUDIT_REQUIRED", (
            f"Expected MACHINERY_AUDIT_REQUIRED reason, got: {result.get('reason')}"
        )

    def test_no_ledger_does_not_block(self, tmp_path):
        """When mission-ledger.json is absent, machinery track should not be blocked by Check 1c."""
        _write_clean_signal(tmp_path, track="machinery")
        # No ledger file written — Check 1c must be a graceful no-op
        result = _run_cc(tmp_path, track="machinery")
        # Should not be blocked by MACHINERY_* reason
        machinery_reasons = {"MACHINERY_MISSION_COMPLETE", "MACHINERY_AUDIT_REQUIRED"}
        assert result.get("reason") not in machinery_reasons, (
            f"Check 1c blocked when ledger is absent: {result}"
        )

    def test_active_mission_does_not_block(self, tmp_path):
        """When stop_status is not MISSION_COMPLETE, machinery track should not be blocked."""
        _write_clean_signal(tmp_path, track="machinery")
        _write_ledger(tmp_path, {
            "mission_id": "test-mission-003",
            "stop_status": "EXECUTION_REQUIRED",
            "open_gaps": ["GAP-ARCH-001"],
            "audit_pending": False,
            "execution_pending": True,
        })
        result = _run_cc(tmp_path, track="machinery")
        machinery_reasons = {"MACHINERY_MISSION_COMPLETE", "MACHINERY_AUDIT_REQUIRED"}
        assert result.get("reason") not in machinery_reasons, (
            f"Check 1c incorrectly blocked an active mission: {result}"
        )

    def test_product_track_ignores_machinery_ledger(self, tmp_path):
        """Product track must ignore machinery mission-ledger.json (Check 1c is machinery-only)."""
        _write_clean_signal(tmp_path, track="product")
        _write_ledger(tmp_path, {
            "mission_id": "test-mission-004",
            "stop_status": "MISSION_COMPLETE",
            "open_gaps": [],
            "audit_pending": False,
            "execution_pending": False,
        })
        result = _run_cc(tmp_path, track="product")
        machinery_reasons = {"MACHINERY_MISSION_COMPLETE", "MACHINERY_AUDIT_REQUIRED"}
        assert result.get("reason") not in machinery_reasons, (
            f"Product track was blocked by machinery ledger: {result}"
        )

    def test_audit_pending_with_execution_pending_does_not_block(self, tmp_path):
        """audit_pending=True AND execution_pending=True must NOT trigger MACHINERY_AUDIT_REQUIRED.

        The audit is only required when execution is done (execution_pending=False).
        """
        _write_clean_signal(tmp_path, track="machinery")
        _write_ledger(tmp_path, {
            "mission_id": "test-mission-005",
            "stop_status": "EXECUTION_RUNNING",
            "open_gaps": ["GAP-001"],
            "audit_pending": True,
            "execution_pending": True,  # execution is still pending
        })
        result = _run_cc(tmp_path, track="machinery")
        assert result.get("reason") != "MACHINERY_AUDIT_REQUIRED", (
            f"Check 1c blocked when execution is still pending: {result}"
        )
