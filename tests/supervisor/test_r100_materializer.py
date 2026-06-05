"""
R100 — Materializer Unit Tests
Tests materialize() with synthetic declarations and temp directories.
"""
import sys
import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from materialize_declared_evidence import materialize, verify_artifact, load_declaration


# ---------------------------------------------------------------------------
# verify_artifact
# ---------------------------------------------------------------------------

def test_verify_existing_artifact(tmp_path):
    f = tmp_path / "report.md"
    f.write_text("content")
    result = verify_artifact(tmp_path, "report.md")
    assert result["exists"] is True
    assert result["sha256"] is not None
    assert len(result["sha256"]) == 64
    assert result["size_bytes"] == 7


def test_verify_missing_artifact(tmp_path):
    result = verify_artifact(tmp_path, "missing.md")
    assert result["exists"] is False
    assert result["sha256"] is None


# ---------------------------------------------------------------------------
# materialize
# ---------------------------------------------------------------------------

def _write_declaration(tmp_path, items=None, changed_files=None, artifacts=None):
    decl = {
        "run_id": "test-mat-run",
        "sprint_id": "test-mat-sprint",
        "evidence_root": ".local/evidences/test-mat-run",
        "test_results": {"passed": 10, "failed": 0, "skipped": 0},
        "changed_files": changed_files or [],
        "planned_work_items": items or [],
        "evidence_artifacts": artifacts or [],
    }
    decl_path = tmp_path / "evidence-declaration.yaml"
    decl_path.write_text(yaml.dump(decl), encoding="utf-8")

    # Create evidence root
    evidence_dir = tmp_path / ".local" / "evidences" / "test-mat-run"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # Create reports/supervisor/ for summary output
    (tmp_path / "reports" / "supervisor").mkdir(parents=True, exist_ok=True)

    return decl_path


def test_materialize_all_artifacts_verified(tmp_path):
    # Create evidence files
    (tmp_path / "report.md").write_text("evidence report")

    decl_path = _write_declaration(
        tmp_path,
        items=[{
            "item_id": "W1",
            "title": "Work 1",
            "status": "completed",
            "evidence_paths": ["report.md"],
        }],
        artifacts=[{"path": "report.md", "type": "report"}],
    )

    out_dir = tmp_path / "materialized"
    result = materialize(decl_path, tmp_path, out_dir)

    assert result["exit_code"] == 0
    assert result["artifacts_verified"] >= 1
    assert result["artifacts_missing"] == 0
    assert (out_dir / "materialized-evidence-manifest.yaml").exists()
    assert (out_dir / "missing-evidence-report.md").exists()
    assert (out_dir / "source-change-diffs.patch").exists()

    # Check missing report says NONE
    report = (out_dir / "missing-evidence-report.md").read_text(encoding="utf-8")
    assert "NONE" in report


def test_materialize_with_missing_artifacts(tmp_path):
    decl_path = _write_declaration(
        tmp_path,
        items=[{
            "item_id": "W1",
            "title": "Work 1",
            "status": "completed",
            "evidence_paths": ["nonexistent.md"],
        }],
        artifacts=[{"path": "nonexistent.md", "type": "report"}],
    )

    out_dir = tmp_path / "materialized"
    result = materialize(decl_path, tmp_path, out_dir)

    assert result["exit_code"] == 2  # partial
    assert result["artifacts_missing"] >= 1

    # Missing report should list the file
    report = (out_dir / "missing-evidence-report.md").read_text(encoding="utf-8")
    assert "nonexistent.md" in report


def test_materialize_work_item_grades(tmp_path):
    (tmp_path / "done.md").write_text("completed work")

    decl_path = _write_declaration(
        tmp_path,
        items=[
            {"item_id": "A", "title": "Done Item", "status": "completed", "evidence_paths": ["done.md"]},
            {"item_id": "B", "title": "Partial Item", "status": "partial", "evidence_paths": []},
            {"item_id": "C", "title": "Blocked", "status": "blocked_external_gate", "evidence_paths": []},
        ],
    )

    out_dir = tmp_path / "materialized"
    result = materialize(decl_path, tmp_path, out_dir)

    grades = {g["item_id"]: g["supervisor_grade"] for g in result["work_item_grades"]}
    assert grades["A"] == "ACCEPTED"
    assert grades["B"] == "REWORK_REQUIRED"
    assert grades["C"] == "BLOCKED_EXTERNAL_GATE"


def test_materialize_summary_written(tmp_path):
    decl_path = _write_declaration(tmp_path)
    out_dir = tmp_path / "materialized"
    result = materialize(decl_path, tmp_path, out_dir)

    summary_path = tmp_path / "reports" / "supervisor" / "materialized-evidence-review.md"
    assert summary_path.exists()
    text = summary_path.read_text(encoding="utf-8")
    assert "Materialized Evidence Review" in text
    assert "test-mat-run" in text


def test_load_declaration(tmp_path):
    decl = {"run_id": "foo", "sprint_id": "bar"}
    p = tmp_path / "decl.yaml"
    p.write_text(yaml.dump(decl), encoding="utf-8")
    loaded = load_declaration(p)
    assert loaded["run_id"] == "foo"
    assert loaded["sprint_id"] == "bar"
