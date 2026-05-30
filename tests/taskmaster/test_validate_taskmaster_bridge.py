"""
test_validate_taskmaster_bridge.py
Tests for tools/taskmaster/validate_taskmaster_bridge.py

Coverage:
  - Valid task passes
  - Missing FF bridge ref fails
  - Missing acceptance_evidence fails
  - Missing validation_command fails
  - Blocked task without blocker_type fails
  - Work-ahead without non_authoritative fails
  - Missing tasks file returns warning (exit 0) before activation
  - Empty task list passes with warning
  - Invalid status fails
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.taskmaster.validate_taskmaster_bridge import validate, ValidationResult


# ============================================================
# Test fixtures
# ============================================================

def make_valid_task(**overrides) -> dict:
    """Return a minimal valid task."""
    task = {
        "task_id": "TASK-001",
        "title": "Test task",
        "status": "pending",
        "ff_taskcard_ref": "TC-0001",
        "supervisor_task_ref": "TC-SUP-007",
        "acceptance_evidence": "reports/supervisor/evidence-review.json validated",
        "validation_command": "python -m pytest tests/taskmaster/ -v",
    }
    task.update(overrides)
    return task


def make_valid_file(tasks: list | None = None) -> dict:
    """Return a minimal valid task export file."""
    return {
        "sprint_id": "TEST-SPRINT-001",
        "timestamp": "2026-05-30T00:00:00",
        "verdict": "ACCEPTED",
        "tasks": tasks if tasks is not None else [make_valid_task()],
    }


def write_temp_json(data: dict) -> Path:
    """Write data to a temp file and return its path."""
    f = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8")
    json.dump(data, f)
    f.close()
    return Path(f.name)


# ============================================================
# PASS-path tests
# ============================================================

class TestValidTask:
    def test_valid_task_passes(self):
        """A valid task with all required fields should pass."""
        path = write_temp_json(make_valid_file([make_valid_task()]))
        result = validate(path)
        assert result.valid, f"Expected valid but got errors: {result.errors}"
        assert result.summary()["error_count"] == 0

    def test_valid_task_with_ff_gate_ref(self):
        """Valid task with ff_gate_ref instead of ff_taskcard_ref passes."""
        task = make_valid_task()
        del task["ff_taskcard_ref"]
        task["ff_gate_ref"] = "gate_10"
        path = write_temp_json(make_valid_file([task]))
        result = validate(path)
        assert result.valid

    def test_valid_task_with_ff_doc_ref(self):
        """Valid task with ff_doc_ref passes."""
        task = make_valid_task()
        del task["ff_taskcard_ref"]
        task["ff_doc_ref"] = "docs/taskmaster/taskmaster-supervisor-integration.md"
        path = write_temp_json(make_valid_file([task]))
        result = validate(path)
        assert result.valid

    def test_empty_task_list_passes_with_warning(self):
        """Empty task list should pass with a warning."""
        path = write_temp_json(make_valid_file([]))
        result = validate(path)
        assert result.valid
        assert len(result.warnings) > 0

    def test_missing_file_returns_warning_not_error(self):
        """Missing task file before activation is WARNING only (not failure)."""
        result = validate(Path("/nonexistent/path/tasks.json"))
        assert result.valid, "Missing file should be WARNING not ERROR (pre-activation)"
        assert len(result.warnings) > 0

    def test_done_task_with_non_authoritative_passes(self):
        """done task with non_authoritative=True passes."""
        task = make_valid_task(status="done", non_authoritative=True)
        path = write_temp_json(make_valid_file([task]))
        result = validate(path)
        assert result.valid


# ============================================================
# FAIL-path tests
# ============================================================

class TestMissingBridgeRef:
    def test_missing_all_ff_refs_fails(self):
        """Task with no FF bridge ref fails."""
        task = make_valid_task()
        del task["ff_taskcard_ref"]
        path = write_temp_json(make_valid_file([task]))
        result = validate(path)
        assert not result.valid
        assert any("bridge reference" in e for e in result.errors)

    def test_missing_acceptance_evidence_fails(self):
        """Task with no acceptance_evidence fails."""
        task = make_valid_task()
        task["acceptance_evidence"] = ""
        path = write_temp_json(make_valid_file([task]))
        result = validate(path)
        assert not result.valid
        assert any("acceptance_evidence" in e for e in result.errors)

    def test_missing_validation_command_fails(self):
        """Task with no validation_command fails."""
        task = make_valid_task()
        task["validation_command"] = ""
        path = write_temp_json(make_valid_file([task]))
        result = validate(path)
        assert not result.valid
        assert any("validation_command" in e for e in result.errors)

    def test_blocked_without_blocker_type_fails(self):
        """Blocked task without blocker_type fails."""
        task = make_valid_task(status="blocked")
        path = write_temp_json(make_valid_file([task]))
        result = validate(path)
        assert not result.valid
        assert any("blocker_type" in e for e in result.errors)

    def test_evidence_blocked_without_blocker_type_fails(self):
        """evidence-blocked task without blocker_type fails."""
        task = make_valid_task(status="evidence-blocked")
        path = write_temp_json(make_valid_file([task]))
        result = validate(path)
        assert not result.valid

    def test_done_without_non_authoritative_fails(self):
        """done task with non_authoritative=False fails (TM done ≠ FF gate closed)."""
        task = make_valid_task(status="done", non_authoritative=False)
        path = write_temp_json(make_valid_file([task]))
        result = validate(path)
        assert not result.valid
        assert any("non_authoritative" in e or "gate closed" in e for e in result.errors)

    def test_invalid_status_fails(self):
        """Task with invalid status fails."""
        task = make_valid_task(status="flying")
        path = write_temp_json(make_valid_file([task]))
        result = validate(path)
        assert not result.valid
        assert any("status" in e for e in result.errors)

    def test_invalid_json_fails(self):
        """Malformed JSON fails."""
        f = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w")
        f.write("{ not valid json }")
        f.close()
        result = validate(Path(f.name))
        assert not result.valid
        assert any("Invalid JSON" in e or "JSON" in e for e in result.errors)
