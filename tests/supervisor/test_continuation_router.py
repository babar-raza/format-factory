"""
Tests for continuation_router.py
Sprint: FORMAT-FACTORY-AUTONOMOUS-ORCHESTRATOR-PERSISTENT-CONTINUATION-001
"""
import json
import pytest
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))

from tools.supervisor.continuation_router import (
    ROUTE_STOP_ADVISORY,
    ROUTE_STOP_INVALID,
    ROUTE_STOP_NO_CONTINUATION,
    route,
)
from tools.supervisor.continuation_state import (
    make_active_continuation,
)

_VALID_ACTION = {
    "action_id": "test-001",
    "action_type": "RUN_JSON_VALIDATION",
    "objective": "test validation",
    "preferred_backend": "LOCAL_DETERMINISTIC",
    "fallback_backends": [],
    "target": "reports/autonomous-orchestrator/current-autonomy-baseline.json",
    "result_path": "reports/autonomous-orchestrator/proof-run/cycle-001-result.json",
    "allowed_write_roots": ["reports/autonomous-orchestrator"],
    "evidence_required": True,
    "external_gate": False,
}


@pytest.fixture
def temp_state(tmp_path, monkeypatch):
    """Redirect state file paths to temp directory."""
    monkeypatch.setattr("tools.supervisor.continuation_state.STATE_DIR", tmp_path)
    monkeypatch.setattr("tools.supervisor.continuation_state.ACTIVE_CONTINUATION_PATH",
                        tmp_path / "active-continuation.json")
    monkeypatch.setattr("tools.supervisor.continuation_state.NEXT_ACTION_PATH",
                        tmp_path / "next-action.json")
    monkeypatch.setattr("tools.supervisor.continuation_state.STOP_REASON_PATH",
                        tmp_path / "stop-reason.json")
    # NOTE: continuation_router delegates to continuation_state for paths,
    # so patching continuation_state above is sufficient.
    return tmp_path


class TestRouter:
    def test_no_continuation_stops(self, temp_state):
        # No active-continuation.json
        d = route("test-run", 0)
        assert d.decision == ROUTE_STOP_NO_CONTINUATION
        assert not d.should_dispatch

    def test_advisory_prompt_stops(self, temp_state, monkeypatch):
        cont = make_active_continuation(
            "TEST-001", "H4",
            "reports/supervisor/next-sprint.md",  # advisory!
        )
        (temp_state / "active-continuation.json").write_text(json.dumps(cont))
        monkeypatch.setattr("tools.supervisor.continuation_router.load_active_continuation",
                            lambda: cont)
        d = route("test-run", 0, next_action_override="reports/supervisor/next-sprint.md")
        assert d.decision in {ROUTE_STOP_ADVISORY, ROUTE_STOP_INVALID, ROUTE_STOP_NO_CONTINUATION}
        assert not d.should_dispatch

    def test_missing_next_action_file_stops(self, temp_state, monkeypatch):
        cont = make_active_continuation("TEST-001", "H4", ".local/supervisor/next-action.json")
        cont["autonomous_continue"] = True
        monkeypatch.setattr("tools.supervisor.continuation_router.load_active_continuation",
                            lambda: cont)
        # next-action.json does not exist → STOP_INVALID
        d = route("test-run", 0, next_action_override="reports/NONEXISTENT_xyz_abc_123.json")
        assert not d.should_dispatch

    def test_autonomous_continue_false_stops(self, temp_state, monkeypatch):
        cont = make_active_continuation("TEST-001", "H4", ".local/supervisor/next-action.json")
        cont["autonomous_continue"] = False
        monkeypatch.setattr("tools.supervisor.continuation_router.load_active_continuation",
                            lambda: cont)
        d = route("test-run", 0)
        assert not d.should_dispatch

    def test_routing_decision_has_to_dict(self, temp_state, monkeypatch):
        cont = make_active_continuation("TEST-001", "H4", ".local/supervisor/next-action.json")
        cont["autonomous_continue"] = False
        monkeypatch.setattr("tools.supervisor.continuation_router.load_active_continuation",
                            lambda: cont)
        d = route("test-run", 0)
        d_dict = d.to_dict()
        assert "decision" in d_dict
        assert "should_dispatch" in d_dict
