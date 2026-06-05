"""Tests for R106 autonomous cycle integration — anti-skip checks in cycle."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from anti_skip_checker import run_all_checks


def test_cycle_anti_skip_with_declaration(tmp_path):
    """Anti-skip checks work with a complete declaration (simulating cycle Step 3b)."""
    evidence_root = tmp_path / "reports" / "acceleration-r106"
    evidence_root.mkdir(parents=True)
    (evidence_root / "raw-test-log.txt").write_text("pytest output here")
    (evidence_root / "evidence-manifest.yaml").write_text("sprint_id: FORMAT-FACTORY-ACCELERATION-R106-TEST-001")
    (evidence_root / "dry-run-ledger.json").write_text("{}")
    samples = evidence_root / "sample-outputs"
    samples.mkdir()
    (samples / "check-result.json").write_text("{}")

    declaration = {
        "run_id": "acceleration-r106",
        "sprint_id": "FORMAT-FACTORY-ACCELERATION-R106-TEST-001",
        "evidence_root": str(evidence_root),
        "planned_work_items": [],
        "test_results": {"passed": 80, "failed": 0},
        "worker_self_verdict": "PASS",
        "reports_created": [],
        "git_status_final": "uncommitted changes — DIRTY_MULTI_STREAM_ACCUMULATED",
        "dirty_state_classification": "DIRTY_MULTI_STREAM_ACCUMULATED",
        "changed_files": [],
    }

    grades = [
        {"item_id": "W0", "supervisor_grade": "ACCEPTED_VERIFIED", "test_file_content_checked": True},
        {"item_id": "W1", "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS"},
    ]

    result = run_all_checks(
        prompt_text="Acceleration sprint: improve anti-skip tool and gap selector. Skills: registry. Supervisor: pipeline.",
        gaps_data={"sprint_id": "FORMAT-FACTORY-ACCELERATION-R106-TEST-001", "stream": "acceleration"},
        expected_sprint="FORMAT-FACTORY-ACCELERATION-R106-TEST-001",
        evidence_root=evidence_root,
        declaration=declaration,
        grades=grades,
        target_stream="acceleration",
        repo_root=tmp_path,
        sample_outputs_dir=samples,
        prior_test_count=50,
    )

    assert result["total_checks"] == 17
    # Should pass — evidence quality has at least one ACCEPTED_VERIFIED
    assert result["all_pass"] is True


def test_cycle_anti_skip_catches_regression(tmp_path):
    """Anti-skip catches test count regression in cycle context."""
    evidence_root = tmp_path / "reports" / "r106"
    evidence_root.mkdir(parents=True)
    (evidence_root / "raw-test-log.txt").write_text("output")
    (evidence_root / "evidence-manifest.yaml").write_text("ok")
    (evidence_root / "dry-run-ledger.json").write_text("{}")
    samples = evidence_root / "sample-outputs"
    samples.mkdir()
    (samples / "data.json").write_text("{}")

    declaration = {
        "run_id": "r106",
        "sprint_id": "SPRINT-R106",
        "evidence_root": str(evidence_root),
        "planned_work_items": [],
        "test_results": {"passed": 30, "failed": 0},
        "worker_self_verdict": "PASS",
        "reports_created": [],
        "git_status_final": "clean",
    }

    result = run_all_checks(
        evidence_root=evidence_root,
        declaration=declaration,
        grades=[{"item_id": "A1", "supervisor_grade": "ACCEPTED_VERIFIED", "test_file_content_checked": True}],
        repo_root=tmp_path,
        sample_outputs_dir=samples,
        prior_test_count=100,
    )

    # Should have a test_count_regression violation
    regression_checks = [c for c in result["checks"] if c["check"] == "test_count_regression"]
    assert len(regression_checks) == 1
    assert regression_checks[0]["is_violation"] is True


def test_cycle_anti_skip_catches_all_path_only(tmp_path):
    """Anti-skip catches when all items are path-only accepted."""
    evidence_root = tmp_path / "evidence"
    evidence_root.mkdir()
    (evidence_root / "raw-test-log.txt").write_text("output")
    (evidence_root / "evidence-manifest.yaml").write_text("ok")
    (evidence_root / "dry-run-ledger.json").write_text("{}")
    samples = evidence_root / "sample-outputs"
    samples.mkdir()
    (samples / "data.json").write_text("{}")

    declaration = {
        "run_id": "r106",
        "sprint_id": "SPRINT-R106",
        "evidence_root": str(evidence_root),
        "planned_work_items": [],
        "test_results": {"passed": 50, "failed": 0},
        "worker_self_verdict": "PASS",
        "reports_created": [],
        "git_status_final": "clean",
    }

    grades = [
        {"item_id": "W0", "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS"},
        {"item_id": "W1", "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS"},
    ]

    result = run_all_checks(
        evidence_root=evidence_root,
        declaration=declaration,
        grades=grades,
        repo_root=tmp_path,
        sample_outputs_dir=samples,
    )

    # Should have evidence_quality_score violation
    quality_checks = [c for c in result["checks"] if c["check"] == "evidence_quality_score"]
    assert len(quality_checks) == 1
    assert quality_checks[0]["is_violation"] is True
