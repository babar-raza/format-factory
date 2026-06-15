"""Tests for action queue population from gap ledger.

Rework: TC-GAP-D02 — proves that action queue can be populated
from gap ledger data with correct structure, priorities, and counts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.action_queue import (
    make_queue_item,
    enqueue,
    _load_queue,
    _save_queue,
    STREAM_PRODUCT,
    STATUS_PENDING,
    STATUS_BLOCKED,
    FORBIDDEN_IN_QUEUE,
)


@pytest.fixture
def tmp_queue(tmp_path, monkeypatch):
    """Redirect queue to a temp file."""
    q = tmp_path / "action-queue.jsonl"
    monkeypatch.setattr("tools.supervisor.action_queue.QUEUE_PATH", q)
    return q


def _make_gap_action(gap_id: str, fmt: str, cap: str, priority: int = 5):
    return make_queue_item(
        action_type="PRODUCT_GAP_CLOSURE",
        stream=STREAM_PRODUCT,
        priority=priority,
        target=f"{fmt}/{cap}",
        objective=f"Close gap {gap_id}: {fmt} {cap}",
        gap_id=gap_id,
    )


class TestActionQueuePopulation:
    def test_populate_multiple_actions_from_gaps(self, tmp_queue):
        """Populate queue with 5+ actions derived from gap ledger entries."""
        gaps = [
            ("GAP-FODS-COMM-LOAD-001", "FODS", "Load", 1),
            ("GAP-FODT-COMM-LOAD-001", "FODT", "Load", 1),
            ("GAP-Gnumeric-FOSS-LOAD-001", "Gnumeric", "Load", 2),
            ("GAP-SYLK-FOSS-PARSE-001", "SYLK", "Parse", 3),
            ("GAP-ABW-FOSS-LOAD-001", "ABW", "Load", 3),
            ("GAP-ZST-FOSS-COMPRESS-001", "ZST", "Compress", 4),
        ]
        ids = []
        for gap_id, fmt, cap, prio in gaps:
            item = _make_gap_action(gap_id, fmt, cap, prio)
            aid = enqueue(item)
            ids.append(aid)

        items = _load_queue()
        assert len(items) == 6, f"Expected 6 queued items, got {len(items)}"
        assert all(i["action_type"] == "PRODUCT_GAP_CLOSURE" for i in items)
        assert all(i["stream"] == STREAM_PRODUCT for i in items)
        assert all(i["status"] == STATUS_PENDING for i in items)

    def test_priority_ordering(self, tmp_queue):
        """Higher-priority items (lower number) come first when sorted."""
        enqueue(_make_gap_action("G-1", "FODS", "Load", 1))
        enqueue(_make_gap_action("G-2", "ABW", "Load", 5))
        enqueue(_make_gap_action("G-3", "FODT", "Load", 2))

        items = _load_queue()
        sorted_items = sorted(items, key=lambda i: i["priority"])
        assert sorted_items[0]["gap_id"] == "G-1"
        assert sorted_items[1]["gap_id"] == "G-3"
        assert sorted_items[2]["gap_id"] == "G-2"

    def test_forbidden_action_types_rejected(self, tmp_queue):
        """FORBIDDEN_IN_QUEUE action types raise ValueError."""
        for forbidden in ["GIT_PUSH", "GIT_COMMIT", "GATE_11_APPROVAL"]:
            item = make_queue_item(action_type=forbidden)
            with pytest.raises(ValueError, match="Forbidden"):
                enqueue(item)
        assert len(_load_queue()) == 0

    def test_external_gate_items_blocked(self, tmp_queue):
        """Items with external_gate=True are pre-blocked."""
        item = make_queue_item(
            action_type="PRODUCT_GAP_CLOSURE",
            external_gate=True,
            objective="Needs human approval",
        )
        enqueue(item)
        items = _load_queue()
        assert items[0]["status"] == STATUS_BLOCKED

    def test_queue_persists_as_jsonl(self, tmp_queue):
        """Queue file is valid JSONL with one JSON object per line."""
        enqueue(_make_gap_action("G-1", "CSV", "Probe", 2))
        enqueue(_make_gap_action("G-2", "DIF", "Load", 3))

        lines = tmp_queue.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        for line in lines:
            obj = json.loads(line)
            assert "action_id" in obj
            assert "action_type" in obj
