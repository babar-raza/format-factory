"""Regression tests for Fix 3: _check_skill_transcript_existence().

TC-SGOV-021: Verify that skill_transcript evidence artifacts are checked for
file existence on disk (WARN level, not ERROR).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from sprint_executor_validate import _check_skill_transcript_existence


def test_valid_transcript_no_warning(tmp_path):
    """Skill transcript that exists on disk produces no warning."""
    transcript = tmp_path / "transcript.json"
    transcript.write_text("{}", encoding="utf-8")
    doc = {
        "evidence_artifacts": [
            {"type": "skill_transcript", "path": "transcript.json"}
        ]
    }
    warnings = _check_skill_transcript_existence(doc, tmp_path)
    assert warnings == []


def test_missing_transcript_produces_warning(tmp_path):
    """Skill transcript file that does not exist produces a WARN."""
    doc = {
        "evidence_artifacts": [
            {"type": "skill_transcript", "path": "nonexistent/transcript.json"}
        ]
    }
    warnings = _check_skill_transcript_existence(doc, tmp_path)
    assert len(warnings) == 1
    assert "missing on disk" in warnings[0]
    assert "nonexistent/transcript.json" in warnings[0]


def test_empty_path_produces_warning(tmp_path):
    """Skill transcript with empty path produces a WARN."""
    doc = {
        "evidence_artifacts": [
            {"type": "skill_transcript", "path": ""}
        ]
    }
    warnings = _check_skill_transcript_existence(doc, tmp_path)
    assert len(warnings) == 1
    assert "empty path" in warnings[0]


def test_non_transcript_artifact_skipped(tmp_path):
    """Non-skill_transcript artifacts are not checked."""
    doc = {
        "evidence_artifacts": [
            {"type": "regression_test", "path": "nonexistent.py"},
            {"type": "inventory", "path": "also-missing.yaml"},
        ]
    }
    warnings = _check_skill_transcript_existence(doc, tmp_path)
    assert warnings == []


def test_no_evidence_artifacts(tmp_path):
    """Declaration with no evidence_artifacts returns empty list."""
    doc = {}
    warnings = _check_skill_transcript_existence(doc, tmp_path)
    assert warnings == []


def test_mixed_valid_and_missing(tmp_path):
    """Multiple transcripts: only missing ones produce warnings."""
    (tmp_path / "exists.json").write_text("{}", encoding="utf-8")
    doc = {
        "evidence_artifacts": [
            {"type": "skill_transcript", "path": "exists.json"},
            {"type": "skill_transcript", "path": "missing.json"},
        ]
    }
    warnings = _check_skill_transcript_existence(doc, tmp_path)
    assert len(warnings) == 1
    assert "missing.json" in warnings[0]


def test_non_dict_artifact_skipped(tmp_path):
    """Non-dict entries in evidence_artifacts are skipped gracefully."""
    doc = {
        "evidence_artifacts": [
            "not-a-dict",
            {"type": "skill_transcript", "path": "missing.json"},
        ]
    }
    warnings = _check_skill_transcript_existence(doc, tmp_path)
    assert len(warnings) == 1
    assert "missing.json" in warnings[0]
