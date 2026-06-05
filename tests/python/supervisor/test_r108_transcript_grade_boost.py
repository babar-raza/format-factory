"""R108 Wave 3: Transcript-grade pipeline boost tests.

Verify that grade_item() treats transcript_validation.all_valid=True
as a concrete proof dimension for ACCEPTED_VERIFIED.
"""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS_DIR = str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from grade_declared_work import grade_item  # noqa: E402


def _make_inspection(item_id: str = "W1", transcript_validation=None, **kwargs):
    """Build a minimal item_inspection dict matching grade_item's expected shape."""
    tests_declared = kwargs.get("tests_declared", [])
    base = {
        "item_id": item_id,
        "declared_status": "completed",
        "has_evidence": True,
        "has_tests": bool(tests_declared),
        "evidence_paths_found": ["reports/test/some-report.md"],
        "evidence_paths_missing": [],
        "tests_declared": tests_declared,
        "tests_with_content": kwargs.get("tests_with_content", []),
        "tests_empty_or_stub": [],
        "acceptance_criteria_verified": kwargs.get("criteria_verified", False),
        "acceptance_criteria_pattern": kwargs.get("criteria_pattern", ""),
    }
    if transcript_validation is not None:
        base["transcript_validation"] = transcript_validation
    return base


class TestTranscriptBoostsVerified:
    """Valid transcript alone should produce ACCEPTED_VERIFIED."""

    def test_valid_transcript_gives_verified(self):
        insp = _make_inspection(
            transcript_validation={
                "transcripts_found": 1,
                "transcripts_valid": 1,
                "transcripts_invalid": 0,
                "all_valid": True,
                "valid_transcripts": [{"path": "t.json", "skill_id": "s1", "mode": "dry-run", "result": "PASS"}],
                "invalid_transcripts": [],
            }
        )
        grade = grade_item(insp, {"passed": 1, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"

    def test_invalid_transcript_no_boost(self):
        insp = _make_inspection(
            transcript_validation={
                "transcripts_found": 1,
                "transcripts_valid": 0,
                "transcripts_invalid": 1,
                "all_valid": False,
                "valid_transcripts": [],
                "invalid_transcripts": [{"path": "t.json", "errors": ["bad"]}],
            }
        )
        grade = grade_item(insp, {"passed": 1, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"

    def test_no_transcript_unchanged(self):
        insp = _make_inspection()
        grade = grade_item(insp, {"passed": 1, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"

    def test_mixed_transcript_no_boost(self):
        insp = _make_inspection(
            transcript_validation={
                "transcripts_found": 2,
                "transcripts_valid": 1,
                "transcripts_invalid": 1,
                "all_valid": False,
                "valid_transcripts": [{"path": "t1.json", "skill_id": "s1", "mode": "dry-run", "result": "PASS"}],
                "invalid_transcripts": [{"path": "t2.json", "errors": ["bad"]}],
            }
        )
        grade = grade_item(insp, {"passed": 1, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"

    def test_transcript_with_tests_still_verified(self):
        insp = _make_inspection(
            tests_declared=["tests/test_foo.py"],
            tests_with_content=["tests/test_foo.py"],
            transcript_validation={
                "transcripts_found": 1,
                "transcripts_valid": 1,
                "transcripts_invalid": 0,
                "all_valid": True,
                "valid_transcripts": [{"path": "t.json", "skill_id": "s1", "mode": "live", "result": "PASS"}],
                "invalid_transcripts": [],
            }
        )
        grade = grade_item(insp, {"passed": 5, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_VERIFIED"

    def test_transcript_boost_adds_criteria_met_entry(self):
        insp = _make_inspection(
            transcript_validation={
                "transcripts_found": 1,
                "transcripts_valid": 1,
                "transcripts_invalid": 0,
                "all_valid": True,
                "valid_transcripts": [{"path": "t.json", "skill_id": "s1", "mode": "dry-run", "result": "PASS"}],
                "invalid_transcripts": [],
            }
        )
        grade = grade_item(insp, {"passed": 1, "failed": 0})
        criteria = grade.get("acceptance_criteria_met", [])
        assert any("Transcript validation" in c for c in criteria)

    def test_none_transcript_validation_unchanged(self):
        insp = _make_inspection(transcript_validation=None)
        grade = grade_item(insp, {"passed": 1, "failed": 0})
        assert grade["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"
