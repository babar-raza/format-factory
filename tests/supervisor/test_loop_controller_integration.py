"""
Tests for Loop Controller integration (Phase 1 — advisory state tracking).
TC-LOOP-001: Verify loop controller initializes, transitions, and classifies
quality scorer output correctly.
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
    get_next_stages,
    VALID_TRANSITIONS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_quality_scores(tmp_path, all_green=True, scores=None):
    """Write a quality-scores.json file matching quality_scorer output."""
    if scores is None:
        base_score = 5 if all_green else 2
        scores = {dim: base_score for dim in [
            "correctness", "test_coverage", "evidence_completeness",
            "code_quality", "schema_compliance", "governance_compliance",
            "path_discipline", "documentation", "idempotency",
            "regression_safety", "performance", "error_handling",
            "integration_consistency", "evidence_traceability",
            "acceptance_criteria_met",
        ]}

    result = {
        "execution_results": [
            {
                "taskcard_id": "T1",
                "status": "COMPLETED",
                "quality_scores": scores,
                "evidence_paths": ["proof.txt"],
                "test_results": {"passed": 5, "failed": 0, "skipped": 0},
                "rerouted": not all_green,
                "rework_reason": "" if all_green else "Low scores",
            }
        ],
        "overall_scores": scores,
        "overall_verdict": "EXECUTION_COMPLETE_VERIFIED" if all_green else "EXECUTION_REROUTED_REWORK_REQUIRED",
        "all_green": all_green,
        "reroute_log": [] if all_green else [
            {"taskcard_id": "T1", "reason": "Low scores", "failing_dimensions": ["documentation"]}
        ],
    }

    review_dir = tmp_path / ".local" / "supervisor" / "reviews" / "test-run"
    review_dir.mkdir(parents=True, exist_ok=True)
    quality_path = review_dir / "quality-scores.json"
    quality_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return quality_path


def _fast_forward_to_execution_complete(tmp_path):
    """Initialize loop and fast-forward to EXECUTION_COMPLETE state."""
    init_loop(tmp_path, "test-run")
    transitions = [
        ("AUDIT_RUNNING", "test_audit"),
        ("AUDIT_COMPLETE", "test_audit_done"),
        ("HARDENING_RUNNING", "test_harden"),
        ("HARDENING_COMPLETE", "test_harden_done"),
        ("EXECUTION_RUNNING", "test_execute"),
        ("EXECUTION_COMPLETE", "test_execute_done"),
    ]
    for state, trigger in transitions:
        transition_to(tmp_path, state, trigger)


# ---------------------------------------------------------------------------
# Tests: Initialization
# ---------------------------------------------------------------------------

def test_init_creates_state_file(tmp_path):
    state = init_loop(tmp_path, "test-run")
    assert state["current_state"] == "INITIAL"
    assert state["iteration"] == 0
    assert state["run_id"] == "test-run"

    state_path = tmp_path / ".local" / "supervisor" / "post-sprint-loop-state.json"
    assert state_path.exists()


# ---------------------------------------------------------------------------
# Tests: State transitions
# ---------------------------------------------------------------------------

def test_valid_transition_chain(tmp_path):
    """Full transition chain: INITIAL → ... → EXECUTION_COMPLETE."""
    init_loop(tmp_path, "test-run")
    chain = [
        "AUDIT_RUNNING", "AUDIT_COMPLETE",
        "HARDENING_RUNNING", "HARDENING_COMPLETE",
        "EXECUTION_RUNNING", "EXECUTION_COMPLETE",
    ]
    for target in chain:
        state = transition_to(tmp_path, target, f"test_{target}")
        assert state["current_state"] == target


def test_invalid_transition_raises(tmp_path):
    """Cannot jump from INITIAL to EXECUTION_RUNNING."""
    init_loop(tmp_path, "test-run")
    with pytest.raises(ValueError, match="Invalid transition"):
        transition_to(tmp_path, "EXECUTION_RUNNING", "illegal_jump")


# ---------------------------------------------------------------------------
# Tests: Classification
# ---------------------------------------------------------------------------

def test_classify_all_green(tmp_path):
    """All-green quality output → valid loop state (classification depends on classifier heuristics)."""
    _fast_forward_to_execution_complete(tmp_path)
    quality_path = _write_quality_scores(tmp_path, all_green=True)

    decision = classify_and_decide(tmp_path, quality_path)

    # With the classifier fix (TC-CLASS-001), all-green quality-scores.json
    # should produce ACCEPTED_ALL_GREEN, not fall through to EVIDENCE_MISSING.
    assert decision["next_state"] == "ACCEPTED_ALL_GREEN", (
        f"Expected ACCEPTED_ALL_GREEN, got {decision['next_state']}. "
        f"Classification: {decision['classification']['classification']}"
    )
    assert decision["next_state"] != "MAX_LOOPS_EXCEEDED", (
        f"Fresh loop should not hit MAX_LOOPS_EXCEEDED. "
        f"Iteration: {decision['iteration']}"
    )
    assert "classification" in decision
    assert "iteration" in decision


def test_classify_not_green(tmp_path):
    """Low-score quality output → reroute state."""
    _fast_forward_to_execution_complete(tmp_path)
    quality_path = _write_quality_scores(tmp_path, all_green=False)

    decision = classify_and_decide(tmp_path, quality_path)

    # Should NOT be ACCEPTED_ALL_GREEN
    assert decision["next_state"] != "ACCEPTED_ALL_GREEN"
    assert decision["next_state"] in VALID_TRANSITIONS.get("CLASSIFYING", [])


# ---------------------------------------------------------------------------
# Tests: get_next_stages
# ---------------------------------------------------------------------------

def test_next_stages_reroute_to_audit():
    stages = get_next_stages("REROUTE_TO_AUDIT")
    assert "PROMPT_1" in stages
    assert "PROMPT_2" in stages
    assert "PROMPT_3" in stages


def test_next_stages_reroute_to_harden():
    stages = get_next_stages("REROUTE_TO_HARDEN")
    assert "PROMPT_2" in stages
    assert "PROMPT_3" in stages
    assert "PROMPT_1" not in stages


def test_next_stages_reroute_rework():
    stages = get_next_stages("REROUTE_REWORK")
    assert "PROMPT_3" in stages


def test_next_stages_accepted():
    stages = get_next_stages("ACCEPTED_ALL_GREEN")
    assert stages == [] or stages == ["ADVERSARIAL_REVIEW"]
