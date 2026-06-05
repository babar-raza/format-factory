"""TC-TEST-003: AI Learning Loop tests."""

import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent


@pytest.fixture
def loop_dir(tmp_path):
    return tmp_path / "learning"


def test_loop_produces_jsonl(loop_dir):
    from tools.supervisor.ai_learning_loop import run_loop
    result = run_loop("test-sprint", loop_dir)
    out = loop_dir / "sprint-learnings.jsonl"
    assert out.exists()
    assert result["learning_count"] >= 3


def test_all_entries_are_valid_json(loop_dir):
    from tools.supervisor.ai_learning_loop import run_loop
    run_loop("test-sprint", loop_dir)
    out = loop_dir / "sprint-learnings.jsonl"
    for line in out.read_text().splitlines():
        entry = json.loads(line)
        assert entry.get("authority_state") == "ai_draft"
        assert entry.get("archived_to_memory") is False


def test_all_categories_valid(loop_dir):
    from tools.supervisor.ai_learning_loop import run_loop, _VALID_CATEGORIES
    run_loop("test-sprint", loop_dir)
    out = loop_dir / "sprint-learnings.jsonl"
    for line in out.read_text().splitlines():
        entry = json.loads(line)
        assert entry["category"] in _VALID_CATEGORIES, f"Invalid category: {entry['category']}"


def test_round_trip_readable(loop_dir):
    from tools.supervisor.ai_learning_loop import run_loop
    run_loop("test-sprint", loop_dir)
    out = loop_dir / "sprint-learnings.jsonl"
    entries = [json.loads(line) for line in out.read_text().splitlines()]
    assert len(entries) >= 3
    for e in entries:
        assert "sprint_id" in e
        assert "description" in e
        assert "recommended_action" in e
