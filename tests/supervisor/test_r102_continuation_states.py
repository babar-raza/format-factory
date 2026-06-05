"""
R102 — Extended Continuation State Machine Tests
Tests the 4 new continuation states added in R102:
  - NO_GENERIC_NEXT_PROMPT
  - NO_LEGACY_REVIEW_CONTRADICTION
  - NO_STALE_GAPS
  - NO_MISSING_EVIDENCE_MANIFEST
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from autonomous_cycle import classify_continuation_state

POLICIES_PATH = REPO_ROOT / ".supervisor" / "policies.yaml"


def _review():
    return {"overall_verdict": "ACCEPTED", "autonomous_continue": True}


def test_no_generic_next_prompt():
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=False,
        hard_stops=["generic_next_prompt"],
        overclaimed=[],
        rework_items=[],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "NO_GENERIC_NEXT_PROMPT"


def test_no_legacy_review_contradiction():
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=False,
        hard_stops=["legacy_review_contradiction"],
        overclaimed=[],
        rework_items=[],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "NO_LEGACY_REVIEW_CONTRADICTION"


def test_no_stale_gaps():
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=False,
        hard_stops=["stale_gaps"],
        overclaimed=[],
        rework_items=[],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "NO_STALE_GAPS"


def test_no_missing_evidence_manifest():
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=False,
        hard_stops=["missing_evidence_manifest"],
        overclaimed=[],
        rework_items=[],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "NO_MISSING_EVIDENCE_MANIFEST"


def test_overclaimed_still_takes_priority():
    """Overclaimed items should still take priority over new hard stop types."""
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=False,
        hard_stops=["generic_next_prompt"],
        overclaimed=["item-X"],
        rework_items=[],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "NO_UNSAFE_SOURCE_STATE"


def test_max_iterations_before_new_stops():
    """Max iterations should take priority over new hard stop types."""
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=True,
        hard_stops=["max_iterations_reached", "generic_next_prompt"],
        overclaimed=[],
        rework_items=[],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "NO_MAX_ITERATIONS"


def test_unknown_hard_stop_falls_to_broken_baseline():
    """Unknown hard stop types should fall through to NO_BROKEN_BASELINE."""
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=False,
        hard_stops=["unknown_stop_reason"],
        overclaimed=[],
        rework_items=[],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "NO_BROKEN_BASELINE"


# ---------------------------------------------------------------------------
# Original states still work
# ---------------------------------------------------------------------------

def test_yes_still_works():
    state = classify_continuation_state(
        auto_continue_value=True,
        at_max_iterations=False,
        hard_stops=[],
        overclaimed=[],
        rework_items=[],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "YES"


def test_yes_with_rework_still_works():
    state = classify_continuation_state(
        auto_continue_value="true_with_rework",
        at_max_iterations=False,
        hard_stops=[],
        overclaimed=[],
        rework_items=["x"],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "YES_WITH_REWORK"
