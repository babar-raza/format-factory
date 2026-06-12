"""
Tests that the action queue is the primary execution source when --queue-first is used.
Sprint: FORMAT-FACTORY-H6-AUTONOMOUS-PRODUCT-QUEUE-CONSUMPTION-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))

from tools.supervisor.action_queue import (
    FORBIDDEN_IN_QUEUE,
    dequeue_next, mark_done, mark_failed, _load_queue, _save_queue,
)
from tools.supervisor.autonomous_orchestrator import _queue_item_to_next_action


# ── Helpers ────────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_queue(tmp_path, monkeypatch):
    q = tmp_path / "action-queue.jsonl"
    monkeypatch.setattr("tools.supervisor.action_queue.QUEUE_PATH", q)
    return q


# ── queue_item_to_next_action conversion ──────────────────────────────────────

def test_queue_item_to_next_action_preserves_action_id():
    item = {"action_id": "test-001", "action_type": "RUN_JSON_VALIDATION",
            "preferred_backend": "LOCAL_DETERMINISTIC", "objective": "test"}
    action = _queue_item_to_next_action(item, cycle_index=1, sprint_id="TEST-SPRINT")
    assert action["action_id"] == "test-001"


def test_queue_item_to_next_action_preserves_action_type():
    item = {"action_id": "q-001", "action_type": "PRODUCT_GAP_CLASSIFICATION_READONLY",
            "objective": "Classify gaps"}
    action = _queue_item_to_next_action(item, cycle_index=1, sprint_id="TEST-SPRINT")
    assert action["action_type"] == "PRODUCT_GAP_CLASSIFICATION_READONLY"


def test_queue_item_to_next_action_from_queue_flag():
    item = {"action_id": "q-001", "action_type": "RUN_JSON_VALIDATION", "objective": "x"}
    action = _queue_item_to_next_action(item, cycle_index=1, sprint_id="TEST-SPRINT")
    assert action.get("from_queue") is True
    assert action.get("queue_item_id") == "q-001"


def test_queue_item_to_next_action_carries_target():
    item = {"action_id": "q-001", "action_type": "RUN_JSON_VALIDATION",
            "target": "some/path.json", "objective": "x"}
    action = _queue_item_to_next_action(item, cycle_index=1, sprint_id="TEST-SPRINT")
    assert action.get("target") == "some/path.json"


def test_queue_item_to_next_action_carries_target_path():
    item = {"action_id": "q-001", "action_type": "RUN_JSON_VALIDATION",
            "target_path": "some/path.json", "objective": "x"}
    action = _queue_item_to_next_action(item, cycle_index=1, sprint_id="TEST-SPRINT")
    assert action.get("target") == "some/path.json"


def test_queue_item_to_next_action_result_path_in_write_roots():
    item = {"action_id": "q-001", "action_type": "RUN_JSON_VALIDATION",
            "result_path": "reports/h6-queue-product-loop/host-run/q001.json",
            "allowed_write_roots": ["reports/h6-queue-product-loop/"],
            "objective": "x"}
    action = _queue_item_to_next_action(item, cycle_index=1, sprint_id="TEST-SPRINT")
    assert "reports/h6-queue-product-loop/" in action["allowed_write_roots"]


def test_queue_item_to_next_action_external_gate_preserved():
    item = {"action_id": "q-001", "action_type": "RUN_JSON_VALIDATION",
            "external_gate": True, "objective": "x"}
    action = _queue_item_to_next_action(item, cycle_index=1, sprint_id="TEST-SPRINT")
    assert action["external_gate"] is True


# ── dequeue_next priority ordering ────────────────────────────────────────────

def test_dequeue_next_selects_lowest_priority_first(tmp_queue, monkeypatch):
    items = [
        {"action_id": "high", "priority": 5, "action_type": "RUN_JSON_VALIDATION",
         "status": "pending", "queued_at": "2026-01-01T00:00:00Z", "external_gate": False},
        {"action_id": "low", "priority": 1, "action_type": "RUN_JSON_VALIDATION",
         "status": "pending", "queued_at": "2026-01-01T00:00:00Z", "external_gate": False},
    ]
    _save_queue(items)
    chosen = dequeue_next()
    assert chosen["action_id"] == "low"


def test_dequeue_next_skips_external_gate_items(tmp_queue, monkeypatch):
    items = [
        {"action_id": "gated", "priority": 0, "action_type": "RUN_JSON_VALIDATION",
         "status": "pending", "queued_at": "2026-01-01T00:00:00Z", "external_gate": True},
        {"action_id": "safe", "priority": 5, "action_type": "RUN_JSON_VALIDATION",
         "status": "pending", "queued_at": "2026-01-01T00:00:00Z", "external_gate": False},
    ]
    _save_queue(items)
    chosen = dequeue_next()
    assert chosen["action_id"] == "safe"


def test_dequeue_next_skips_running_items(tmp_queue, monkeypatch):
    items = [
        {"action_id": "running", "priority": 1, "action_type": "RUN_JSON_VALIDATION",
         "status": "running", "queued_at": "2026-01-01T00:00:00Z", "external_gate": False},
        {"action_id": "pending", "priority": 2, "action_type": "RUN_JSON_VALIDATION",
         "status": "pending", "queued_at": "2026-01-01T00:00:00Z", "external_gate": False},
    ]
    _save_queue(items)
    chosen = dequeue_next()
    assert chosen["action_id"] == "pending"


def test_dequeue_next_empty_queue_returns_none(tmp_queue, monkeypatch):
    _save_queue([])
    assert dequeue_next() is None


def test_mark_done_sets_result_path(tmp_queue, monkeypatch):
    items = [{"action_id": "q1", "status": "running", "action_type": "RUN_JSON_VALIDATION"}]
    _save_queue(items)
    mark_done("q1", result_path="some/result.json")
    loaded = _load_queue()
    assert loaded[0]["status"] == "done"
    assert loaded[0]["result_path"] == "some/result.json"


def test_mark_failed_sets_error(tmp_queue, monkeypatch):
    items = [{"action_id": "q1", "status": "running", "action_type": "RUN_JSON_VALIDATION"}]
    _save_queue(items)
    mark_failed("q1", error="something broke")
    loaded = _load_queue()
    assert loaded[0]["status"] == "failed"
    assert loaded[0]["error"] == "something broke"


# ── PRODUCT_GAP_CLASSIFICATION_READONLY in safe set ──────────────────────────

def test_product_gap_classification_in_safe_pilot_actions():
    from tools.supervisor.product_action_guard import SAFE_PRODUCT_PILOT_ACTIONS
    assert "PRODUCT_GAP_CLASSIFICATION_READONLY" in SAFE_PRODUCT_PILOT_ACTIONS


def test_product_gap_classification_not_in_forbidden():
    assert "PRODUCT_GAP_CLASSIFICATION_READONLY" not in FORBIDDEN_IN_QUEUE


# ── advisory Markdown never becomes queue item ────────────────────────────────

def test_advisory_md_not_an_action_type_in_forbidden_set():
    """Advisory Markdown file names never appear as action types in FORBIDDEN_IN_QUEUE."""
    import re
    md_pattern = re.compile(r'\.md$', re.IGNORECASE)
    for forbidden in FORBIDDEN_IN_QUEUE:
        assert not md_pattern.search(forbidden), \
            f"Forbidden action type should not be a .md file path: {forbidden}"
