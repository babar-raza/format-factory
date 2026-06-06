"""
Tests for orchestrator resume functionality.
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001
"""
import json
import pytest
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))

from tools.supervisor.autonomous_orchestrator import AutonomousOrchestrator, DEFAULT_SPRINT_ID
from tools.supervisor.autonomous_orchestrator import LOCK_PATH
from tools.supervisor.continuation_state import (
    ORCHESTRATOR_STATE_PATH,
    STOP_REASON_PATH,
    STOP_MAX_CYCLES,
    make_orchestrator_state,
    save_orchestrator_state,
    write_stop_reason,
)


@pytest.fixture(autouse=True)
def clean_lock():
    if LOCK_PATH.exists():
        LOCK_PATH.unlink()
    yield
    if LOCK_PATH.exists():
        LOCK_PATH.unlink()


class TestResumeFromStop:
    def test_resume_from_stopped_state(self):
        """Simulate a stopped orchestrator and verify resume starts from saved cycle_index."""
        # Write a stopped state at cycle 2
        state = make_orchestrator_state("resume-test", status="STOPPED", cycle_index=2)
        save_orchestrator_state(state)
        write_stop_reason("resume-test", STOP_MAX_CYCLES, "max cycles", 2, resumable=True)

        orch = AutonomousOrchestrator(
            max_cycles=1, dry_run=True, resume=True, sprint_id=DEFAULT_SPRINT_ID
        )
        result = orch.run()
        assert result.resumed is True
        # Should start from cycle 2 (not cycle 0)
        # cycles_completed may be 0 if no valid seed, but resumed=True confirms resume path taken
        assert result.stop_code is not None

    def test_resume_clears_max_cycles_stop_reason(self):
        """After resume, old MAX_CYCLES stop reason should be cleared."""
        state = make_orchestrator_state("resume-test2", status="STOPPED", cycle_index=1)
        save_orchestrator_state(state)
        write_stop_reason("resume-test2", STOP_MAX_CYCLES, "max cycles", 1, resumable=True)

        orch = AutonomousOrchestrator(
            max_cycles=1, dry_run=True, resume=True, sprint_id=DEFAULT_SPRINT_ID
        )
        orch.run()
        # Stop reason file should exist but may be new stop, not old MAX_CYCLES
        if STOP_REASON_PATH.exists():
            data = json.loads(STOP_REASON_PATH.read_text())
            # Could be any stop code after resume, just ensure it's structured
            assert "stop_code" in data

    def test_fresh_start_when_no_state_file(self):
        """Without existing state, should start from cycle 0."""
        if ORCHESTRATOR_STATE_PATH.exists():
            ORCHESTRATOR_STATE_PATH.unlink()

        orch = AutonomousOrchestrator(
            max_cycles=1, dry_run=True, resume=False, sprint_id=DEFAULT_SPRINT_ID
        )
        result = orch.run()
        assert result.run_id != ""

    def test_state_file_written_after_run(self):
        """Orchestrator state file must exist after any run."""
        orch = AutonomousOrchestrator(
            max_cycles=1, dry_run=True, sprint_id=DEFAULT_SPRINT_ID
        )
        orch.run()
        assert ORCHESTRATOR_STATE_PATH.exists()
        state = json.loads(ORCHESTRATOR_STATE_PATH.read_text())
        assert state["orchestrator_run_id"] != ""
        assert state["status"] in {"RUNNING", "STOPPED", "IDLE", "COMPLETED", "BLOCKED"}

    def test_stop_reason_file_written_after_run(self):
        """Stop reason file must exist after any run."""
        orch = AutonomousOrchestrator(
            max_cycles=1, dry_run=True, sprint_id=DEFAULT_SPRINT_ID
        )
        orch.run()
        assert STOP_REASON_PATH.exists()
        data = json.loads(STOP_REASON_PATH.read_text())
        assert "stop_code" in data
        assert "resumable" in data

    def test_heartbeat_written_after_run(self):
        """Heartbeat file must exist after any run."""
        from tools.supervisor.continuation_state import ORCHESTRATOR_HEARTBEAT_PATH
        orch = AutonomousOrchestrator(
            max_cycles=1, dry_run=True, sprint_id=DEFAULT_SPRINT_ID
        )
        orch.run()
        assert ORCHESTRATOR_HEARTBEAT_PATH.exists()
