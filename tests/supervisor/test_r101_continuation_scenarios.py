"""
R101 — Continuation State Machine Scenario Tests
Tests max_iteration, checkpoint, dirty-tree, YES_WITH_REWORK,
and NO_GENERIC_NEXT_PROMPT scenarios.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from autonomous_cycle import classify_continuation_state
from generate_supervisor_packet import (
    detect_stream_from_sprint_id,
    STREAM_FOCUS,
    generate_next_sprint_md,
)


POLICIES_PATH = REPO_ROOT / ".supervisor" / "policies.yaml"


# ---------------------------------------------------------------------------
# classify_continuation_state scenarios
# ---------------------------------------------------------------------------

def _review():
    return {"overall_verdict": "ACCEPTED", "autonomous_continue": True}


def test_yes_pure_new_work():
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


def test_yes_with_rework():
    state = classify_continuation_state(
        auto_continue_value="true_with_rework",
        at_max_iterations=False,
        hard_stops=[],
        overclaimed=[],
        rework_items=["item-1"],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "YES_WITH_REWORK"


def test_no_max_iterations():
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=True,
        hard_stops=["max_iterations_reached"],
        overclaimed=[],
        rework_items=[],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "NO_MAX_ITERATIONS"


def test_no_unsafe_source_state():
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=False,
        hard_stops=[],
        overclaimed=["item-X"],
        rework_items=[],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "NO_UNSAFE_SOURCE_STATE"


def test_no_broken_baseline():
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=False,
        hard_stops=["critical_rework_blocks_continuation"],
        overclaimed=[],
        rework_items=[],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "NO_BROKEN_BASELINE"


def test_no_external_gate():
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=False,
        hard_stops=[],
        overclaimed=[],
        rework_items=[],
        review=_review(),
        policies_path=POLICIES_PATH,
    )
    assert state == "NO_EXTERNAL_GATE"


# ---------------------------------------------------------------------------
# NO_GENERIC_NEXT_PROMPT scenario
# ---------------------------------------------------------------------------

def test_generic_prompt_not_generated_for_supervisor():
    """When stream is supervisor, the generated prompt must NOT contain
    the generic 'Continue normal mega-train lanes' focus string."""
    md = generate_next_sprint_md(
        {"sprint_id": "FORMAT-FACTORY-SUPERVISOR-R100-TEST", "verdict": "ACCEPTED", "facts": {}},
        {"critical_count": 0, "contradictions": [], "autonomous_continue": True},
        "", [], stream="supervisor"
    )
    assert "Continue normal mega-train lanes" not in md
    assert STREAM_FOCUS["supervisor"] in md


def test_generic_prompt_not_generated_for_acceleration():
    md = generate_next_sprint_md(
        {"sprint_id": "FORMAT-FACTORY-ACCELERATION-R101-TEST", "verdict": "ACCEPTED", "facts": {}},
        {"critical_count": 0, "contradictions": [], "autonomous_continue": True},
        "", [], stream="acceleration"
    )
    assert "Continue normal mega-train lanes" not in md
    assert STREAM_FOCUS["acceleration"] in md


def test_generic_prompt_not_generated_for_skills():
    md = generate_next_sprint_md(
        {"sprint_id": "FORMAT-FACTORY-SKILLS-R99-TEST", "verdict": "ACCEPTED", "facts": {}},
        {"critical_count": 0, "contradictions": [], "autonomous_continue": True},
        "", [], stream="skills"
    )
    assert "Continue normal mega-train lanes" not in md
    assert STREAM_FOCUS["skills"] in md


# ---------------------------------------------------------------------------
# Stream detection integration
# ---------------------------------------------------------------------------

def test_stream_detection_feeds_correct_focus():
    """End-to-end: sprint_id → stream → focus string in prompt."""
    sprint_ids = {
        "FORMAT-FACTORY-SUPERVISOR-R100-X": "supervisor",
        "FORMAT-FACTORY-ACCELERATION-R101-X": "acceleration",
        "FORMAT-FACTORY-SKILLS-R99-X": "skills",
        "FORMAT-FACTORY-R93-X": "mainstream",
    }
    for sid, expected_stream in sprint_ids.items():
        stream = detect_stream_from_sprint_id(sid)
        assert stream == expected_stream
        md = generate_next_sprint_md(
            {"sprint_id": sid, "verdict": "ACCEPTED", "facts": {}},
            {"critical_count": 0, "contradictions": [], "autonomous_continue": True},
            "", [], stream=stream
        )
        assert STREAM_FOCUS[expected_stream] in md
