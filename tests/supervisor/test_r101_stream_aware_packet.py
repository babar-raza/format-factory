"""
R101 — Stream-Aware Packet Generation Tests
Tests that generate_supervisor_packet.py produces stream-specific prompts
instead of generic product-oriented prompts for non-mainstream streams.

Covers:
  - detect_stream_from_sprint_id()
  - synthesize_stream_tasks() for acceleration/skills/supervisor
  - synthesize_sprint_tasks() with stream parameter
  - generate_next_sprint_md() with stream parameter
  - generate_packet() stream detection wiring
  - Anti-regression: no "Continue normal mega-train lanes" in non-mainstream
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from generate_supervisor_packet import (
    KNOWN_STREAMS,
    STREAM_FOCUS,
    detect_stream_from_sprint_id,
    synthesize_stream_tasks,
    synthesize_sprint_tasks,
    generate_next_sprint_md,
)


# ---------------------------------------------------------------------------
# detect_stream_from_sprint_id
# ---------------------------------------------------------------------------

def test_detect_supervisor_stream():
    sid = "FORMAT-FACTORY-SUPERVISOR-R100-AUTONOMOUS-CONTINUATION-MEGA-TRAIN-001"
    assert detect_stream_from_sprint_id(sid) == "supervisor"


def test_detect_acceleration_stream():
    sid = "FORMAT-FACTORY-ACCELERATION-R101-DEEP-TOOLING-MEGA-TRAIN-001"
    assert detect_stream_from_sprint_id(sid) == "acceleration"


def test_detect_skills_stream():
    sid = "FORMAT-FACTORY-SKILLS-R99-GOVERNED-EXECUTION-MEGA-TRAIN-001"
    assert detect_stream_from_sprint_id(sid) == "skills"


def test_detect_mainstream_explicit():
    sid = "FORMAT-FACTORY-MAINSTREAM-R103-PRODUCT-DEEPENING-MEGA-TRAIN-001"
    assert detect_stream_from_sprint_id(sid) == "mainstream"


def test_detect_mainstream_legacy():
    """Legacy sprints without stream prefix default to mainstream."""
    sid = "FORMAT-FACTORY-R93-CONTEXT-PACK-SUPERVISOR-MCP-ACCELERATION-POC-MEGA-TRAIN-001"
    assert detect_stream_from_sprint_id(sid) == "mainstream"


def test_detect_case_insensitive():
    sid = "format-factory-supervisor-r100-test"
    assert detect_stream_from_sprint_id(sid) == "supervisor"


def test_detect_unknown_defaults_mainstream():
    assert detect_stream_from_sprint_id("RANDOM-STRING") == "mainstream"


# ---------------------------------------------------------------------------
# STREAM_FOCUS constants
# ---------------------------------------------------------------------------

def test_stream_focus_has_all_streams():
    for stream in KNOWN_STREAMS:
        assert stream in STREAM_FOCUS, f"Missing focus for {stream}"


def test_stream_focus_strings_are_distinct():
    values = list(STREAM_FOCUS.values())
    assert len(values) == len(set(values)), "Stream focus strings must be unique"


def test_mainstream_focus_mentions_product():
    assert "Product" in STREAM_FOCUS["mainstream"]


def test_supervisor_focus_mentions_grading():
    assert "grading" in STREAM_FOCUS["supervisor"].lower()


def test_acceleration_focus_mentions_tooling():
    assert "tooling" in STREAM_FOCUS["acceleration"].lower() or "tool" in STREAM_FOCUS["acceleration"].lower()


def test_skills_focus_mentions_governed():
    assert "governed" in STREAM_FOCUS["skills"].lower() or "skill" in STREAM_FOCUS["skills"].lower()


# ---------------------------------------------------------------------------
# synthesize_stream_tasks
# ---------------------------------------------------------------------------

def _empty_review():
    return {"sprint_id": "test", "verdict": "ACCEPTED", "facts": {}}


def _empty_contradictions():
    return {"critical_count": 0, "contradictions": [], "autonomous_continue": True}


def test_acceleration_tasks_not_empty():
    tasks = synthesize_stream_tasks("acceleration", _empty_review(), _empty_contradictions(), REPO_ROOT)
    assert len(tasks) >= 3


def test_acceleration_tasks_no_product_gaps():
    tasks = synthesize_stream_tasks("acceleration", _empty_review(), _empty_contradictions(), REPO_ROOT)
    titles = " ".join(t["title"] for t in tasks)
    assert "Product deepening" not in titles
    assert "dogfood" not in titles.lower()
    assert "package artifacts" not in titles.lower()


def test_acceleration_tasks_mention_tooling():
    tasks = synthesize_stream_tasks("acceleration", _empty_review(), _empty_contradictions(), REPO_ROOT)
    titles = " ".join(t["title"] for t in tasks).lower()
    assert any(kw in titles for kw in ("skill", "gap", "handoff", "prompt", "engine"))


def test_skills_tasks_not_empty():
    tasks = synthesize_stream_tasks("skills", _empty_review(), _empty_contradictions(), REPO_ROOT)
    assert len(tasks) >= 3


def test_skills_tasks_mention_skill_domain():
    tasks = synthesize_stream_tasks("skills", _empty_review(), _empty_contradictions(), REPO_ROOT)
    titles = " ".join(t["title"] for t in tasks).lower()
    assert any(kw in titles for kw in ("skill", "transcript", "registry", "governed"))


def test_supervisor_tasks_not_empty():
    tasks = synthesize_stream_tasks("supervisor", _empty_review(), _empty_contradictions(), REPO_ROOT)
    assert len(tasks) >= 3


def test_supervisor_tasks_mention_supervisor_domain():
    tasks = synthesize_stream_tasks("supervisor", _empty_review(), _empty_contradictions(), REPO_ROOT)
    titles = " ".join(t["title"] for t in tasks).lower()
    assert any(kw in titles for kw in ("grading", "continuation", "prompt", "evidence", "replay"))


def test_all_stream_tasks_end_with_evidence_declaration():
    """Every stream's tasks should end with the evidence declaration task."""
    for stream in ("acceleration", "skills", "supervisor"):
        tasks = synthesize_stream_tasks(stream, _empty_review(), _empty_contradictions(), REPO_ROOT)
        assert "evidence declaration" in tasks[-1]["title"].lower()


def test_stream_tasks_include_repair_when_critical():
    contradictions = {
        "critical_count": 1,
        "contradictions": [
            {"severity": "CRITICAL", "description": "test failure", "detail": "fix it"}
        ],
    }
    for stream in ("acceleration", "skills", "supervisor"):
        tasks = synthesize_stream_tasks(stream, _empty_review(), contradictions, REPO_ROOT)
        repair = [t for t in tasks if t["task_id"].startswith("REPAIR-")]
        assert len(repair) == 1, f"{stream} should have 1 repair task"


# ---------------------------------------------------------------------------
# synthesize_sprint_tasks with stream parameter
# ---------------------------------------------------------------------------

def test_mainstream_tasks_include_product_gaps():
    """Mainstream stream should still get product-oriented tasks."""
    tasks = synthesize_sprint_tasks(_empty_review(), _empty_contradictions(), REPO_ROOT, stream="mainstream")
    titles = " ".join(t["title"] for t in tasks).lower()
    # Should have product/dogfood/package tasks
    assert any(kw in titles for kw in ("product", "dogfood", "package", "gap"))


def test_supervisor_tasks_via_synthesize_sprint_tasks():
    """When stream=supervisor, synthesize_sprint_tasks delegates to synthesize_stream_tasks."""
    tasks = synthesize_sprint_tasks(_empty_review(), _empty_contradictions(), REPO_ROOT, stream="supervisor")
    titles = " ".join(t["title"] for t in tasks).lower()
    assert "product deepening" not in titles
    assert any(kw in titles for kw in ("grading", "continuation", "prompt", "evidence"))


def test_default_stream_is_mainstream():
    """Default stream parameter should be mainstream (backwards compatible)."""
    tasks_default = synthesize_sprint_tasks(_empty_review(), _empty_contradictions(), REPO_ROOT)
    tasks_explicit = synthesize_sprint_tasks(_empty_review(), _empty_contradictions(), REPO_ROOT, stream="mainstream")
    # Both should produce product-oriented tasks
    default_titles = {t["title"] for t in tasks_default}
    explicit_titles = {t["title"] for t in tasks_explicit}
    assert default_titles == explicit_titles


# ---------------------------------------------------------------------------
# generate_next_sprint_md with stream
# ---------------------------------------------------------------------------

def test_next_sprint_md_mainstream_uses_product_focus():
    md = generate_next_sprint_md(_empty_review(), _empty_contradictions(), "", [], stream="mainstream")
    assert STREAM_FOCUS["mainstream"] in md


def test_next_sprint_md_supervisor_uses_supervisor_focus():
    md = generate_next_sprint_md(_empty_review(), _empty_contradictions(), "", [], stream="supervisor")
    assert STREAM_FOCUS["supervisor"] in md
    assert "Continue normal mega-train lanes" not in md


def test_next_sprint_md_acceleration_uses_acceleration_focus():
    md = generate_next_sprint_md(_empty_review(), _empty_contradictions(), "", [], stream="acceleration")
    assert STREAM_FOCUS["acceleration"] in md
    assert "Continue normal mega-train lanes" not in md


def test_next_sprint_md_skills_uses_skills_focus():
    md = generate_next_sprint_md(_empty_review(), _empty_contradictions(), "", [], stream="skills")
    assert STREAM_FOCUS["skills"] in md
    assert "Continue normal mega-train lanes" not in md


def test_next_sprint_md_critical_contradictions_override_stream_focus():
    """When critical contradictions exist, focus should be repair-oriented regardless of stream."""
    contradictions = {
        "critical_count": 1,
        "contradictions": [{"severity": "CRITICAL", "description": "broken"}],
        "autonomous_continue": False,
    }
    md = generate_next_sprint_md(_empty_review(), contradictions, "", [], stream="supervisor")
    assert "REPAIR" in md


def test_no_generic_focus_in_non_mainstream():
    """Anti-regression: no stream should produce 'Continue normal mega-train lanes'."""
    for stream in ("acceleration", "skills", "supervisor"):
        md = generate_next_sprint_md(_empty_review(), _empty_contradictions(), "", [], stream=stream)
        assert "Continue normal mega-train lanes" not in md, \
            f"Stream {stream} produced generic focus string"
