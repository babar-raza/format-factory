"""
R102 — Replay Tests for 3 Review Packages with Accurate Classification
Verifies replay of acceleration-r102, mainstream-r104, supervisor-r101.
Key R102 requirement: classification is accurate (not rubber-stamp all-accepted).

Tests:
  - Package existence and self-containment
  - Stream detection from sprint_id
  - Grade distribution accuracy (grading engine can produce non-ACCEPTED)
  - Declaration-review package detection (not legacy)
"""
import json
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from generate_supervisor_packet import detect_stream_from_sprint_id
from grade_declared_work import grade_item

REVIEW_BASE = REPO_ROOT / ".local" / "supervisor" / "reviews"

PACKAGES = {
    "acceleration-r102": "acceleration",
    "mainstream-r104": "mainstream",
    "supervisor-r101": "supervisor",
}


def _get_zip(run_id: str) -> Path:
    return REVIEW_BASE / run_id / "declaration-review-package.zip"


def _load_yaml_from_zip(zip_path: Path, suffix: str) -> dict:
    with zipfile.ZipFile(zip_path, "r") as zf:
        matches = [n for n in zf.namelist() if n.endswith(suffix)]
        if not matches:
            return {}
        with zf.open(matches[0]) as f:
            return yaml.safe_load(f.read().decode("utf-8")) or {}


def _load_json_from_zip(zip_path: Path, suffix: str):
    with zipfile.ZipFile(zip_path, "r") as zf:
        matches = [n for n in zf.namelist() if n.endswith(suffix)]
        if not matches:
            return None
        with zf.open(matches[0]) as f:
            return json.loads(f.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# Package existence
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("run_id", list(PACKAGES.keys()))
def test_package_exists(run_id):
    if not REVIEW_BASE.exists():
        pytest.skip(".local/supervisor/reviews/ does not exist (gitignored, CI skip)")
    assert _get_zip(run_id).exists(), f"Missing: {_get_zip(run_id)}"


# ---------------------------------------------------------------------------
# Stream detection
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("run_id,expected", list(PACKAGES.items()))
def test_stream_detection(run_id, expected):
    path = _get_zip(run_id)
    if not path.exists():
        pytest.skip("missing")
    decl = _load_yaml_from_zip(path, "evidence-declaration.yaml")
    sid = decl.get("sprint_id", "")
    assert detect_stream_from_sprint_id(sid) == expected


# ---------------------------------------------------------------------------
# Declaration-review package detection (not legacy)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("run_id", list(PACKAGES.keys()))
def test_is_declaration_review_package(run_id):
    """Package should be detected as declaration-review, not legacy."""
    path = _get_zip(run_id)
    if not path.exists():
        pytest.skip("missing")
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()
        has_decl = any("evidence-declaration.yaml" in n for n in names)
        has_supervisor = any("supervisor/" in n or "supervisor-" in n for n in names)
        # Must NOT have legacy markers
        has_final_verdict = any("final-verdict.md" in n for n in names)
        has_bundle_metadata = any("bundle-metadata/" in n for n in names)
    assert has_decl, "Missing evidence-declaration.yaml"
    assert has_supervisor, "Missing supervisor artifacts"
    assert not has_final_verdict, "Should not have legacy final-verdict.md"
    assert not has_bundle_metadata, "Should not have legacy bundle-metadata/"


# ---------------------------------------------------------------------------
# Grades exist and are valid enums
# ---------------------------------------------------------------------------

VALID_GRADES = {
    "ACCEPTED_VERIFIED", "ACCEPTED_WITH_LIMITATIONS", "ACCEPTED",
    "ACCEPTED_WITH_WARNINGS", "REWORK_REQUIRED", "REJECTED",
    "BLOCKED_EXTERNAL_GATE", "NOT_ATTEMPTED", "NOT_IN_SCOPE",
    "OVERCLAIMED", "INSUFFICIENT_EVIDENCE", "DEFERRED_WITH_REASON",
}


@pytest.mark.parametrize("run_id", list(PACKAGES.keys()))
def test_grades_valid_enums(run_id):
    path = _get_zip(run_id)
    if not path.exists():
        pytest.skip("missing")
    data = _load_json_from_zip(path, "item-grades.json")
    if data is None:
        pytest.skip("no grades")
    grades_list = data if isinstance(data, list) else data.get("grades", [])
    assert len(grades_list) > 0, "Empty grades"
    for g in grades_list:
        assert g["supervisor_grade"] in VALID_GRADES


# ---------------------------------------------------------------------------
# Accurate classification: grading engine does NOT rubber-stamp
# ---------------------------------------------------------------------------

def test_grade_engine_rejects_missing_evidence():
    """Grading engine produces OVERCLAIMED for completed item with no evidence."""
    inspection = {
        "item_id": "REPLAY-01",
        "declared_status": "completed",
        "has_evidence": False,
        "has_tests": False,
        "evidence_paths_missing": ["some/path.py"],
        "evidence_paths_found": [],
    }
    g = grade_item(inspection, {"failed": 0})
    assert g["supervisor_grade"] == "OVERCLAIMED"


def test_grade_engine_rejects_missing_paths():
    """Grading engine produces REWORK_REQUIRED for completed item with missing paths."""
    inspection = {
        "item_id": "REPLAY-02",
        "declared_status": "completed",
        "has_evidence": True,
        "has_tests": True,
        "evidence_paths_missing": ["missing/file.py"],
        "evidence_paths_found": ["found/file.py"],
        "tests_declared": ["test_something"],
    }
    g = grade_item(inspection, {"failed": 0})
    assert g["supervisor_grade"] == "REWORK_REQUIRED"


def test_grade_engine_rejects_failed_tests():
    """Grading engine produces REWORK_REQUIRED for completed item with test failures."""
    inspection = {
        "item_id": "REPLAY-03",
        "declared_status": "completed",
        "has_evidence": True,
        "has_tests": True,
        "evidence_paths_missing": [],
        "evidence_paths_found": ["found/file.py"],
        "tests_declared": ["test_something"],
    }
    g = grade_item(inspection, {"failed": 1})
    assert g["supervisor_grade"] == "REWORK_REQUIRED"


def test_grade_engine_accepts_with_limitations_for_stub_tests():
    """Grading engine produces ACCEPTED_WITH_LIMITATIONS for stub tests."""
    inspection = {
        "item_id": "REPLAY-04",
        "declared_status": "completed",
        "has_evidence": True,
        "has_tests": True,
        "evidence_paths_missing": [],
        "evidence_paths_found": ["found/file.py"],
        "tests_declared": ["test_something"],
        "tests_with_content": [],
        "tests_empty_or_stub": ["test_stub.py"],
    }
    g = grade_item(inspection, {"failed": 0})
    assert g["supervisor_grade"] == "ACCEPTED_WITH_LIMITATIONS"


def test_grade_engine_defers_with_reason():
    """Grading engine produces DEFERRED_WITH_REASON for deferred items."""
    inspection = {
        "item_id": "REPLAY-05",
        "declared_status": "deferred",
        "has_evidence": False,
        "has_tests": False,
    }
    g = grade_item(inspection, {"failed": 0})
    assert g["supervisor_grade"] == "DEFERRED_WITH_REASON"


def test_grade_engine_not_all_accepted_on_mixed_input():
    """Given a mix of complete/partial/missing items, engine produces mixed grades."""
    items = [
        {"item_id": "A", "declared_status": "completed", "has_evidence": True,
         "has_tests": True, "evidence_paths_missing": [], "evidence_paths_found": ["f"],
         "tests_declared": ["t"]},
        {"item_id": "B", "declared_status": "completed", "has_evidence": False,
         "has_tests": False, "evidence_paths_missing": ["m"], "evidence_paths_found": []},
        {"item_id": "C", "declared_status": "partial", "has_evidence": True,
         "has_tests": False, "evidence_paths_found": ["f"]},
        {"item_id": "D", "declared_status": "not_started", "has_evidence": False,
         "has_tests": False},
    ]
    grades = [grade_item(i, {"failed": 0})["supervisor_grade"] for i in items]
    accepted_count = sum(1 for g in grades if "ACCEPTED" in g)
    non_accepted_count = len(grades) - accepted_count
    assert non_accepted_count >= 2, f"Expected at least 2 non-accepted, got grades: {grades}"
