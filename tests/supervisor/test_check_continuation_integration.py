"""
Integration tests for check_continuation.py — multi-sprint continuation simulation.
Tests the full state-file flow: signal → check → update → check again.
TC-VERI-001: End-to-end 2-sprint integration test.
"""
import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.supervisor.check_continuation import check


def _write_signal(tmp_path, overrides=None):
    signal = {
        "autonomous_continue": True,
        "iteration": 0,
        "max_iterations": 5,
        "continuation_state": "YES",
        "hard_stops_detected": [],
        "stop_reason": None,
        "rework_items": [],
    }
    if overrides:
        signal.update(overrides)
    sig_dir = tmp_path / ".local" / "supervisor"
    sig_dir.mkdir(parents=True, exist_ok=True)
    (sig_dir / "continuation-signal.json").write_text(
        json.dumps(signal), encoding="utf-8"
    )
    return signal


def _write_gates(tmp_path, autonomous=True):
    gates_dir = tmp_path / "reports" / "supervisor"
    gates_dir.mkdir(parents=True, exist_ok=True)
    yes_no = "YES" if autonomous else "NO — repair required first"
    (gates_dir / "approval-gates.md").write_text(
        f"AUTONOMOUS_CONTINUE: {yes_no}\n", encoding="utf-8"
    )


def _write_work_items(tmp_path, items=None):
    if items is None:
        items = [{"item_id": "TASK-001", "title": "Test task"}]
    wi_dir = tmp_path / ".local" / "supervisor"
    wi_dir.mkdir(parents=True, exist_ok=True)
    (wi_dir / "next-work-items.json").write_text(
        json.dumps({"items": items}), encoding="utf-8"
    )


def _update_iteration(tmp_path, new_iteration):
    sig_path = tmp_path / ".local" / "supervisor" / "continuation-signal.json"
    signal = json.loads(sig_path.read_text(encoding="utf-8"))
    signal["iteration"] = new_iteration
    sig_path.write_text(json.dumps(signal), encoding="utf-8")


# ── Multi-sprint simulation ──────────────────────────────────────────────

class TestMultiSprintContinuation:
    """Simulates a 3-sprint autonomous loop: 2 successful + 1 stop."""

    def test_sprint_0_continues(self, tmp_path):
        _write_signal(tmp_path, {"iteration": 0, "max_iterations": 5})
        _write_gates(tmp_path)
        _write_work_items(tmp_path)
        result = check(tmp_path)
        assert result["verdict"] == "CONTINUE"
        assert result["iteration"] == 0

    def test_sprint_1_continues_after_increment(self, tmp_path):
        _write_signal(tmp_path, {"iteration": 0, "max_iterations": 5})
        _write_gates(tmp_path)
        _write_work_items(tmp_path)

        # Sprint 0: check → CONTINUE
        r0 = check(tmp_path)
        assert r0["verdict"] == "CONTINUE"

        # Simulate sprint completion: increment iteration
        _update_iteration(tmp_path, 1)

        # Sprint 1: check → CONTINUE
        r1 = check(tmp_path)
        assert r1["verdict"] == "CONTINUE"
        assert r1["iteration"] == 1

    def test_full_loop_continue_continue_stop(self, tmp_path):
        _write_signal(tmp_path, {"iteration": 0, "max_iterations": 3})
        _write_gates(tmp_path)
        _write_work_items(tmp_path)

        # Sprint 0
        r0 = check(tmp_path)
        assert r0["verdict"] == "CONTINUE"
        _update_iteration(tmp_path, 1)

        # Sprint 1
        r1 = check(tmp_path)
        assert r1["verdict"] == "CONTINUE"
        _update_iteration(tmp_path, 2)

        # Sprint 2
        r2 = check(tmp_path)
        assert r2["verdict"] == "CONTINUE"
        _update_iteration(tmp_path, 3)

        # Sprint 3: at max_iterations → STOP
        r3 = check(tmp_path)
        assert r3["verdict"] == "STOP"
        assert r3["reason"] == "MAX_ITERATIONS"

    def test_hard_stop_mid_loop(self, tmp_path):
        _write_signal(tmp_path, {"iteration": 1, "max_iterations": 5})
        _write_gates(tmp_path)
        _write_work_items(tmp_path)

        # Sprint 1: CONTINUE
        r1 = check(tmp_path)
        assert r1["verdict"] == "CONTINUE"

        # Sprint 2: hard stop injected
        sig_path = tmp_path / ".local" / "supervisor" / "continuation-signal.json"
        signal = json.loads(sig_path.read_text(encoding="utf-8"))
        signal["iteration"] = 2
        signal["hard_stops_detected"] = ["critical_rework_blocks_continuation"]
        sig_path.write_text(json.dumps(signal), encoding="utf-8")

        r2 = check(tmp_path)
        assert r2["verdict"] == "STOP"
        assert r2["reason"] == "HARD_STOP"

    def test_rework_items_passed_through(self, tmp_path):
        _write_signal(tmp_path, {
            "iteration": 1,
            "max_iterations": 5,
            "continuation_state": "YES_WITH_REWORK",
            "rework_items": ["REWORK-001", "REWORK-002"],
        })
        _write_gates(tmp_path)
        _write_work_items(tmp_path)

        result = check(tmp_path)
        assert result["verdict"] == "CONTINUE"
        assert result["rework_items"] == ["REWORK-001", "REWORK-002"]

    def test_approval_gate_change_mid_loop(self, tmp_path):
        _write_signal(tmp_path, {"iteration": 1, "max_iterations": 5})
        _write_gates(tmp_path, autonomous=True)
        _write_work_items(tmp_path)

        # Sprint 1: CONTINUE
        r1 = check(tmp_path)
        assert r1["verdict"] == "CONTINUE"

        # External change: approval gate flipped to NO
        _write_gates(tmp_path, autonomous=False)

        r2 = check(tmp_path)
        assert r2["verdict"] == "STOP"
        assert r2["reason"] == "APPROVAL_GATE_NO"

    def test_work_items_removed_mid_loop(self, tmp_path):
        _write_signal(tmp_path, {"iteration": 1, "max_iterations": 5})
        _write_gates(tmp_path)
        _write_work_items(tmp_path)

        r1 = check(tmp_path)
        assert r1["verdict"] == "CONTINUE"

        # Remove work items file
        (tmp_path / ".local" / "supervisor" / "next-work-items.json").unlink()

        r2 = check(tmp_path)
        assert r2["verdict"] == "STOP"
        assert r2["reason"] == "NO_WORK_ITEMS"
