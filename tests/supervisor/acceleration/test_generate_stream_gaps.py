"""Tests for generate_stream_gaps.py — fresh gap generation for all 4 streams."""

import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))

from generate_stream_gaps import (
    generate_acceleration_gaps,
    generate_all_stream_gaps,
    generate_mainstream_gaps,
    generate_skills_gaps,
    generate_supervisor_gaps,
)


# ── Mainstream gaps ──────────────────────────────────────────────


def test_mainstream_gaps_from_matrix():
    matrix = {
        "commercial_net_products": [
            {
                "format": "FODS",
                "dogfood_status": {
                    "fods_to_csv_dotnet": "GAP_DOGFOOD_EXTERNAL",
                },
                "dotnet_status": {
                    "load": "PASS",
                    "save": "NOT_IMPLEMENTED",
                },
            }
        ]
    }
    gaps = generate_mainstream_gaps(matrix)
    assert len(gaps) >= 2
    assert all(g["stream"] == "mainstream" for g in gaps)
    statuses = {g["current_status"] for g in gaps}
    assert "GAP_DOGFOOD_EXTERNAL" in statuses
    assert "NOT_IMPLEMENTED" in statuses


def test_mainstream_gaps_empty_matrix():
    gaps = generate_mainstream_gaps({})
    assert gaps == []


def test_mainstream_gaps_all_pass():
    matrix = {
        "commercial_net_products": [
            {
                "format": "FODS",
                "dotnet_status": {"load": "PASS", "save": "PASS"},
            }
        ]
    }
    gaps = generate_mainstream_gaps(matrix)
    assert gaps == []


# ── Acceleration gaps ────────────────────────────────────────────


def test_acceleration_gaps_detect_missing_tools(tmp_path):
    tool_dir = tmp_path / "tools"
    tool_dir.mkdir()
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    gaps = generate_acceleration_gaps(tool_dir, test_dir)
    missing = [g for g in gaps if g.get("current_status") == "NOT_IMPLEMENTED"]
    assert len(missing) >= 10  # most tools missing from empty dir


def test_acceleration_gaps_detect_untested_tools(tmp_path):
    tool_dir = tmp_path / "tools"
    tool_dir.mkdir()
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    # Create tool but no test
    (tool_dir / "next_best_action.py").write_text("# stub")
    gaps = generate_acceleration_gaps(tool_dir, test_dir)
    untested = [g for g in gaps if g.get("current_status") == "PARTIAL"]
    assert any("untested" in g["gap_id"] for g in untested)


def test_acceleration_gaps_include_integration_gaps(tmp_path):
    tool_dir = tmp_path / "tools"
    tool_dir.mkdir()
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    gaps = generate_acceleration_gaps(tool_dir, test_dir)
    integration = [g for g in gaps if "integration" in g["gap_id"]]
    assert len(integration) >= 2  # review-package + manifest colocation


def test_acceleration_gaps_all_have_stream_field(tmp_path):
    tool_dir = tmp_path / "tools"
    tool_dir.mkdir()
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    gaps = generate_acceleration_gaps(tool_dir, test_dir)
    assert all(g["stream"] == "acceleration" for g in gaps)


# ── Skills gaps ──────────────────────────────────────────────────


def test_skills_gaps_missing_registry():
    gaps = generate_skills_gaps(None)
    assert len(gaps) == 1
    assert gaps[0]["current_status"] == "NOT_FOUND"


def test_skills_gaps_unregistered_tools():
    registry = {"skills": []}
    gaps = generate_skills_gaps(registry)
    unregistered = [g for g in gaps if g.get("current_status") == "NOT_REGISTERED"]
    assert len(unregistered) >= 4  # at least next_best_action, stream_forecaster, anti_skip_checker, stream_prompt_generator


def test_skills_gaps_draft_skills():
    registry = {
        "skills": [
            {"skill_id": "my-draft", "status": "draft", "command": "/my-draft"},
        ]
    }
    gaps = generate_skills_gaps(registry)
    drafts = [g for g in gaps if g.get("current_status") == "DRAFT"]
    assert len(drafts) == 1
    assert drafts[0]["skill_id"] == "my-draft"


def test_skills_gaps_all_registered():
    registry = {
        "skills": [
            {"skill_id": f"s{i}", "status": "active", "command": f"/{cmd}"}
            for i, cmd in enumerate([
                "next-best-action", "stream-forecaster", "anti-skip-checker",
                "stream-prompt-generator", "generate-stream-gaps",
            ])
        ]
    }
    gaps = generate_skills_gaps(registry)
    unregistered = [g for g in gaps if g.get("current_status") == "NOT_REGISTERED"]
    assert unregistered == []


# ── Supervisor gaps ──────────────────────────────────────────────


def test_supervisor_gaps_not_empty():
    gaps = generate_supervisor_gaps()
    assert len(gaps) >= 5
    assert all(g["stream"] == "supervisor" for g in gaps)


# ── All streams ──────────────────────────────────────────────────


def test_all_stream_gaps_has_4_streams():
    payload = generate_all_stream_gaps(sprint_id="R103")
    assert set(payload["streams"].keys()) == {"mainstream", "acceleration", "skills", "supervisor"}
    assert payload["sprint_id"] == "R103"
    assert payload["is_stale"] is False


def test_all_stream_gaps_total_matches():
    payload = generate_all_stream_gaps(sprint_id="R103")
    assert payload["total_gaps"] == sum(payload["streams"].values())
    assert payload["total_gaps"] == len(payload["gaps"])


def test_all_stream_gaps_no_stale_flag():
    payload = generate_all_stream_gaps(sprint_id="R103")
    assert payload["is_stale"] is False


def test_all_stream_gaps_with_matrix():
    matrix = {
        "commercial_net_products": [
            {
                "format": "FODS",
                "dogfood_status": {"csv_export": "GAP_DOGFOOD_EXTERNAL"},
            }
        ]
    }
    payload = generate_all_stream_gaps(matrix=matrix, sprint_id="R103")
    assert payload["streams"]["mainstream"] >= 1


def test_gap_ids_unique():
    payload = generate_all_stream_gaps(sprint_id="R103")
    ids = [g["gap_id"] for g in payload["gaps"]]
    assert len(ids) == len(set(ids)), f"Duplicate gap IDs found: {[x for x in ids if ids.count(x) > 1]}"
