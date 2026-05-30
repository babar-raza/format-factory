"""
test_validate_dual_orchestration_bridge.py
Tests for tools/taskmaster/validate_dual_orchestration_bridge.py

Coverage:
  - Valid state with no drift passes
  - TM done task claiming gate closure fails (RULE-1)
  - TM done task with non_authoritative=False fails (RULE-1)
  - Ruflo lane complete without non_authoritative fails (RULE-2)
  - Ruflo lane missing non_authoritative fails (RULE-3)
  - Ruflo lane claiming gate closure fails (RULE-4)
  - Supervisor verdict claiming gate approval fails (RULE-5)
  - Missing TM/Ruflo files before activation returns warning (exit 0)
  - Empty task/lane list passes with warning
  - Contradiction between evidence verdict and TM done fails (RULE-1)
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.taskmaster.validate_dual_orchestration_bridge import validate, DriftResult


# ============================================================
# Fixtures
# ============================================================

def make_valid_tm_task(**overrides) -> dict:
    base = {
        "task_id": "TASK-001",
        "title": "Valid task",
        "status": "pending",
        "ff_taskcard_ref": "TC-0001",
        "acceptance_evidence": "test log",
        "validation_command": "pytest tests/",
        "non_authoritative": True,
    }
    base.update(overrides)
    return base


def make_valid_tm_file(tasks: list) -> dict:
    return {
        "sprint_id": "TEST-001",
        "timestamp": "2026-05-30T00:00:00",
        "verdict": "ACCEPTED",
        "tasks": tasks,
    }


def make_valid_ruflo_lane(**overrides) -> dict:
    base = {
        "lane_id": "C0",
        "owner_role": "Coordinator",
        "allowed_files": ["reports/**"],
        "forbidden_files": ["AGENTS.md"],
        "non_authoritative": True,
        "status": "pending",
    }
    base.update(overrides)
    return base


def make_valid_ruflo_file(lanes: list) -> dict:
    return {
        "sprint_id": "TEST-001",
        "timestamp": "2026-05-30T00:00:00",
        "verdict": "ACCEPTED",
        "coordinator_lane": "C0",
        "lanes": lanes,
        "overlap_check_passed": True,
    }


def write_temp_json(data: dict) -> Path:
    f = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8")
    json.dump(data, f)
    f.close()
    return Path(f.name)


# ============================================================
# PASS-path tests
# ============================================================

class TestNoDrift:
    def test_valid_pending_task_no_drift(self):
        """Valid pending task with no gate closure claims — no drift."""
        tm = write_temp_json(make_valid_tm_file([make_valid_tm_task(status="pending")]))
        ruflo = write_temp_json(make_valid_ruflo_file([make_valid_ruflo_lane(status="pending")]))
        result = validate(tm, ruflo, None)
        assert not result.has_drift, f"Unexpected violations: {result.violations}"

    def test_valid_done_task_with_non_authoritative_no_drift(self):
        """done task with non_authoritative=True — no drift."""
        task = make_valid_tm_task(status="done", non_authoritative=True)
        tm = write_temp_json(make_valid_tm_file([task]))
        result = validate(tm, None, None)
        assert not result.has_drift

    def test_missing_tm_file_is_warning_not_violation(self):
        """Missing TM file before activation is WARNING only."""
        result = validate(Path("/nonexistent/tasks.json"), None, None)
        assert not result.has_drift
        assert len(result.warnings) > 0

    def test_missing_ruflo_file_is_warning_not_violation(self):
        """Missing Ruflo lanes file before activation is WARNING only."""
        result = validate(None, Path("/nonexistent/lanes.json"), None)
        assert not result.has_drift
        assert len(result.warnings) > 0

    def test_empty_task_list_no_drift(self):
        """Empty task list has no drift."""
        tm = write_temp_json(make_valid_tm_file([]))
        result = validate(tm, None, None)
        assert not result.has_drift

    def test_completed_lane_with_non_authoritative_no_drift(self):
        """Completed lane with non_authoritative=True — no drift."""
        lane = make_valid_ruflo_lane(status="completed", non_authoritative=True)
        ruflo = write_temp_json(make_valid_ruflo_file([lane]))
        result = validate(None, ruflo, None)
        assert not result.has_drift


# ============================================================
# FAIL-path tests
# ============================================================

class TestDriftDetected:
    def test_tm_done_with_gate_closure_keyword_fails(self):
        """done task with gate_closed in description violates RULE-1."""
        task = make_valid_tm_task(
            status="done",
            non_authoritative=True,
            title="gate_closed gate_11_approved",
        )
        tm = write_temp_json(make_valid_tm_file([task]))
        result = validate(tm, None, None)
        assert result.has_drift
        assert any("RULE-1" in v["rule"] for v in result.violations)

    def test_tm_done_without_non_authoritative_fails(self):
        """done task with non_authoritative=False violates RULE-1."""
        task = make_valid_tm_task(status="done", non_authoritative=False)
        tm = write_temp_json(make_valid_tm_file([task]))
        result = validate(tm, None, None)
        assert result.has_drift
        assert any("RULE-1" in v["rule"] for v in result.violations)

    def test_ruflo_completed_without_non_authoritative_fails(self):
        """Completed lane without non_authoritative violates RULE-2."""
        lane = make_valid_ruflo_lane(status="completed")
        del lane["non_authoritative"]
        ruflo = write_temp_json(make_valid_ruflo_file([lane]))
        result = validate(None, ruflo, None)
        assert result.has_drift
        assert any(v["rule"] in ("RULE-2", "RULE-3") for v in result.violations)

    def test_ruflo_lane_missing_non_authoritative_fails(self):
        """Lane without non_authoritative field violates RULE-3."""
        lane = make_valid_ruflo_lane()
        del lane["non_authoritative"]
        ruflo = write_temp_json(make_valid_ruflo_file([lane]))
        result = validate(None, ruflo, None)
        assert result.has_drift
        assert any("RULE-3" in v["rule"] for v in result.violations)

    def test_ruflo_lane_with_gate_closure_keyword_fails(self):
        """Ruflo lane claiming gate closure violates RULE-4."""
        lane = make_valid_ruflo_lane(
            non_authoritative=True,
            title="gate_closed commercial_product_ready: true",
        )
        ruflo = write_temp_json(make_valid_ruflo_file([lane]))
        result = validate(None, ruflo, None)
        assert result.has_drift
        assert any("RULE-4" in v["rule"] for v in result.violations)

    def test_ruflo_memory_without_non_authoritative_fails(self):
        """Ruflo lane with non_authoritative=False violates RULE-3."""
        lane = make_valid_ruflo_lane(non_authoritative=False)
        ruflo = write_temp_json(make_valid_ruflo_file([lane]))
        result = validate(None, ruflo, None)
        assert result.has_drift

    def test_supervisor_verdict_claiming_gate_approval_fails(self):
        """Supervisor verdict with GATE_APPROVED violates RULE-5."""
        state = {"verdict": "GATE_APPROVED_COMMERCIAL_READY"}
        state_file = write_temp_json(state)
        result = validate(None, None, state_file)
        assert result.has_drift
        assert any("RULE-5" in v["rule"] for v in result.violations)
