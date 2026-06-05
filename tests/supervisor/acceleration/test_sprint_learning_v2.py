"""Tests for generate_sprint_learning.py v2 — R100 Train F."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from generate_sprint_learning import (
    generate_parallelization_suggestions,
    generate_repeated_command_inventory,
    generate_shallow_evidence_warnings,
    generate_all,
)


def _ledger(*lanes):
    return {"lanes": list(lanes)}


def _lane(lane_id, group="", deps=None, cmds=None, status="completed",
          tests=0, files=None, evidence=None):
    return {
        "lane_id": lane_id,
        "concurrency_group": group,
        "dependency_graph": deps or [],
        "commands": cmds or [],
        "status": status,
        "test_count": tests,
        "files_changed": files or [],
        "evidence_artifacts": evidence or [],
        "duration_seconds": 10,
        "blockers": [],
        "notes": "",
    }


def test_parallelization_no_groups():
    ledger = _ledger(_lane("L1"), _lane("L2"))
    result = generate_parallelization_suggestions(ledger, "S1")
    assert "No additional parallelization" in result


def test_parallelization_finds_independent_lanes():
    ledger = _ledger(
        _lane("L1", group="G1"),
        _lane("L2", group="G1"),
        _lane("L3", group="G1", deps=["L1"]),
    )
    result = generate_parallelization_suggestions(ledger, "S1")
    assert "L1" in result
    assert "L2" in result


def test_repeated_commands_none():
    ledger = _ledger(_lane("L1", cmds=["pytest"]), _lane("L2", cmds=["dotnet test"]))
    result = generate_repeated_command_inventory(ledger, "S1")
    assert "No repeated commands" in result


def test_repeated_commands_found():
    ledger = _ledger(
        _lane("L1", cmds=["pytest tests/"]),
        _lane("L2", cmds=["pytest tests/"]),
    )
    result = generate_repeated_command_inventory(ledger, "S1")
    assert "pytest tests/" in result
    assert "2 lanes" in result


def test_shallow_warnings_zero_tests():
    ledger = _ledger(_lane("L1", tests=0, files=["x.py"], evidence=["e.yaml"]))
    result = generate_shallow_evidence_warnings(ledger, "S1")
    assert "zero tests" in result


def test_shallow_warnings_no_files():
    ledger = _ledger(_lane("L1", tests=5, files=[], evidence=["e.yaml"]))
    result = generate_shallow_evidence_warnings(ledger, "S1")
    assert "no files changed" in result


def test_shallow_warnings_no_evidence():
    ledger = _ledger(_lane("L1", tests=5, files=["x.py"], evidence=[]))
    result = generate_shallow_evidence_warnings(ledger, "S1")
    assert "no evidence artifacts" in result


def test_shallow_warnings_all_ok():
    ledger = _ledger(_lane("L1", tests=5, files=["x.py"], evidence=["e.yaml"]))
    result = generate_shallow_evidence_warnings(ledger, "S1")
    assert "adequate evidence" in result


def test_generate_all_produces_7_files(tmp_path):
    ledger_path = tmp_path / "ledger.json"
    grades_path = tmp_path / "grades.json"
    gaps_path = tmp_path / "gaps.json"
    output_dir = tmp_path / "out"

    import json
    ledger_path.write_text(json.dumps({"lanes": [
        {"lane_id": "L1", "status": "completed", "duration_seconds": 10,
         "test_count": 5, "tests_passed": 5, "tests_failed": 0,
         "files_changed": ["x.py"], "commands": ["pytest"], "evidence_artifacts": ["e.yaml"],
         "concurrency_group": "", "dependency_graph": [], "blockers": [], "notes": ""}
    ]}))
    grades_path.write_text(json.dumps({"work_item_grades": []}))
    gaps_path.write_text(json.dumps({"selected_gaps": []}))

    outputs = generate_all("S1", ledger_path, grades_path, gaps_path, output_dir)
    assert len(outputs) == 7
    assert "parallelization-suggestions" in outputs
    assert "repeated-command-inventory" in outputs
    assert "shallow-evidence-warnings" in outputs


# --- v3 (R101): validate all 7 reports produce valid markdown ---


def test_learning_notes_has_sections():
    from generate_sprint_learning import generate_learning_notes
    ledger = _ledger(
        _lane("L1", tests=5, files=["a.py"]),
        _lane("L2", status="blocked"),
    )
    grades = [{"supervisor_grade": "ACCEPTED"}, {"supervisor_grade": "REJECTED"}]
    result = generate_learning_notes(ledger, grades, "R101")
    assert "What was fast" in result
    assert "What was slow" in result
    assert "What was blocked" in result
    assert "Grade summary" in result
    assert "ACCEPTED" in result
    assert "REJECTED" in result


def test_speed_bottlenecks_has_sections():
    from generate_sprint_learning import generate_speed_bottlenecks
    ledger = _ledger(
        _lane("L1", tests=5, files=["a.py"]),
        _lane("L2", status="failed"),
    )
    result = generate_speed_bottlenecks(ledger, "R101")
    assert "Speed Bottlenecks" in result
    assert "Blocked / Failed" in result


def test_next_agent_briefing_has_sections():
    from generate_sprint_learning import generate_next_agent_briefing
    ledger = _ledger(_lane("L1"))
    gaps = {"selected_gaps": [{"stream": "mainstream", "gap_id": "g1", "description": "test gap"}]}
    result = generate_next_agent_briefing(ledger, gaps, "R101")
    assert "Priority actions" in result
    assert "Remaining gaps" in result
    assert "Recommendations" in result


def test_skill_candidates_with_manual():
    from generate_sprint_learning import generate_skill_candidates
    ledger = _ledger(_lane("L1", cmds=["pytest tests/"]))
    result = generate_skill_candidates(ledger, "R101")
    assert "Skill Candidates" in result


def test_generate_all_files_exist(tmp_path):
    """Positive: all 7 files actually exist on disk after generate_all."""
    import json
    ledger_path = tmp_path / "ledger.json"
    grades_path = tmp_path / "grades.json"
    gaps_path = tmp_path / "gaps.json"
    output_dir = tmp_path / "out"

    ledger_path.write_text(json.dumps({"lanes": [
        {"lane_id": "L1", "status": "completed", "duration_seconds": 10,
         "test_count": 5, "tests_passed": 5, "tests_failed": 0,
         "files_changed": ["x.py"], "commands": ["pytest"], "evidence_artifacts": ["e.yaml"],
         "concurrency_group": "", "dependency_graph": [], "blockers": [], "notes": ""}
    ]}))
    grades_path.write_text(json.dumps({"work_item_grades": []}))
    gaps_path.write_text(json.dumps({"selected_gaps": []}))

    outputs = generate_all("S1", ledger_path, grades_path, gaps_path, output_dir)
    for name, path_str in outputs.items():
        assert Path(path_str).exists(), f"{name} file should exist at {path_str}"
        content = Path(path_str).read_text()
        assert len(content) > 10, f"{name} should have non-trivial content"


def test_generate_all_negative_missing_inputs(tmp_path):
    """Negative: missing input files should still produce reports (empty data)."""
    output_dir = tmp_path / "out"
    outputs = generate_all(
        "S1",
        tmp_path / "no-ledger.json",
        tmp_path / "no-grades.json",
        tmp_path / "no-gaps.json",
        output_dir,
    )
    assert len(outputs) == 7
    for name, path_str in outputs.items():
        assert Path(path_str).exists()
