"""
Tests for post_sprint_loop_controller.py — state machine transitions.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from post_sprint_loop_controller import (  # noqa: E402
    DEFAULT_MAX_LOOPS,
    INVALID_FINAL_STATES,
    VALID_STATES,
    VALID_TRANSITIONS,
    classify_and_decide,
    get_next_stages,
    init_loop,
    run_loop_dry,
    transition_to,
)


@pytest.fixture
def loop_root(tmp_path: Path):
    """Create a temporary repo root with .local/supervisor/ directory."""
    (tmp_path / ".local" / "supervisor").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def stage3_all_green(tmp_path: Path) -> Path:
    """Create a valid all-green Stage 3 output file."""
    p = tmp_path / "stage3-all-green.json"
    p.write_text(json.dumps({
        "sprint_id": "TEST",
        "timestamp": "2026-06-15T00:00:00Z",
        "execution_results": [{
            "taskcard_id": "TC-001",
            "status": "COMPLETED",
            "quality_scores": {
                "correctness": 5, "test_coverage": 5, "evidence_completeness": 5,
                "code_quality": 5, "schema_compliance": 5, "governance_compliance": 5,
                "path_discipline": 5, "documentation": 5, "idempotency": 5,
                "regression_safety": 5, "performance": 5, "error_handling": 5,
                "integration_consistency": 5, "evidence_traceability": 5,
                "acceptance_criteria_met": 5,
            },
            "evidence_paths": ["evidence/log.txt"],
            "test_results": {"passed": 10, "failed": 0, "skipped": 0},
        }],
        "overall_verdict": "EXECUTION_COMPLETE_VERIFIED",
        "all_green": True,
        "reroute_log": [],
        "evidence_manifest": [{"path": "evidence/log.txt", "type": "log"}],
        "self_review": {"l1_execution_issues": [], "l2_integration_issues": [], "l3_system_weaknesses": []},
        "evidence_bundle_path": "/tmp/evidence.zip",
    }), encoding="utf-8")
    return p


@pytest.fixture
def stage3_not_green(tmp_path: Path) -> Path:
    """Create a not-green Stage 3 output file."""
    p = tmp_path / "stage3-not-green.json"
    p.write_text(json.dumps({
        "sprint_id": "TEST",
        "timestamp": "2026-06-15T00:00:00Z",
        "execution_results": [{
            "taskcard_id": "TC-001",
            "status": "COMPLETED",
            "quality_scores": {
                "correctness": 3, "test_coverage": 5, "evidence_completeness": 5,
                "code_quality": 5, "schema_compliance": 5, "governance_compliance": 5,
                "path_discipline": 5, "documentation": 5, "idempotency": 5,
                "regression_safety": 5, "performance": 5, "error_handling": 5,
                "integration_consistency": 5, "evidence_traceability": 5,
                "acceptance_criteria_met": 5,
            },
            "evidence_paths": ["evidence/log.txt"],
            "test_results": {"passed": 5, "failed": 2, "skipped": 0},
        }],
        "overall_verdict": "EXECUTION_COMPLETE_WITH_LIMITATIONS",
        "all_green": False,
        "reroute_log": [],
        "evidence_manifest": [{"path": "evidence/log.txt", "type": "log"}],
        "self_review": {"l1_execution_issues": [], "l2_integration_issues": [], "l3_system_weaknesses": []},
        "evidence_bundle_path": "/tmp/evidence.zip",
    }), encoding="utf-8")
    return p


@pytest.fixture
def stage3_missing(tmp_path: Path) -> Path:
    """Return a path to a non-existent file."""
    return tmp_path / "nonexistent.json"


class TestInitLoop:
    def test_creates_state_file(self, loop_root):
        state = init_loop(loop_root, "test-run-001")
        assert state["current_state"] == "INITIAL"
        assert state["iteration"] == 0
        assert state["max_iterations"] == DEFAULT_MAX_LOOPS
        state_file = loop_root / ".local" / "supervisor" / "post-sprint-loop-state.json"
        assert state_file.exists()

    def test_custom_max_loops(self, loop_root):
        state = init_loop(loop_root, "test-run-002", max_loops=5)
        assert state["max_iterations"] == 5


class TestTransitions:
    def test_valid_transition(self, loop_root):
        init_loop(loop_root, "test-run")
        state = transition_to(loop_root, "AUDIT_RUNNING", "start_audit")
        assert state["current_state"] == "AUDIT_RUNNING"
        assert len(state["decision_history"]) == 1

    def test_invalid_transition_rejected(self, loop_root):
        init_loop(loop_root, "test-run")
        with pytest.raises(ValueError, match="Invalid transition"):
            transition_to(loop_root, "EXECUTION_COMPLETE", "skip_to_end")

    def test_full_happy_path_transitions(self, loop_root):
        """Walk through all transitions in the happy path."""
        init_loop(loop_root, "test-run")
        transition_to(loop_root, "AUDIT_RUNNING", "start_audit")
        transition_to(loop_root, "AUDIT_COMPLETE", "audit_finished")
        transition_to(loop_root, "HARDENING_RUNNING", "start_hardening")
        transition_to(loop_root, "HARDENING_COMPLETE", "hardening_finished")
        transition_to(loop_root, "EXECUTION_RUNNING", "start_execution")
        state = transition_to(loop_root, "EXECUTION_COMPLETE", "execution_finished")
        assert state["current_state"] == "EXECUTION_COMPLETE"
        assert len(state["decision_history"]) == 6


class TestClassifyAndDecide:
    def test_all_green_decision(self, loop_root, stage3_all_green):
        init_loop(loop_root, "test-run")
        # Walk to EXECUTION_COMPLETE
        transition_to(loop_root, "AUDIT_RUNNING", "start_audit")
        transition_to(loop_root, "AUDIT_COMPLETE", "audit_finished")
        transition_to(loop_root, "HARDENING_RUNNING", "start_hardening")
        transition_to(loop_root, "HARDENING_COMPLETE", "hardening_finished")
        transition_to(loop_root, "EXECUTION_RUNNING", "start_execution")
        transition_to(loop_root, "EXECUTION_COMPLETE", "execution_finished")

        result = classify_and_decide(loop_root, stage3_all_green)
        assert result["next_state"] == "ACCEPTED_ALL_GREEN"
        assert result["classification"]["classification"] == "STRUCTURED_ALL_GREEN"

    def test_not_green_reroutes(self, loop_root, stage3_not_green):
        init_loop(loop_root, "test-run")
        transition_to(loop_root, "AUDIT_RUNNING", "start_audit")
        transition_to(loop_root, "AUDIT_COMPLETE", "audit_finished")
        transition_to(loop_root, "HARDENING_RUNNING", "start_hardening")
        transition_to(loop_root, "HARDENING_COMPLETE", "hardening_finished")
        transition_to(loop_root, "EXECUTION_RUNNING", "start_execution")
        transition_to(loop_root, "EXECUTION_COMPLETE", "execution_finished")

        result = classify_and_decide(loop_root, stage3_not_green)
        assert result["next_state"] in ("REROUTE_TO_HARDEN", "REROUTE_REWORK")

    def test_missing_restarts_from_audit(self, loop_root, stage3_missing):
        init_loop(loop_root, "test-run")
        transition_to(loop_root, "AUDIT_RUNNING", "start_audit")
        transition_to(loop_root, "AUDIT_COMPLETE", "audit_finished")
        transition_to(loop_root, "HARDENING_RUNNING", "start_hardening")
        transition_to(loop_root, "HARDENING_COMPLETE", "hardening_finished")
        transition_to(loop_root, "EXECUTION_RUNNING", "start_execution")
        transition_to(loop_root, "EXECUTION_COMPLETE", "execution_finished")

        result = classify_and_decide(loop_root, stage3_missing)
        assert result["next_state"] == "REROUTE_TO_AUDIT"

    def test_max_loops_exceeded(self, loop_root, stage3_not_green):
        init_loop(loop_root, "test-run", max_loops=1)
        transition_to(loop_root, "AUDIT_RUNNING", "start_audit")
        transition_to(loop_root, "AUDIT_COMPLETE", "audit_finished")
        transition_to(loop_root, "HARDENING_RUNNING", "start_hardening")
        transition_to(loop_root, "HARDENING_COMPLETE", "hardening_finished")
        transition_to(loop_root, "EXECUTION_RUNNING", "start_execution")
        transition_to(loop_root, "EXECUTION_COMPLETE", "execution_finished")

        result = classify_and_decide(loop_root, stage3_not_green)
        assert result["next_state"] == "MAX_LOOPS_EXCEEDED"


class TestGetNextStages:
    def test_reroute_to_audit(self):
        assert get_next_stages("REROUTE_TO_AUDIT") == ["PROMPT_1", "PROMPT_2", "PROMPT_3"]

    def test_reroute_to_harden(self):
        assert get_next_stages("REROUTE_TO_HARDEN") == ["PROMPT_2", "PROMPT_3"]

    def test_reroute_rework(self):
        assert get_next_stages("REROUTE_REWORK") == ["PROMPT_3"]

    def test_accepted(self):
        assert get_next_stages("ACCEPTED_ALL_GREEN") == []

    def test_terminal_states(self):
        assert get_next_stages("MAX_LOOPS_EXCEEDED") == []
        assert get_next_stages("HARD_STOP") == []
        assert get_next_stages("BLOCKED_EXTERNAL") == []

    def test_initial(self):
        assert get_next_stages("INITIAL") == ["PROMPT_1", "PROMPT_2", "PROMPT_3"]


class TestDryRun:
    def test_dry_run_all_green(self, loop_root, stage3_all_green):
        result = run_loop_dry(loop_root, "dry-test", stage3_all_green)
        assert result["next_state"] == "ACCEPTED_ALL_GREEN"
        assert result["next_stages"] == []

    def test_dry_run_not_green(self, loop_root, stage3_not_green):
        result = run_loop_dry(loop_root, "dry-test", stage3_not_green)
        assert result["next_state"] in ("REROUTE_TO_HARDEN", "REROUTE_REWORK")
        assert len(result["next_stages"]) > 0


class TestValidStates:
    def test_all_valid_states_covered(self):
        """All declared valid states have transition entries."""
        for state in VALID_STATES:
            if state in ("ACCEPTED_ALL_GREEN", "MAX_LOOPS_EXCEEDED", "HARD_STOP", "BLOCKED_EXTERNAL"):
                continue  # Terminal or near-terminal states
            assert state in VALID_TRANSITIONS, f"{state} missing from transitions"

    def test_no_invalid_final_states_in_valid_states(self):
        """Invalid final states are not in the valid states enum."""
        for invalid in INVALID_FINAL_STATES:
            assert invalid not in VALID_STATES
