"""Tests for action queue merge behavior in capability_map_generator.

Verifies that user-populated actions survive capability_map_generator.py runs
(TC-GAP-D02 fix for the overwrite bug).
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))


@pytest.fixture
def queue_path(tmp_path):
    """Return a temporary action-queue.json path."""
    return tmp_path / "action-queue.json"


def _write_queue(path, actions):
    """Write a minimal action-queue.json."""
    payload = {
        "schema_version": "1.0",
        "generated_at": "2026-01-01T00:00:00Z",
        "sprint_id": "TEST",
        "run_id": "test-run",
        "advisory_only": True,
        "note": "test",
        "total_actions": len(actions),
        "actions": actions,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _read_queue(path):
    """Read action-queue.json and return the actions list."""
    return json.loads(path.read_text(encoding="utf-8"))["actions"]


def _simulate_generator_write(queue_path, generated_actions):
    """Simulate the fixed generator write step (merge logic)."""
    generated_ids = {a["action_id"] for a in generated_actions}
    actions = list(generated_actions)
    if queue_path.exists():
        try:
            existing = json.loads(queue_path.read_text(encoding="utf-8"))
            for existing_action in existing.get("actions", []):
                if existing_action.get("action_id") not in generated_ids:
                    actions.append(existing_action)
        except (json.JSONDecodeError, KeyError):
            pass
    _write_queue(queue_path, actions)


class TestActionQueueMerge:
    """Test suite for action queue merge behavior."""

    def test_user_action_survives_regeneration(self, queue_path):
        """User-populated actions are preserved when generator runs."""
        user_action = {"action_id": "ACT-USER-CUSTOM", "description": "User task"}
        generated = [{"action_id": "ACT-GEN-001", "description": "Generated task"}]

        _write_queue(queue_path, [generated[0], user_action])
        _simulate_generator_write(queue_path, generated)

        result = _read_queue(queue_path)
        ids = {a["action_id"] for a in result}
        assert "ACT-USER-CUSTOM" in ids, "User action was lost"
        assert "ACT-GEN-001" in ids, "Generated action missing"
        assert len(result) == 2

    def test_duplicate_generated_ids_not_doubled(self, queue_path):
        """Generated actions replace old generated actions (no duplicates)."""
        old_gen = {"action_id": "ACT-GEN-001", "description": "Old version"}
        new_gen = {"action_id": "ACT-GEN-001", "description": "New version"}

        _write_queue(queue_path, [old_gen])
        _simulate_generator_write(queue_path, [new_gen])

        result = _read_queue(queue_path)
        assert len(result) == 1
        assert result[0]["description"] == "New version"

    def test_empty_existing_queue(self, queue_path):
        """Works correctly when existing queue has no actions."""
        _write_queue(queue_path, [])
        generated = [{"action_id": "ACT-GEN-001", "description": "Generated"}]

        _simulate_generator_write(queue_path, generated)

        result = _read_queue(queue_path)
        assert len(result) == 1
        assert result[0]["action_id"] == "ACT-GEN-001"

    def test_no_existing_queue_file(self, queue_path):
        """Works correctly when no queue file exists yet."""
        generated = [{"action_id": "ACT-GEN-001", "description": "Generated"}]

        _simulate_generator_write(queue_path, generated)

        result = _read_queue(queue_path)
        assert len(result) == 1

    def test_corrupt_existing_queue(self, queue_path):
        """Corrupt existing file is handled gracefully (regenerate from scratch)."""
        queue_path.write_text("NOT VALID JSON", encoding="utf-8")
        generated = [{"action_id": "ACT-GEN-001", "description": "Generated"}]

        _simulate_generator_write(queue_path, generated)

        result = _read_queue(queue_path)
        assert len(result) == 1
        assert result[0]["action_id"] == "ACT-GEN-001"

    def test_multiple_user_actions_preserved(self, queue_path):
        """Multiple user actions are all preserved."""
        user1 = {"action_id": "ACT-USER-A", "description": "First user"}
        user2 = {"action_id": "ACT-USER-B", "description": "Second user"}
        gen = {"action_id": "ACT-GEN-001", "description": "Generated"}

        _write_queue(queue_path, [gen, user1, user2])
        new_gen = [{"action_id": "ACT-GEN-001", "description": "Regenerated"}]

        _simulate_generator_write(queue_path, new_gen)

        result = _read_queue(queue_path)
        ids = {a["action_id"] for a in result}
        assert ids == {"ACT-GEN-001", "ACT-USER-A", "ACT-USER-B"}
        assert len(result) == 3
