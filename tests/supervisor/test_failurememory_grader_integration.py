"""Integration test: grade_declared_work.py write_outputs() records failures to FailureMemory.

TC-AMD-CONV-001: Proof advancement PROOF_LEVEL_2 → PROOF_LEVEL_3.
"""

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from grade_declared_work import write_outputs  # noqa: E402


def _make_review(grades: list[dict]) -> dict:
    """Build a minimal review dict for write_outputs."""
    accepted = [g for g in grades if g["supervisor_grade"] in ("ACCEPTED", "ACCEPTED_VERIFIED")]
    rework = [g for g in grades if g["supervisor_grade"] in ("REWORK_REQUIRED", "OVERCLAIMED")]
    rejected = [g for g in grades if g["supervisor_grade"] == "REJECTED"]
    overclaimed = [g for g in grades if g["supervisor_grade"] == "OVERCLAIMED"]
    return {
        "run_id": "test-conv-001",
        "sprint_id": "test-conv-001",
        "timestamp": "2026-06-24T12:00:00Z",
        "overall_verdict": "REWORK_REQUIRED" if rework else "ACCEPTED",
        "autonomous_continue": len(rework) == 0,
        "item_grades": grades,
        "accepted_items": [g["item_id"] for g in accepted],
        "rework_items": [g["item_id"] for g in rework],
        "rejected_items": [g["item_id"] for g in rejected],
        "overclaimed_items": [g["item_id"] for g in overclaimed],
        "critical_rework_count": len(rejected) + len(overclaimed),
    }


def test_write_outputs_records_rework_to_failure_memory(tmp_path):
    """write_outputs with REWORK_REQUIRED grades creates failure-memory entries."""
    # Set up a fake repo root with .git marker so FailureMemory can find it
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    (repo_root / ".local" / "supervisor").mkdir(parents=True)

    output_dir = repo_root / "review-output"
    output_dir.mkdir()

    grades = [
        {
            "item_id": "WI-GOOD",
            "item_title": "Good item",
            "supervisor_grade": "ACCEPTED_VERIFIED",
            "required_rework": None,
        },
        {
            "item_id": "WI-BAD",
            "item_title": "Bad item",
            "supervisor_grade": "REWORK_REQUIRED",
            "required_rework": "Evidence incomplete",
        },
    ]
    review = _make_review(grades)

    write_outputs(review, output_dir)

    # Verify failure-memory.json was created with the rework entry
    fm_path = repo_root / ".local" / "supervisor" / "failure-memory.json"
    assert fm_path.exists(), "failure-memory.json should be created"

    data = json.loads(fm_path.read_text(encoding="utf-8"))
    failures = data.get("failures", [])
    assert len(failures) >= 1, f"Expected at least 1 failure entry, got {len(failures)}"

    # Find the entry matching our rework item
    matching = [f for f in failures if f.get("root_cause") == "Evidence incomplete"]
    assert len(matching) == 1, f"Expected 1 matching failure, got {len(matching)}"
    assert matching[0]["category"] == "OVERCLAIM_FAILURE"
    assert matching[0]["sprint_discovered"] == "test-conv-001"


def test_write_outputs_no_failures_no_fm_entry(tmp_path):
    """write_outputs with all ACCEPTED grades creates no failure-memory entries."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()

    output_dir = repo_root / "review-output"
    output_dir.mkdir()

    grades = [
        {
            "item_id": "WI-OK",
            "item_title": "OK item",
            "supervisor_grade": "ACCEPTED_VERIFIED",
            "required_rework": None,
        },
    ]
    review = _make_review(grades)

    write_outputs(review, output_dir)

    fm_path = repo_root / ".local" / "supervisor" / "failure-memory.json"
    if fm_path.exists():
        data = json.loads(fm_path.read_text(encoding="utf-8"))
        # Should have 0 failures (FailureMemory.save() still creates file but with empty list)
        assert data.get("failure_count", 0) == 0


def test_write_outputs_overclaimed_uses_correct_category(tmp_path):
    """OVERCLAIMED grades use GRADING_FALSE_POSITIVE category."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()
    (repo_root / ".local" / "supervisor").mkdir(parents=True)

    output_dir = repo_root / "review-output"
    output_dir.mkdir()

    grades = [
        {
            "item_id": "WI-OVER",
            "item_title": "Overclaimed item",
            "supervisor_grade": "OVERCLAIMED",
            "required_rework": "Claimed done but no evidence",
        },
    ]
    review = _make_review(grades)

    write_outputs(review, output_dir)

    fm_path = repo_root / ".local" / "supervisor" / "failure-memory.json"
    assert fm_path.exists()
    data = json.loads(fm_path.read_text(encoding="utf-8"))
    failures = data.get("failures", [])
    matching = [f for f in failures if f.get("root_cause") == "Claimed done but no evidence"]
    assert len(matching) == 1
    assert matching[0]["category"] == "GRADING_FALSE_POSITIVE"
