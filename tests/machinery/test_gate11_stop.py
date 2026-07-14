"""Tests for Gate 11 check_continuation stop behavior (TC-GFB-024-02, FF-MR-2026-001).

Requirements: REQ-TEST-003 — Gate 11 stop verified via test.

Tests:
1. When a product has state=GATE_11_READY, check_continuation returns STOP
2. When all products are NOT_READY, Gate 11 does not block continuation
3. Gate 11 stop does not fire when gate-states.yaml is absent
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


def _make_continuation_env(tmp_path: Path) -> None:
    """Create minimal environment for check_continuation.py to run."""
    sig_dir = tmp_path / ".local" / "supervisor"
    sig_dir.mkdir(parents=True)
    signal = {
        "autonomous_continue": True,
        "continuation_state": "YES",
        "iteration": 1,
        "max_iterations": 12,
        "rework_items": [],
        "stop_reason": None,
        "session_id": None,
        "hard_stops_detected": [],
    }
    (sig_dir / "continuation-signal.json").write_text(json.dumps(signal))

    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "supervisor").mkdir()
    (tmp_path / "reports" / "supervisor" / "approval-gates.md").write_text(
        "AUTONOMOUS_CONTINUE: YES\n"
    )
    (tmp_path / ".local" / "supervisor" / "next-work-items.json").write_text(
        json.dumps({"work_items": [{"id": "W1", "format": "csv"}]})
    )


class TestGate11StopBehavior:
    """Check 11 in check_continuation.py must stop when a product is GATE_11_READY."""

    def test_gate11_ready_product_stops_continuation(self, tmp_path: Path) -> None:
        """When a product has state=GATE_11_READY, check returns verdict=STOP."""
        _make_continuation_env(tmp_path)
        (tmp_path / "registry").mkdir()
        gate_yaml = {
            "gate_states": [{"state_id": "GATE_11_READY", "per_product": True}],
            "format_gate_states": {
                "csv": {
                    "python": {
                        "state": "GATE_11_READY",
                        "p1_oracle_verified": True,
                    }
                }
            },
        }
        (tmp_path / "registry" / "gate-states.yaml").write_text(
            yaml.dump(gate_yaml), encoding="utf-8"
        )

        from check_continuation import check
        result = check(tmp_path)
        assert result["verdict"] == "STOP", (
            f"Expected STOP when csv has state=GATE_11_READY, got: {result['verdict']}"
        )
        assert result.get("reason") == "gate_11_ready_pending_authorization", (
            f"Expected reason=gate_11_ready_pending_authorization, got: {result.get('reason')}"
        )

    def test_not_ready_products_do_not_trigger_gate11_stop(self, tmp_path: Path) -> None:
        """When all products are NOT_READY, Gate 11 check must not block."""
        _make_continuation_env(tmp_path)
        (tmp_path / "registry").mkdir()
        gate_yaml = {
            "gate_states": [{"state_id": "NOT_READY", "per_product": True}],
            "format_gate_states": {
                "csv": {"python": {"state": "NOT_READY"}},
                "fods": {"python": {"state": "NOT_READY"}},
            },
        }
        (tmp_path / "registry" / "gate-states.yaml").write_text(
            yaml.dump(gate_yaml), encoding="utf-8"
        )

        from check_continuation import check
        result = check(tmp_path)
        assert result.get("reason") != "gate_11_ready_pending_authorization", (
            f"Gate 11 must not block when all products are NOT_READY: {result}"
        )

    def test_missing_gate_states_file_does_not_block(self, tmp_path: Path) -> None:
        """When gate-states.yaml is absent, Gate 11 check must not block."""
        _make_continuation_env(tmp_path)
        # Do NOT create registry/gate-states.yaml

        from check_continuation import check
        result = check(tmp_path)
        assert result.get("reason") != "gate_11_ready_pending_authorization", (
            f"Gate 11 must not block when gate-states.yaml is absent: {result}"
        )

    def test_gate11_ready_product_in_message_identifies_format(self, tmp_path: Path) -> None:
        """The stop message must identify which format/language is GATE_11_READY."""
        _make_continuation_env(tmp_path)
        (tmp_path / "registry").mkdir()
        gate_yaml = {
            "gate_states": [{"state_id": "GATE_11_READY", "per_product": True}],
            "format_gate_states": {
                "fods": {
                    "python": {"state": "GATE_11_READY", "p1_oracle_verified": True}
                }
            },
        }
        (tmp_path / "registry" / "gate-states.yaml").write_text(
            yaml.dump(gate_yaml), encoding="utf-8"
        )

        from check_continuation import check
        result = check(tmp_path)
        assert result["verdict"] == "STOP"
        # The message should reference fods/python
        msg = result.get("message", "") or result.get("stop_reason", "")
        assert "fods" in msg.lower() or "fods" in str(result).lower(), (
            f"Stop message should identify fods as the GATE_11_READY format: {result}"
        )
