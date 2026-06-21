"""TC-RC3: Regression tests for check_continuation.py dual-field invariant.

Verifies that check_continuation correctly handles both:
  - autonomous_continue field (Check 2)
  - hard_stops_detected field (Check 4)

These are independent checks; both must be clean for a CONTINUE verdict.
The code ordering is correct (hard_stops appended before auto_continue_value set),
but these tests guard against future regressions.

Source references:
  - check_continuation.py: Check 2 (line ~264), Check 4 (line ~288)
  - autonomous_cycle.py: hard_stops append at line ~1451, auto_continue at ~1491
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
from check_continuation import check  # noqa: E402


def _write_signal(tmp: Path, **fields) -> Path:
    """Write a minimal continuation-signal.json to tmp directory."""
    signal_dir = tmp / ".local" / "supervisor"
    signal_dir.mkdir(parents=True, exist_ok=True)
    signal_path = signal_dir / "continuation-signal.json"
    base: dict = {
        "autonomous_continue": True,
        "hard_stops_detected": [],
        "continuation_state": "YES",
        "stop_reason": None,
        "iteration": 1,
        "max_iterations": 100,
        "rework_items": [],
    }
    base.update(fields)
    signal_path.write_text(json.dumps(base), encoding="utf-8")
    return signal_path


def _write_gates(tmp: Path, content: str) -> None:
    gates_dir = tmp / "reports" / "supervisor"
    gates_dir.mkdir(parents=True, exist_ok=True)
    (gates_dir / "approval-gates.md").write_text(content, encoding="utf-8")


def _write_work_items(tmp: Path) -> None:
    work_dir = tmp / ".local" / "supervisor"
    work_dir.mkdir(parents=True, exist_ok=True)
    (work_dir / "next-work-items.json").write_text(
        json.dumps({"stream": "product", "work_items": [{"item_id": "TEST-001", "title": "test item"}]}), encoding="utf-8"
    )


class TestContinuationSignalInvariants:
    """TC-RC3: check_continuation dual-field invariant tests."""

    def test_stop_when_autonomous_continue_false(self, tmp_path):
        """STOP when autonomous_continue=false and gates also say NO.

        Note: check_continuation.py Check 2 has a B4 override: if gates say YES,
        a false signal (e.g. from evidence_quality_zero) is treated as stale and
        overridden. This test uses AUTONOMOUS_CONTINUE: NO in gates to exercise
        the genuine STOP path when both the signal and the gate agree to stop.
        """
        _write_signal(tmp_path, autonomous_continue=False, hard_stops_detected=[])
        _write_gates(tmp_path, "AUTONOMOUS_CONTINUE: NO")
        _write_work_items(tmp_path)
        result = check(tmp_path)
        assert result["verdict"] == "STOP", (
            "Expected STOP when autonomous_continue=False and gates=NO, "
            f"got {result['verdict']} (reason: {result.get('reason')})"
        )

    def test_stop_when_hard_stops_detected_nonempty(self, tmp_path):
        """STOP when hard_stops_detected is non-empty, even if autonomous_continue=true.

        This is the key invariant: both fields are checked independently.
        A signal with autonomous_continue=true but hard_stops_detected=['evidence_quality_zero']
        must produce STOP — not CONTINUE.
        """
        _write_signal(
            tmp_path,
            autonomous_continue=True,
            hard_stops_detected=["evidence_quality_zero"],
        )
        _write_gates(tmp_path, "AUTONOMOUS_CONTINUE: YES")
        _write_work_items(tmp_path)
        result = check(tmp_path)
        assert result["verdict"] == "STOP", (
            "Expected STOP when hard_stops_detected=['evidence_quality_zero'] "
            f"even with autonomous_continue=True, got {result['verdict']}"
        )

    def test_continue_when_both_clean(self, tmp_path):
        """CONTINUE when both autonomous_continue=true and hard_stops_detected=[].

        Baseline: the happy path must still work after any future changes.
        """
        _write_signal(
            tmp_path,
            autonomous_continue=True,
            hard_stops_detected=[],
            continuation_state="YES",
        )
        _write_gates(tmp_path, "AUTONOMOUS_CONTINUE: YES")
        _write_work_items(tmp_path)
        result = check(tmp_path)
        assert result["verdict"] == "CONTINUE", (
            f"Expected CONTINUE when both fields are clean, got {result['verdict']} "
            f"(reason: {result.get('reason')})"
        )

    def test_string_true_with_rework_treated_as_truthy(self, tmp_path):
        """'true_with_rework' string passes the autonomous_continue truthy check.

        The rework path uses string "true_with_rework" as the autonomous_continue value.
        This must be treated as truthy (passes Check 2) — rework handling is separate.
        """
        _write_signal(
            tmp_path,
            autonomous_continue="true_with_rework",
            hard_stops_detected=[],
            continuation_state="YES",
        )
        _write_gates(tmp_path, "AUTONOMOUS_CONTINUE: YES")
        _write_work_items(tmp_path)
        result = check(tmp_path)
        # Must not stop due to the autonomous_continue check alone
        # (may stop for other reasons, but NOT "autonomous_continue is false")
        if result["verdict"] == "STOP":
            assert result.get("reason") != "autonomous_continue is false", (
                "'true_with_rework' must be treated as truthy — "
                f"got STOP with reason: {result.get('reason')}"
            )
