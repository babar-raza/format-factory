"""
R100 — Bridge to Legacy Format Unit Tests
Tests bridge_to_legacy_format() output structure and content.
"""
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from autonomous_cycle import bridge_to_legacy_format


def _make_review(verdict="ACCEPTED", accepted=None, rework=None, overclaimed=None, rejected=None):
    return {
        "run_id": "test-bridge",
        "sprint_id": "test-sprint",
        "overall_verdict": verdict,
        "item_grades": [],
        "accepted_items": accepted or ["A", "B"],
        "rework_items": rework or [],
        "rejected_items": rejected or [],
        "overclaimed_items": overclaimed or [],
        "autonomous_continue": True,
        "critical_rework_count": len(overclaimed or []) + len(rejected or []),
    }


def _make_manifest(exit_code=0, autonomous_continue=True):
    return {
        "sprint_id": "test-sprint",
        "timestamp": "2026-06-03T00:00:00",
        "exit_code": exit_code,
        "autonomous_continue": autonomous_continue,
    }


def _make_decl():
    return {
        "test_results": {"passed": 100, "failed": 0, "skipped": 2},
        "evidence_root": ".local/evidences/test-bridge",
        "git_head_end": "abc123",
    }


def test_bridge_writes_evidence_review_json(tmp_path):
    review = _make_review()
    manifest = _make_manifest()
    decl = _make_decl()

    # Create reports/supervisor/ in tmp_path
    sup_dir = tmp_path / "reports" / "supervisor"
    sup_dir.mkdir(parents=True, exist_ok=True)

    bridge_to_legacy_format(review, manifest, decl, tmp_path)

    er_path = sup_dir / "evidence-review.json"
    assert er_path.exists()
    er = json.loads(er_path.read_text(encoding="utf-8"))
    assert er["sprint_id"] == "test-sprint"
    assert er["verdict"] == "ACCEPTED"
    assert er["facts"]["test_count"] == 100
    assert er["facts"]["fail_count"] == 0
    assert er["facts"]["skip_count"] == 2


def test_bridge_writes_contradictions_json(tmp_path):
    review = _make_review()
    manifest = _make_manifest()
    decl = _make_decl()

    sup_dir = tmp_path / "reports" / "supervisor"
    sup_dir.mkdir(parents=True, exist_ok=True)

    bridge_to_legacy_format(review, manifest, decl, tmp_path)

    c_path = sup_dir / "contradictions.json"
    assert c_path.exists()
    c = json.loads(c_path.read_text(encoding="utf-8"))
    assert c["overall"] == "CLEAN"
    assert c["critical_count"] == 0
    assert c["autonomous_continue"] is True


def test_bridge_with_overclaimed_produces_critical_contradictions(tmp_path):
    review = _make_review(
        verdict="ACCEPTED_WITH_REWORK",
        overclaimed=["X1"],
    )
    review["item_grades"] = [
        {"item_id": "X1", "item_title": "Bad Item", "supervisor_grade": "OVERCLAIMED",
         "required_rework": "Missing evidence"},
    ]
    manifest = _make_manifest(exit_code=3, autonomous_continue=False)
    decl = _make_decl()

    sup_dir = tmp_path / "reports" / "supervisor"
    sup_dir.mkdir(parents=True, exist_ok=True)

    bridge_to_legacy_format(review, manifest, decl, tmp_path)

    c = json.loads((sup_dir / "contradictions.json").read_text(encoding="utf-8"))
    assert c["overall"] == "CRITICAL_CONTRADICTIONS"
    assert c["critical_count"] >= 1
    assert any("OVERCLAIMED" in ct["description"] for ct in c["contradictions"])


def test_bridge_with_test_failures(tmp_path):
    review = _make_review()
    manifest = _make_manifest()
    decl = {
        "test_results": {"passed": 95, "failed": 5, "skipped": 0},
        "evidence_root": "",
        "git_head_end": "abc123",
    }

    sup_dir = tmp_path / "reports" / "supervisor"
    sup_dir.mkdir(parents=True, exist_ok=True)

    bridge_to_legacy_format(review, manifest, decl, tmp_path)

    c = json.loads((sup_dir / "contradictions.json").read_text(encoding="utf-8"))
    assert c["critical_count"] >= 1
    assert any("failed" in ct["description"].lower() for ct in c["contradictions"])


def test_bridge_evidence_review_bundle_validation(tmp_path):
    """evidence-review.json bundle_validation_pass reflects exit code."""
    review = _make_review()
    manifest = _make_manifest(exit_code=9)  # error
    decl = _make_decl()

    sup_dir = tmp_path / "reports" / "supervisor"
    sup_dir.mkdir(parents=True, exist_ok=True)

    bridge_to_legacy_format(review, manifest, decl, tmp_path)

    er = json.loads((sup_dir / "evidence-review.json").read_text(encoding="utf-8"))
    assert er["bundle_validation_pass"] is False  # exit 9 → not pass
