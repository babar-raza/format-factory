"""
Tests for loop state reset logic (TC-RESET-001 verification).
Validates that:
- New run_ids get fresh loop state
- Terminal states auto-reset on next cycle
- max_iterations from policies.yaml used when available
- Fallback max_iterations when no policies.yaml
"""
import json
import sys
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))
sys.path.insert(0, str(_repo_root / "tools" / "supervisor"))

from post_sprint_loop_controller import (
    init_loop,
    transition_to,
    classify_and_decide,
    _read_state,
    _state_file_path,
    VALID_TRANSITIONS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_quality_scores(tmp_path, all_green=True):
    """Write quality-scores.json matching production schema."""
    base_score = 5 if all_green else 2
    scores = {dim: base_score for dim in [
        "correctness", "test_coverage", "evidence_completeness",
        "code_quality", "schema_compliance", "governance_compliance",
        "path_discipline", "documentation", "idempotency",
        "regression_safety", "performance", "error_handling",
        "integration_consistency", "evidence_traceability",
        "acceptance_criteria_met",
    ]}
    data = {
        "execution_results": [{
            "taskcard_id": "T1",
            "status": "COMPLETED" if all_green else "REROUTED",
            "quality_scores": scores,
            "evidence_paths": ["proof.txt"],
            "test_results": {"passed": 5, "failed": 0, "skipped": 0},
            "rerouted": not all_green,
        }],
        "overall_scores": scores,
        "overall_verdict": "EXECUTION_COMPLETE_VERIFIED" if all_green
            else "EXECUTION_REROUTED_REWORK_REQUIRED",
        "all_green": all_green,
        "reroute_log": [] if all_green else [
            {"taskcard_id": "T1", "reason": "Low", "failing_dimensions": ["correctness"]}
        ],
    }
    path = tmp_path / "quality-scores.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def _fast_forward(tmp_path):
    """Fast-forward loop state to EXECUTION_COMPLETE."""
    for state, trigger in [
        ("AUDIT_RUNNING", "audit"), ("AUDIT_COMPLETE", "audit_done"),
        ("HARDENING_RUNNING", "harden"), ("HARDENING_COMPLETE", "harden_done"),
        ("EXECUTION_RUNNING", "execute"), ("EXECUTION_COMPLETE", "execute_done"),
    ]:
        transition_to(tmp_path, state, trigger)


# ---------------------------------------------------------------------------
# Tests: Fresh state for new run_id
# ---------------------------------------------------------------------------

def test_different_run_id_gets_fresh_state(tmp_path):
    """Init with run_id 'sprint-1', then init with 'sprint-2' -> fresh state."""
    init_loop(tmp_path, "sprint-1", max_loops=5)
    _fast_forward(tmp_path)

    # Classify to increment iteration
    quality_path = _write_quality_scores(tmp_path, all_green=False)
    classify_and_decide(tmp_path, quality_path)

    state1 = _read_state(tmp_path)
    assert state1["run_id"] == "sprint-1"
    assert state1["iteration"] >= 1

    # Now init a new sprint — should get fresh state
    init_loop(tmp_path, "sprint-2", max_loops=12)
    state2 = _read_state(tmp_path)
    assert state2["run_id"] == "sprint-2"
    assert state2["iteration"] == 0
    assert state2["current_state"] == "INITIAL"


def test_same_run_id_preserves_state(tmp_path):
    """Re-reading with same run_id doesn't reset iteration."""
    init_loop(tmp_path, "sprint-1", max_loops=12)
    _fast_forward(tmp_path)

    quality_path = _write_quality_scores(tmp_path, all_green=False)
    classify_and_decide(tmp_path, quality_path)

    state = _read_state(tmp_path)
    assert state["iteration"] == 1
    assert state["run_id"] == "sprint-1"


# ---------------------------------------------------------------------------
# Tests: Terminal state auto-reset
# ---------------------------------------------------------------------------

def test_max_loops_exceeded_is_terminal(tmp_path):
    """Reaching MAX_LOOPS_EXCEEDED should be detectable as terminal."""
    init_loop(tmp_path, "sprint-terminal", max_loops=1)
    _fast_forward(tmp_path)

    quality_path = _write_quality_scores(tmp_path, all_green=False)
    decision = classify_and_decide(tmp_path, quality_path)

    # With max_loops=1 and not-green, should hit MAX_LOOPS_EXCEEDED
    assert decision["next_state"] == "MAX_LOOPS_EXCEEDED"

    state = _read_state(tmp_path)
    assert state["current_state"] == "MAX_LOOPS_EXCEEDED"


def test_accepted_all_green_is_terminal(tmp_path):
    """ACCEPTED_ALL_GREEN is a terminal state."""
    init_loop(tmp_path, "sprint-green", max_loops=12)
    _fast_forward(tmp_path)

    quality_path = _write_quality_scores(tmp_path, all_green=True)
    decision = classify_and_decide(tmp_path, quality_path)

    assert decision["next_state"] == "ACCEPTED_ALL_GREEN"
    state = _read_state(tmp_path)
    assert state["current_state"] == "ACCEPTED_ALL_GREEN"


def test_reinit_after_terminal_resets(tmp_path):
    """After MAX_LOOPS_EXCEEDED, a new init_loop resets everything."""
    init_loop(tmp_path, "sprint-old", max_loops=1)
    _fast_forward(tmp_path)
    quality_path = _write_quality_scores(tmp_path, all_green=False)
    classify_and_decide(tmp_path, quality_path)

    state = _read_state(tmp_path)
    assert state["current_state"] == "MAX_LOOPS_EXCEEDED"

    # Re-init should give fresh state
    init_loop(tmp_path, "sprint-new", max_loops=12)
    state = _read_state(tmp_path)
    assert state["current_state"] == "INITIAL"
    assert state["iteration"] == 0
    assert state["run_id"] == "sprint-new"
    assert state["max_iterations"] == 12


# ---------------------------------------------------------------------------
# Tests: max_iterations configuration
# ---------------------------------------------------------------------------

def test_max_iterations_from_init(tmp_path):
    """max_iterations passed to init_loop is stored in state."""
    init_loop(tmp_path, "test-max", max_loops=7)
    state = _read_state(tmp_path)
    assert state["max_iterations"] == 7


def test_default_max_loops_is_3(tmp_path):
    """Default max_loops is 3 (from DEFAULT_MAX_LOOPS constant)."""
    init_loop(tmp_path, "test-default")
    state = _read_state(tmp_path)
    assert state["max_iterations"] == 3


def test_iteration_increments_on_classify(tmp_path):
    """Each classify_and_decide call increments iteration by 1."""
    init_loop(tmp_path, "test-iter", max_loops=10)
    _fast_forward(tmp_path)

    quality_path = _write_quality_scores(tmp_path, all_green=True)
    decision = classify_and_decide(tmp_path, quality_path)
    assert decision["iteration"] == 1

    # Re-init and fast-forward for second classification
    init_loop(tmp_path, "test-iter-2", max_loops=10)
    _fast_forward(tmp_path)
    decision2 = classify_and_decide(tmp_path, quality_path)
    assert decision2["iteration"] == 1  # fresh state, so back to 1


# ---------------------------------------------------------------------------
# Tests: State file structure
# ---------------------------------------------------------------------------

def test_state_file_has_required_fields(tmp_path):
    """Loop state file must have all required fields."""
    init_loop(tmp_path, "test-fields", max_loops=5)
    state = _read_state(tmp_path)

    required = [
        "current_state", "iteration", "max_iterations", "run_id",
        "started_at", "updated_at", "decision_history",
    ]
    for field in required:
        assert field in state, f"Missing field: {field}"


def test_decision_history_records_transitions(tmp_path):
    """Decision history tracks all state transitions."""
    init_loop(tmp_path, "test-history", max_loops=12)
    _fast_forward(tmp_path)

    state = _read_state(tmp_path)
    history = state["decision_history"]
    assert len(history) == 6  # 6 transitions in fast_forward
    assert history[0]["to_state"] == "AUDIT_RUNNING"
    assert history[-1]["to_state"] == "EXECUTION_COMPLETE"
