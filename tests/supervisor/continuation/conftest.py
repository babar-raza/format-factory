"""Shared fixtures for continuation isolation tests."""
import json
import sys
from pathlib import Path

import pytest

# Add tools/supervisor to path for imports
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))


@pytest.fixture
def mock_repo(tmp_path):
    """Create a minimal mock repo structure for continuation tests."""
    supervisor_dir = tmp_path / ".local" / "supervisor"
    supervisor_dir.mkdir(parents=True)
    reports_dir = tmp_path / "reports" / "supervisor"
    reports_dir.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def write_signal(mock_repo):
    """Helper to write a continuation-signal.json in the mock repo."""
    def _write(session_id=None, autonomous_continue=True, sprint_id="test-sprint",
               iteration=0, max_iterations=12, continuation_state="CONTINUE",
               hard_stops=None):
        signal = {
            "autonomous_continue": autonomous_continue,
            "iteration": iteration,
            "max_iterations": max_iterations,
            "next_sprint_path": "reports/supervisor/next-sprint.md",
            "stop_reason": None,
            "rework_items": [],
            "safe_lanes_available": True,
            "generated_at": "2026-06-17T00:00:00",
            "source_sprint_id": sprint_id,
            "hard_stops_detected": hard_stops or [],
            "continuation_state": continuation_state,
        }
        if session_id is not None:
            signal["session_id"] = session_id
        path = mock_repo / ".local" / "supervisor" / "continuation-signal.json"
        path.write_text(json.dumps(signal, indent=2), encoding="utf-8")
        return path
    return _write


@pytest.fixture
def write_approval_gates(mock_repo):
    """Write approval-gates.md with AUTONOMOUS_CONTINUE: YES."""
    def _write(autonomous_continue=True):
        content = f"AUTONOMOUS_CONTINUE: {'YES' if autonomous_continue else 'NO'}\n"
        path = mock_repo / "reports" / "supervisor" / "approval-gates.md"
        path.write_text(content, encoding="utf-8")
        return path
    return _write


@pytest.fixture
def write_work_items(mock_repo):
    """Write next-work-items.json."""
    def _write(items=None):
        path = mock_repo / ".local" / "supervisor" / "next-work-items.json"
        path.write_text(json.dumps(items or [{"id": "test-item"}], indent=2), encoding="utf-8")
        return path
    return _write


@pytest.fixture
def full_continue_setup(write_signal, write_approval_gates, write_work_items):
    """Set up all files needed for a CONTINUE verdict."""
    def _setup(session_id=None, sprint_id="test-sprint"):
        write_signal(session_id=session_id, sprint_id=sprint_id)
        write_approval_gates(autonomous_continue=True)
        write_work_items()
    return _setup
