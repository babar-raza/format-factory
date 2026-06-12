"""Tests for record_lane_execution.py — lane execution recorder."""

import sys
import time
from pathlib import Path


# Add tools/supervisor to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from record_lane_execution import (
    new_lane,
    close_lane,
    load_ledger,
    save_ledger,
    append_lane,
    ledger_summary,
)


def test_new_lane_has_required_fields():
    lane = new_lane("LANE-001", "SPRINT-001", "GROUP-1", "claude-primary")
    assert lane["lane_id"] == "LANE-001"
    assert lane["sprint_id"] == "SPRINT-001"
    assert lane["concurrency_group"] == "GROUP-1"
    assert lane["owner"] == "claude-primary"
    assert lane["status"] == "in_progress"
    assert lane["started_at"] is not None
    assert lane["ended_at"] is None


def test_close_lane_sets_end_and_duration():
    lane = new_lane("LANE-002", "SPRINT-001")
    time.sleep(0.01)
    closed = close_lane(lane, "completed")
    assert closed["status"] == "completed"
    assert closed["ended_at"] is not None
    assert closed["duration_seconds"] is not None
    assert closed["duration_seconds"] >= 0


def test_close_lane_failed_status():
    lane = new_lane("LANE-003", "SPRINT-001")
    closed = close_lane(lane, "failed")
    assert closed["status"] == "failed"


def test_load_ledger_empty(tmp_path):
    ledger = load_ledger(tmp_path / "nonexistent.json")
    assert ledger["schema_version"] == "1.0"
    assert ledger["lanes"] == []


def test_save_and_load_ledger(tmp_path):
    ledger_path = tmp_path / "ledger.json"
    ledger = {"schema_version": "1.0", "lanes": [{"lane_id": "L1"}]}
    save_ledger(ledger_path, ledger)
    loaded = load_ledger(ledger_path)
    assert loaded["lanes"][0]["lane_id"] == "L1"


def test_append_lane_new(tmp_path):
    ledger_path = tmp_path / "ledger.json"
    lane = new_lane("LANE-A", "SPRINT-X")
    result = append_lane(ledger_path, lane)
    assert len(result["lanes"]) == 1
    assert result["lanes"][0]["lane_id"] == "LANE-A"


def test_append_lane_update(tmp_path):
    ledger_path = tmp_path / "ledger.json"
    lane1 = new_lane("LANE-B", "SPRINT-X")
    append_lane(ledger_path, lane1)
    lane1["status"] = "completed"
    result = append_lane(ledger_path, lane1)
    assert len(result["lanes"]) == 1
    assert result["lanes"][0]["status"] == "completed"


def test_append_multiple_lanes(tmp_path):
    ledger_path = tmp_path / "ledger.json"
    append_lane(ledger_path, new_lane("L1", "S1"))
    append_lane(ledger_path, new_lane("L2", "S1"))
    append_lane(ledger_path, new_lane("L3", "S1"))
    ledger = load_ledger(ledger_path)
    assert len(ledger["lanes"]) == 3


def test_ledger_summary():
    ledger = {
        "lanes": [
            {"lane_id": "L1", "status": "completed", "duration_seconds": 10,
             "test_count": 5, "tests_passed": 5, "files_changed": ["a.py"]},
            {"lane_id": "L2", "status": "completed", "duration_seconds": 20,
             "test_count": 3, "tests_passed": 2, "files_changed": ["b.py"]},
            {"lane_id": "L3", "status": "blocked", "duration_seconds": None,
             "test_count": 0, "tests_passed": 0, "files_changed": []},
        ]
    }
    s = ledger_summary(ledger)
    assert s["lane_count"] == 3
    assert s["status_counts"]["completed"] == 2
    assert s["status_counts"]["blocked"] == 1
    assert s["total_duration_seconds"] == 30
    assert s["total_tests"] == 8
    assert s["total_tests_passed"] == 7
    assert s["total_files_changed"] == 2


def test_ledger_summary_empty():
    s = ledger_summary({"lanes": []})
    assert s["lane_count"] == 0
    assert s["total_duration_seconds"] == 0
