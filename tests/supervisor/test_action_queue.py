"""
Tests for tools/supervisor/action_queue.py
Sprint: FORMAT-FACTORY-AUTONOMOUS-SYSTEM-ACCEPTANCE-PERSISTENT-PRODUCT-LOOP-001
"""
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.supervisor.action_queue import (
    enqueue,
    dequeue_next,
    mark_done,
    mark_failed,
    mark_blocked,
    get_queue_stats,
    seed_autonomy_queue,
    FORBIDDEN_IN_QUEUE,
    STATUS_PENDING,
    STATUS_DONE,
    STATUS_FAILED,
    STATUS_BLOCKED,
)


@pytest.fixture
def tmp_queue(tmp_path, monkeypatch):
    """Redirect queue writes to a temp directory."""
    q_path = tmp_path / "action-queue.jsonl"
    monkeypatch.setattr("tools.supervisor.action_queue.QUEUE_PATH", q_path)
    return q_path


# ── Basic enqueue/dequeue ──────────────────────────────────────────────────

def test_enqueue_returns_id(tmp_queue):
    action_id = enqueue({"action_type": "RUN_JSON_VALIDATION", "target_path": "foo.json"})
    assert isinstance(action_id, str) and len(action_id) > 0


def test_enqueue_then_dequeue(tmp_queue):
    enqueue({"action_type": "RUN_JSON_VALIDATION", "target_path": "foo.json"})
    item = dequeue_next()
    assert item is not None
    assert item["action_type"] == "RUN_JSON_VALIDATION"
    assert item["status"] == "running"


def test_dequeue_empty_returns_none(tmp_queue):
    result = dequeue_next()
    assert result is None


def test_enqueue_multiple_fifo_order(tmp_queue):
    enqueue({"action_type": "RUN_JSON_VALIDATION", "target_path": "a.json"})
    enqueue({"action_type": "RUN_YAML_VALIDATION", "target_path": "b.yaml"})
    first = dequeue_next()
    second = dequeue_next()
    assert first["action_type"] == "RUN_JSON_VALIDATION"
    assert second["action_type"] == "RUN_YAML_VALIDATION"


# ── Status transitions ─────────────────────────────────────────────────────

def test_mark_done(tmp_queue):
    action_id = enqueue({"action_type": "RUN_JSON_VALIDATION", "target_path": "foo.json"})
    dequeue_next()
    mark_done(action_id, result_path="some/result.json")
    stats = get_queue_stats()
    assert stats[STATUS_DONE] == 1
    assert stats[STATUS_PENDING] == 0


def test_mark_failed(tmp_queue):
    action_id = enqueue({"action_type": "RUN_JSON_VALIDATION", "target_path": "foo.json"})
    dequeue_next()
    mark_failed(action_id, error="parse error")
    stats = get_queue_stats()
    assert stats[STATUS_FAILED] == 1


def test_mark_blocked(tmp_queue):
    action_id = enqueue({"action_type": "RUN_JSON_VALIDATION", "target_path": "foo.json"})
    dequeue_next()
    mark_blocked(action_id, reason="credential required")
    stats = get_queue_stats()
    assert stats[STATUS_BLOCKED] == 1


def test_stats_empty_queue(tmp_queue):
    stats = get_queue_stats()
    assert stats[STATUS_PENDING] == 0
    assert stats[STATUS_DONE] == 0


# ── Forbidden action types ─────────────────────────────────────────────────

@pytest.mark.parametrize("forbidden_type", [
    "GIT_PUSH",
    "GIT_COMMIT",
    "GATE_11_APPROVAL",
    "PACKAGE_PUBLISH",
    "MCP_ACTIVATE",
    "MUTATE_POC_TARGETS",
])
def test_forbidden_action_rejected(tmp_queue, forbidden_type):
    with pytest.raises(ValueError):
        enqueue({"action_type": forbidden_type})


def test_forbidden_set_is_complete(tmp_queue):
    required = {"GIT_PUSH", "GIT_COMMIT", "GATE_8_APPROVAL", "GATE_11_APPROVAL", "PACKAGE_PUBLISH", "MCP_ACTIVATE"}
    assert required.issubset(FORBIDDEN_IN_QUEUE)


# ── Seed autonomy queue ────────────────────────────────────────────────────

def test_seed_autonomy_queue_returns_ids(tmp_queue):
    ids = seed_autonomy_queue("TEST-SPRINT-001")
    assert isinstance(ids, list)
    assert len(ids) >= 1


def test_seed_queue_items_are_safe(tmp_queue):
    seed_autonomy_queue("TEST-SPRINT-001")
    # All seeded items should be dequeue-able (none blocked)
    item = dequeue_next()
    assert item is not None
    assert item["action_type"] not in FORBIDDEN_IN_QUEUE


def test_seed_queue_persists(tmp_queue):
    seed_autonomy_queue("TEST-SPRINT-001")
    stats = get_queue_stats()
    assert stats[STATUS_PENDING] + stats.get("running", 0) >= 1


# ── Queue survives process restart ─────────────────────────────────────────

def test_queue_durability(tmp_queue):
    """JSONL queue should persist across multiple function calls (simulates restart)."""
    enqueue({"action_type": "RUN_JSON_VALIDATION", "target_path": "foo.json"})
    # Re-read stats without clearing
    stats1 = get_queue_stats()
    assert stats1[STATUS_PENDING] >= 1
    # Dequeue and verify the item is still the one we enqueued
    item = dequeue_next()
    assert item["target_path"] == "foo.json"
