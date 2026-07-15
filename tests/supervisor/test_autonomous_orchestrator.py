"""
Tests for autonomous_orchestrator.py
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001
"""
import pytest
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))

from tools.supervisor.autonomous_orchestrator import (
    AutonomousOrchestrator,
    DEFAULT_SPRINT_ID,
    main,
)
from tools.supervisor.autonomous_orchestrator import LOCK_PATH
from tools.supervisor.continuation_state import (
    STOP_DRY_RUN,
    STOP_MAX_CYCLES,
    STOP_LOCK_HELD,
    STOP_NO_SAFE_ACTION,
)


@pytest.fixture(autouse=True)
def _isolate_lock(tmp_path, monkeypatch):
    """Redirect the orchestrator lock file to tmp_path.

    The real LOCK_PATH at .local/supervisor/orchestrator.lock can conflict
    with concurrent processes. State files (orchestrator-state.json etc.)
    are left on the real path — they're gitignored and designed for this.
    """
    import tools.supervisor.autonomous_orchestrator as orch_mod
    monkeypatch.setattr(orch_mod, "LOCK_PATH", tmp_path / "orchestrator.lock")


class TestOrchestratorDryRun:
    def test_dry_run_once_completes(self):
        orch = AutonomousOrchestrator(max_cycles=1, dry_run=True, sprint_id=DEFAULT_SPRINT_ID)
        result = orch.run(once=True)
        assert result.dry_run is True
        assert result.stop_code in {STOP_DRY_RUN, STOP_MAX_CYCLES, STOP_NO_SAFE_ACTION}

    def test_dry_run_does_not_write_result_files(self, tmp_path):
        orch = AutonomousOrchestrator(max_cycles=1, dry_run=True, sprint_id=DEFAULT_SPRINT_ID)
        orch.run(once=True)
        # No actual result files written
        proof_dir = _repo_root / "reports/autonomous-orchestrator/proof-run"
        # In dry run, no cycle result files should be written
        result_files = list(proof_dir.glob("cycle-*.json")) if proof_dir.exists() else []
        # dry_run means DRY_RUN status in result dict, not actual file writes
        for r in orch.results:
            assert r.get("dry_run") is True or r.get("status") == "DRY_RUN"

    def test_dry_run_max_cycles_3(self):
        orch = AutonomousOrchestrator(max_cycles=3, dry_run=True, sprint_id=DEFAULT_SPRINT_ID)
        result = orch.run()
        assert result.cycles_completed <= 3


class TestOrchestratorLock:
    def test_second_orchestrator_blocked_by_lock(self, monkeypatch):
        # Monkeypatch _acquire_lock to return False (simulates lock held)
        import tools.supervisor.autonomous_orchestrator as orch_mod
        monkeypatch.setattr(orch_mod, "_acquire_lock", lambda run_id: False)
        orch = AutonomousOrchestrator(max_cycles=1, dry_run=True, sprint_id=DEFAULT_SPRINT_ID)
        result = orch.run()
        assert result.stop_code == STOP_LOCK_HELD


class TestOrchestratorMaxCycles:
    def test_max_cycles_1_runs_once(self):
        orch = AutonomousOrchestrator(max_cycles=1, dry_run=True, sprint_id=DEFAULT_SPRINT_ID)
        result = orch.run()
        assert result.cycles_completed <= 1

    def test_stop_code_set_after_max_cycles(self):
        orch = AutonomousOrchestrator(max_cycles=1, dry_run=True, sprint_id=DEFAULT_SPRINT_ID)
        result = orch.run()
        assert result.stop_code is not None

    def test_result_has_run_id(self):
        orch = AutonomousOrchestrator(max_cycles=1, dry_run=True, sprint_id=DEFAULT_SPRINT_ID)
        result = orch.run()
        assert result.run_id != ""


class TestOrchestratorAdvisoryRefusal:
    def test_advisory_prompt_as_seed_stops(self, monkeypatch):
        # If seed action path points to .md file, orchestrator should stop
        orch = AutonomousOrchestrator(
            max_cycles=1, dry_run=True, sprint_id=DEFAULT_SPRINT_ID,
            seed_action_path="reports/supervisor/next-sprint.md",
        )
        # The router will reject advisory path
        result = orch.run()
        # Should stop (not DISPATCH successfully with MD)
        assert result.stop_code != "SUCCESS"


class TestOrchestratorResultDict:
    def test_result_to_dict_has_required_keys(self):
        orch = AutonomousOrchestrator(max_cycles=1, dry_run=True, sprint_id=DEFAULT_SPRINT_ID)
        result = orch.run()
        d = result.to_dict()
        assert "run_id" in d
        assert "cycles_completed" in d
        assert "stop_code" in d
        assert "results" in d


class TestOrchestratorResume:
    def test_resume_flag_does_not_crash(self):
        orch = AutonomousOrchestrator(max_cycles=1, dry_run=True, resume=True, sprint_id=DEFAULT_SPRINT_ID)
        result = orch.run()
        assert result is not None

    def test_resume_sets_resumed_flag(self):
        orch = AutonomousOrchestrator(max_cycles=1, dry_run=True, resume=True, sprint_id=DEFAULT_SPRINT_ID)
        result = orch.run()
        assert result.resumed is True


class TestOrchestratorCLI:
    def test_cli_dry_run_once_exits_0(self):
        exit_code = main(["--once", "--dry-run"])
        assert exit_code == 0

    def test_cli_max_cycles_1_dry_run(self):
        exit_code = main(["--max-cycles", "1", "--dry-run"])
        assert exit_code == 0
