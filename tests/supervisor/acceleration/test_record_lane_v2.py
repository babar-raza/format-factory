"""Tests for record_lane_execution.py v2 — R100 Train E."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from record_lane_execution import (
    new_lane,
    close_lane,
    log_command,
    close_command,
    detect_bottlenecks,
)


def test_new_lane_v2_fields():
    lane = new_lane("L1", "S1", subagent_id="agent-42", dependency_graph=["L0"])
    assert lane["subagent_id"] == "agent-42"
    assert lane["dependency_graph"] == ["L0"]
    assert lane["handoff_from"] == ""
    assert lane["handoff_to"] == ""
    assert lane["command_log"] == []
    assert lane["bottleneck_tags"] == []


def test_new_lane_handoff_from():
    lane = new_lane("L2", "S1", handoff_from="L1")
    assert lane["handoff_from"] == "L1"


def test_log_command():
    lane = new_lane("L1", "S1")
    entry = log_command(lane, "pytest tests/")
    assert entry["command"] == "pytest tests/"
    assert entry["started_at"] is not None
    assert entry["ended_at"] is None
    assert "pytest tests/" in lane["commands"]


def test_close_command():
    lane = new_lane("L1", "S1")
    log_command(lane, "pytest tests/")
    close_command(lane, "pytest tests/")
    assert lane["command_log"][0]["ended_at"] is not None


def test_close_command_no_match():
    lane = new_lane("L1", "S1")
    log_command(lane, "pytest tests/")
    close_command(lane, "dotnet test")  # no match, should not crash
    assert lane["command_log"][0]["ended_at"] is None


def test_detect_bottlenecks_slow():
    lane = new_lane("L1", "S1")
    lane["duration_seconds"] = 400
    tags = detect_bottlenecks(lane)
    assert "slow_lane" in tags
    assert "no_output" in tags  # no files changed


def test_detect_bottlenecks_blocked():
    lane = new_lane("L1", "S1")
    lane["blockers"] = ["dependency missing"]
    tags = detect_bottlenecks(lane)
    assert "blocked" in tags


def test_detect_bottlenecks_test_failures():
    lane = new_lane("L1", "S1")
    lane["tests_failed"] = 3
    tags = detect_bottlenecks(lane)
    assert "test_failures" in tags


def test_detect_bottlenecks_has_dependencies():
    lane = new_lane("L1", "S1", dependency_graph=["L0"])
    tags = detect_bottlenecks(lane)
    assert "has_dependencies" in tags


def test_close_lane_auto_detects_bottlenecks():
    lane = new_lane("L1", "S1")
    lane["tests_failed"] = 1
    closed = close_lane(lane)
    assert "test_failures" in closed["bottleneck_tags"]


def test_close_lane_handoff_to():
    lane = new_lane("L1", "S1")
    closed = close_lane(lane, handoff_to="L2")
    assert closed["handoff_to"] == "L2"


# --- v3 (R101): stream_id and raw_log_path ---


def test_new_lane_stream_id_default():
    lane = new_lane("L1", "S1")
    assert lane["stream_id"] == "mainstream"


def test_new_lane_stream_id_custom():
    lane = new_lane("L1", "S1", stream_id="acceleration")
    assert lane["stream_id"] == "acceleration"


def test_new_lane_raw_log_path():
    lane = new_lane("L1", "S1", raw_log_path="/tmp/lane-L1.log")
    assert lane["raw_log_path"] == "/tmp/lane-L1.log"


def test_new_lane_raw_log_path_default():
    lane = new_lane("L1", "S1")
    assert lane["raw_log_path"] == ""


def test_stream_id_preserved_after_close():
    lane = new_lane("L1", "S1", stream_id="supervisor")
    closed = close_lane(lane)
    assert closed["stream_id"] == "supervisor"
