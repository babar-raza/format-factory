"""Tests for generate_sprint_learning.py — sprint learning report generator."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from generate_sprint_learning import (
    generate_learning_notes,
    generate_speed_bottlenecks,
    generate_next_agent_briefing,
    generate_skill_candidates,
    generate_all,
)


SAMPLE_LEDGER = {
    "lanes": [
        {"lane_id": "L1", "status": "completed", "duration_seconds": 10,
         "test_count": 5, "tests_passed": 5, "blockers": [], "notes": "",
         "commands": ["pytest tests/"]},
        {"lane_id": "L2", "status": "completed", "duration_seconds": 60,
         "test_count": 10, "tests_passed": 8, "blockers": [], "notes": "",
         "commands": ["dotnet test"]},
        {"lane_id": "L3", "status": "blocked", "duration_seconds": None,
         "test_count": 0, "tests_passed": 0, "blockers": ["gate 11 required"],
         "notes": "manual step needed", "commands": []},
    ]
}

SAMPLE_GRADES = [
    {"item_id": "W1", "supervisor_grade": "ACCEPTED"},
    {"item_id": "W2", "supervisor_grade": "ACCEPTED"},
    {"item_id": "W3", "supervisor_grade": "REWORK_REQUIRED"},
]

SAMPLE_GAPS = {
    "selected_gaps": [
        {"gap_id": "g1", "stream": "mainstream", "description": "FODS save"},
        {"gap_id": "g2", "stream": "supervisor", "description": "Gate 11"},
    ]
}


def test_generate_learning_notes():
    notes = generate_learning_notes(SAMPLE_LEDGER, SAMPLE_GRADES, "SPRINT-001")
    assert "SPRINT-001" in notes
    assert "What was fast" in notes
    assert "What was slow" in notes
    assert "What was blocked" in notes
    assert "ACCEPTED" in notes


def test_generate_speed_bottlenecks():
    report = generate_speed_bottlenecks(SAMPLE_LEDGER, "SPRINT-001")
    assert "Speed Bottlenecks" in report
    assert "Total lane time" in report
    assert "Blocked" in report


def test_generate_next_agent_briefing():
    briefing = generate_next_agent_briefing(SAMPLE_LEDGER, SAMPLE_GAPS, "SPRINT-001")
    assert "Next Agent Briefing" in briefing
    assert "Priority actions" in briefing
    assert "Remaining gaps" in briefing
    assert "g1" in briefing


def test_generate_skill_candidates():
    candidates = generate_skill_candidates(SAMPLE_LEDGER, "SPRINT-001")
    assert "Skill Candidates" in candidates
    assert "raw test log capture" in candidates.lower() or "manual" in candidates.lower()


def test_generate_all_creates_files(tmp_path):
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(json.dumps(SAMPLE_LEDGER))

    grades_path = tmp_path / "grades.json"
    grades_path.write_text(json.dumps(SAMPLE_GRADES))

    gaps_path = tmp_path / "gaps.json"
    gaps_path.write_text(json.dumps(SAMPLE_GAPS))

    output_dir = tmp_path / "output"
    outputs = generate_all("SPRINT-001", ledger_path, grades_path, gaps_path, output_dir)

    assert len(outputs) == 7
    for name, path in outputs.items():
        assert Path(path).exists()
        content = Path(path).read_text(encoding="utf-8")
        assert len(content) > 0


def test_generate_all_empty_inputs(tmp_path):
    ledger_path = tmp_path / "empty_ledger.json"
    ledger_path.write_text(json.dumps({"lanes": []}))
    grades_path = tmp_path / "empty_grades.json"
    grades_path.write_text(json.dumps([]))
    gaps_path = tmp_path / "empty_gaps.json"
    gaps_path.write_text(json.dumps({}))

    output_dir = tmp_path / "output2"
    outputs = generate_all("SPRINT-EMPTY", ledger_path, grades_path, gaps_path, output_dir)
    assert len(outputs) == 7
