"""Tests for the no-stop watchdog validator.

Ensures the agent cannot stop while executable work remains.
"""

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from validate_no_stop_watchdog import (
    check_continuation_signal,
    check_next_action,
    check_action_queue,
    check_rework_items,
    run_no_stop_watchdog,
)


@pytest.fixture
def repo_root(tmp_path):
    """Create minimal repo structure."""
    (tmp_path / "CLAUDE.md").write_text("x")
    (tmp_path / ".local" / "supervisor").mkdir(parents=True)
    return tmp_path


class TestContinuationSignal:
    def test_no_signal_allows_stop(self, repo_root):
        result = check_continuation_signal(repo_root)
        assert result["blocks_stop"] is False

    def test_true_with_rework_blocks(self, repo_root):
        sig = repo_root / ".local" / "supervisor" / "continuation-signal.json"
        sig.write_text(json.dumps({
            "autonomous_continue": "true_with_rework",
            "continuation_state": "YES_WITH_REWORK",
            "rework_items": ["RCHE-002"],
            "safe_lanes_available": True,
            "hard_stops_detected": [],
        }))
        result = check_continuation_signal(repo_root)
        assert result["blocks_stop"] is True
        assert len(result["blocking_reasons"]) >= 3

    def test_false_allows_stop(self, repo_root):
        sig = repo_root / ".local" / "supervisor" / "continuation-signal.json"
        sig.write_text(json.dumps({
            "autonomous_continue": False,
            "continuation_state": "NO_COMPLETE",
            "rework_items": [],
            "safe_lanes_available": False,
        }))
        result = check_continuation_signal(repo_root)
        assert result["blocks_stop"] is False


class TestNextAction:
    def test_no_action_allows_stop(self, repo_root):
        result = check_next_action(repo_root)
        assert result["blocks_stop"] is False

    def test_health_check_allows_stop(self, repo_root):
        action = repo_root / ".local" / "supervisor" / "next-action.json"
        action.write_text(json.dumps({"action_type": "QUEUE_HEALTH_CHECK"}))
        result = check_next_action(repo_root)
        assert result["blocks_stop"] is False

    def test_product_patch_blocks(self, repo_root):
        action = repo_root / ".local" / "supervisor" / "next-action.json"
        action.write_text(json.dumps({"action_type": "PRODUCT_SOURCE_PATCH_BOUNDED"}))
        result = check_next_action(repo_root)
        assert result["blocks_stop"] is True


class TestActionQueue:
    def test_no_queue_allows_stop(self, repo_root):
        result = check_action_queue(repo_root)
        assert result["blocks_stop"] is False

    def test_all_done_allows_stop(self, repo_root):
        queue = repo_root / ".local" / "supervisor" / "action-queue.jsonl"
        queue.write_text(json.dumps({"action_id": "a1", "status": "done"}) + "\n")
        result = check_action_queue(repo_root)
        assert result["blocks_stop"] is False

    def test_pending_item_blocks(self, repo_root):
        queue = repo_root / ".local" / "supervisor" / "action-queue.jsonl"
        lines = [
            json.dumps({"action_id": "a1", "status": "done"}),
            json.dumps({"action_id": "a2", "status": "pending"}),
        ]
        queue.write_text("\n".join(lines) + "\n")
        result = check_action_queue(repo_root)
        assert result["blocks_stop"] is True
        assert result["pending_count"] == 1


class TestReworkItems:
    def test_no_rework_allows_stop(self, repo_root):
        sig = repo_root / ".local" / "supervisor" / "continuation-signal.json"
        sig.write_text(json.dumps({"rework_items": []}))
        result = check_rework_items(repo_root)
        assert result["blocks_stop"] is False

    def test_rework_blocks(self, repo_root):
        sig = repo_root / ".local" / "supervisor" / "continuation-signal.json"
        sig.write_text(json.dumps({"rework_items": ["RCHE-002"]}))
        result = check_rework_items(repo_root)
        assert result["blocks_stop"] is True


class TestPackage196Reproduction:
    """Reproduce exact package 196 failure state."""

    def test_package_196_blocks_stop(self, repo_root):
        """With true_with_rework + RCHE-002 + safe lanes, stopping MUST be blocked."""
        sig = repo_root / ".local" / "supervisor" / "continuation-signal.json"
        sig.write_text(json.dumps({
            "autonomous_continue": "true_with_rework",
            "continuation_state": "YES_WITH_REWORK",
            "rework_items": ["RCHE-002"],
            "safe_lanes_available": True,
            "hard_stops_detected": [],
        }))
        action = repo_root / ".local" / "supervisor" / "next-action.json"
        action.write_text(json.dumps({"action_type": "QUEUE_HEALTH_CHECK"}))

        evidence_root = repo_root / ".local" / "evidences" / "pkg196"
        evidence_root.mkdir(parents=True)

        result = run_no_stop_watchdog(evidence_root)
        assert result["verdict"] == "BLOCK_STOP"
        assert "rework_items" in result["blocking_checks"]
        assert result["next_action"] is not None
        assert "RCHE-002" in result["next_action"]

    def test_clean_state_allows_stop(self, repo_root):
        sig = repo_root / ".local" / "supervisor" / "continuation-signal.json"
        sig.write_text(json.dumps({
            "autonomous_continue": False,
            "continuation_state": "NO_COMPLETE",
            "rework_items": [],
            "safe_lanes_available": False,
        }))
        evidence_root = repo_root / ".local" / "evidences" / "clean"
        evidence_root.mkdir(parents=True)

        result = run_no_stop_watchdog(evidence_root)
        assert result["verdict"] == "ALLOW_STOP"
