"""
R102 — Stream-Specific Prompt Quality Tests
Tests that non-mainstream prompts don't contain generic product language.
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from generate_supervisor_packet import (
    generate_next_sprint_md,
    synthesize_sprint_tasks,
    STREAM_FOCUS,
)


def _review():
    return {"sprint_id": "TEST", "verdict": "ACCEPTED", "facts": {"test_count": 100, "fail_count": 0, "skip_count": 0}}


def _contradictions():
    return {"critical_count": 0, "contradictions": [], "autonomous_continue": True}


# ---------------------------------------------------------------------------
# Section header tests
# ---------------------------------------------------------------------------

def test_mainstream_has_product_work_header():
    tasks = synthesize_sprint_tasks(_review(), _contradictions(), REPO_ROOT, stream="mainstream")
    md = generate_next_sprint_md(_review(), _contradictions(), "", tasks, stream="mainstream")
    assert "New Product Work" in md


def test_supervisor_has_supervisor_work_header():
    tasks = synthesize_sprint_tasks(_review(), _contradictions(), REPO_ROOT, stream="supervisor")
    md = generate_next_sprint_md(_review(), _contradictions(), "", tasks, stream="supervisor")
    assert "Supervisor Infrastructure Work" in md
    assert "New Product Work" not in md


def test_acceleration_has_acceleration_work_header():
    tasks = synthesize_sprint_tasks(_review(), _contradictions(), REPO_ROOT, stream="acceleration")
    md = generate_next_sprint_md(_review(), _contradictions(), "", tasks, stream="acceleration")
    assert "Acceleration Tooling Work" in md
    assert "New Product Work" not in md


def test_skills_has_skills_work_header():
    tasks = synthesize_sprint_tasks(_review(), _contradictions(), REPO_ROOT, stream="skills")
    md = generate_next_sprint_md(_review(), _contradictions(), "", tasks, stream="skills")
    assert "Governed Skill Work" in md
    assert "New Product Work" not in md


# ---------------------------------------------------------------------------
# Lane manifest tests
# ---------------------------------------------------------------------------

def test_mainstream_lanes_mention_dogfood():
    tasks = synthesize_sprint_tasks(_review(), _contradictions(), REPO_ROOT, stream="mainstream")
    md = generate_next_sprint_md(_review(), _contradictions(), "", tasks, stream="mainstream")
    assert "Dogfood" in md


def test_supervisor_lanes_mention_grading():
    tasks = synthesize_sprint_tasks(_review(), _contradictions(), REPO_ROOT, stream="supervisor")
    md = generate_next_sprint_md(_review(), _contradictions(), "", tasks, stream="supervisor")
    assert "Grading" in md or "grading" in md


def test_non_mainstream_lanes_no_dogfood():
    for stream in ("supervisor", "acceleration", "skills"):
        tasks = synthesize_sprint_tasks(_review(), _contradictions(), REPO_ROOT, stream=stream)
        md = generate_next_sprint_md(_review(), _contradictions(), "", tasks, stream=stream)
        # Non-mainstream shouldn't have product-specific lanes
        assert "Dogfood export" not in md, f"{stream} prompt contains 'Dogfood export'"
        assert "Package/install proof" not in md, f"{stream} prompt contains 'Package/install proof'"


# ---------------------------------------------------------------------------
# Rules section tests
# ---------------------------------------------------------------------------

def test_mainstream_has_product_rules():
    tasks = synthesize_sprint_tasks(_review(), _contradictions(), REPO_ROOT, stream="mainstream")
    md = generate_next_sprint_md(_review(), _contradictions(), "", tasks, stream="mainstream")
    assert "product-code-change-ledger" in md or "PRODUCT_CODE_LEDGER" in md


def test_non_mainstream_has_stream_boundary_rule():
    for stream in ("supervisor", "acceleration", "skills"):
        tasks = synthesize_sprint_tasks(_review(), _contradictions(), REPO_ROOT, stream=stream)
        md = generate_next_sprint_md(_review(), _contradictions(), "", tasks, stream=stream)
        assert "stream boundary" in md.lower(), f"{stream} missing stream boundary rule"


# ---------------------------------------------------------------------------
# Stream header in prompt
# ---------------------------------------------------------------------------

def test_prompt_includes_stream_label():
    for stream in ("mainstream", "acceleration", "skills", "supervisor"):
        tasks = synthesize_sprint_tasks(_review(), _contradictions(), REPO_ROOT, stream=stream)
        md = generate_next_sprint_md(_review(), _contradictions(), "", tasks, stream=stream)
        assert f"# Stream: {stream}" in md, f"{stream} prompt missing stream label"


# ---------------------------------------------------------------------------
# No generic focus in any non-mainstream stream
# ---------------------------------------------------------------------------

def test_no_generic_focus_anywhere():
    for stream in ("acceleration", "skills", "supervisor"):
        tasks = synthesize_sprint_tasks(_review(), _contradictions(), REPO_ROOT, stream=stream)
        md = generate_next_sprint_md(_review(), _contradictions(), "", tasks, stream=stream)
        assert "Continue normal mega-train lanes" not in md
