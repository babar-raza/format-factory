"""Tests for anti-skip checker discovery and scoring fixes.

R100 regression tests:
- missing_raw_logs=true despite logs declared in reports/<run_id>/raw-logs/
- evidence_quality_score=0 for ACCEPTED_WITH_LIMITATIONS items with declared evidence

These tests verify the fixed discovery logic.
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))
from anti_skip_checker import (
    detect_missing_raw_logs,
    detect_evidence_quality_score,
    _item_has_backed_evidence,
)


class TestRawLogDiscovery:
    """Test that raw logs are discovered from multiple locations."""

    def test_evidence_root_direct_log_discovered(self, tmp_path):
        """Logs directly in evidence_root are discovered."""
        (tmp_path / "test-run.log").write_text("PASSED 100 tests")
        result = detect_missing_raw_logs(tmp_path, declaration=None)
        assert result["is_violation"] is False
        assert result["logs_found_count"] >= 1

    def test_evidence_root_raw_logs_subdir_discovered(self, tmp_path):
        """Logs in evidence_root/raw-logs/ are discovered."""
        raw_logs = tmp_path / "raw-logs"
        raw_logs.mkdir()
        (raw_logs / "sprint-tests.log").write_text("PASSED 200 tests")
        result = detect_missing_raw_logs(tmp_path, declaration=None)
        assert result["is_violation"] is False

    def test_r100_fix_reports_run_id_raw_logs_discovered(self, tmp_path):
        """R100 fix: logs declared in reports/<run_id>/raw-logs/ are discovered."""
        # Simulate: evidence_root = tmp_path/.local/evidences/my-run/
        # logs are in tmp_path/reports/my-run/raw-logs/
        evidence_root = tmp_path / ".local" / "evidences" / "my-run"
        evidence_root.mkdir(parents=True)
        log_dir = tmp_path / "reports" / "my-run" / "raw-logs"
        log_dir.mkdir(parents=True)
        (log_dir / "product-tests.log").write_text("PASSED 500 tests")

        declaration = {
            "run_id": "my-run",
            "evidence_root": ".local/evidences/my-run/",
        }
        result = detect_missing_raw_logs(evidence_root, declaration=declaration)
        assert result["is_violation"] is False, f"Expected log to be discovered but got: {result}"

    def test_declaration_artifact_type_log_discovered(self, tmp_path):
        """Declaration artifact with type='log' is discovered (R100 fix)."""
        log_file = tmp_path / "test-output.log"
        log_file.write_text("PASSED 300 tests")
        declaration = {
            "run_id": "test-run",
            "evidence_artifacts": [
                {"type": "log", "path": str(log_file), "description": "test log"},
            ],
        }
        result = detect_missing_raw_logs(tmp_path, declaration=declaration)
        assert result["is_violation"] is False

    def test_declaration_artifact_type_raw_log_still_discovered(self, tmp_path):
        """Declaration artifact with type='raw_log' still discovered (existing behavior)."""
        log_file = tmp_path / "test-output.log"
        log_file.write_text("PASSED 100 tests")
        declaration = {
            "run_id": "test-run",
            "evidence_artifacts": [
                {"type": "raw_log", "path": str(log_file), "description": "test log"},
            ],
        }
        result = detect_missing_raw_logs(tmp_path, declaration=declaration)
        assert result["is_violation"] is False

    def test_evidence_path_log_in_item_discovered(self, tmp_path):
        """Declared evidence_path ending in .log is discovered."""
        log_file = tmp_path / "reports" / "test-run" / "raw-logs" / "test.log"
        log_file.parent.mkdir(parents=True)
        log_file.write_text("PASSED 50 tests")
        declaration = {
            "run_id": "test-run",
            "planned_work_items": [
                {
                    "item_id": "ITEM-001",
                    "evidence_paths": [str(log_file)],
                }
            ],
        }
        result = detect_missing_raw_logs(tmp_path, declaration=declaration)
        assert result["is_violation"] is False

    def test_truly_missing_logs_still_fails(self, tmp_path):
        """When no logs exist anywhere, violation is True."""
        evidence_root = tmp_path / "evidence"
        evidence_root.mkdir()
        declaration = {"run_id": "empty-run", "evidence_artifacts": [], "planned_work_items": []}
        result = detect_missing_raw_logs(evidence_root, declaration=declaration)
        assert result["is_violation"] is True

    def test_nonexistent_evidence_root_checks_declaration(self, tmp_path):
        """Non-existent evidence_root still checks declaration artifacts."""
        log_file = tmp_path / "test.log"
        log_file.write_text("PASSED 10 tests")
        evidence_root = tmp_path / "nonexistent"  # doesn't exist
        declaration = {
            "run_id": "test-run",
            "evidence_artifacts": [
                {"type": "log", "path": str(log_file), "description": "log"},
            ],
        }
        result = detect_missing_raw_logs(evidence_root, declaration=declaration)
        assert result["is_violation"] is False

    def test_changed_file_log_discovered(self, tmp_path):
        """Log file in changed_files list is discovered."""
        log_file = tmp_path / "my-test.log"
        log_file.write_text("PASSED 200 tests")
        declaration = {
            "run_id": "test-run",
            "changed_files": [str(log_file)],
        }
        result = detect_missing_raw_logs(tmp_path, declaration=declaration)
        assert result["is_violation"] is False


class TestEvidenceQualityScore:
    """Test that evidence_quality_score correctly handles non-ACCEPTED_VERIFIED items."""

    def test_accepted_verified_scores_1(self):
        """ACCEPTED_VERIFIED item gives score=1.0."""
        grades = [{"item_id": "A", "supervisor_grade": "ACCEPTED_VERIFIED", "test_count": 10}]
        result = detect_evidence_quality_score(grades)
        assert result["is_violation"] is False
        assert result["score"] == 1.0

    def test_accepted_with_limitations_with_test_count_not_zero(self):
        """R100 fix: ACCEPTED_WITH_LIMITATIONS + test_count > 0 is not path-only."""
        grades = [
            {"item_id": "A", "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS", "test_count": 99},
        ]
        result = detect_evidence_quality_score(grades)
        assert result["is_violation"] is False, f"Expected not violation but got: {result}"
        assert result["backed_count"] >= 1

    def test_accepted_with_limitations_with_log_path_not_zero(self):
        """R100 fix: ACCEPTED_WITH_LIMITATIONS + log path in evidence = not path-only."""
        grades = [
            {
                "item_id": "A",
                "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS",
                "evidence_paths": ["reports/run/raw-logs/test.log"],
            },
        ]
        result = detect_evidence_quality_score(grades)
        assert result["is_violation"] is False

    def test_truly_path_only_is_violation(self):
        """Items with no test count, no log paths, no acceptance criteria = violation."""
        grades = [
            {"item_id": "A", "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS"},
            {"item_id": "B", "supervisor_grade": "ACCEPTED"},
        ]
        result = detect_evidence_quality_score(grades)
        assert result["is_violation"] is True
        assert result["score"] == 0.0

    def test_mixed_backed_and_path_only_not_violation(self):
        """Some backed items → not a violation even if others are path-only."""
        grades = [
            {"item_id": "A", "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS"},  # path-only
            {"item_id": "B", "supervisor_grade": "ACCEPTED_VERIFIED"},  # backed
        ]
        result = detect_evidence_quality_score(grades)
        assert result["is_violation"] is False

    def test_empty_grades_not_violation(self):
        """No accepted items → not a violation."""
        result = detect_evidence_quality_score([])
        assert result["is_violation"] is False

    def test_rejected_items_not_counted(self):
        """REJECTED items are not counted in quality score."""
        grades = [
            {"item_id": "A", "supervisor_grade": "REJECTED"},
            {"item_id": "B", "supervisor_grade": "ACCEPTED_VERIFIED", "test_count": 5},
        ]
        result = detect_evidence_quality_score(grades)
        assert result["accepted_count"] == 1
        assert result["is_violation"] is False


class TestItemHasBackedEvidence:
    """Unit tests for _item_has_backed_evidence helper."""

    def test_accepted_verified_is_backed(self):
        item = {"supervisor_grade": "ACCEPTED_VERIFIED"}
        assert _item_has_backed_evidence(item) is True

    def test_test_count_gt_zero_is_backed(self):
        item = {"supervisor_grade": "ACCEPTED_WITH_LIMITATIONS", "test_count": 100}
        assert _item_has_backed_evidence(item) is True

    def test_tests_run_field_is_backed(self):
        item = {"supervisor_grade": "ACCEPTED", "tests_run": 50}
        assert _item_has_backed_evidence(item) is True

    def test_acceptance_criteria_met_is_backed(self):
        item = {"supervisor_grade": "ACCEPTED", "acceptance_criteria_met": True}
        assert _item_has_backed_evidence(item) is True

    def test_raw_log_verified_is_backed(self):
        item = {"supervisor_grade": "ACCEPTED", "raw_log_verified": True}
        assert _item_has_backed_evidence(item) is True

    def test_log_evidence_path_is_backed(self):
        item = {
            "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS",
            "evidence_paths": ["reports/sprint/raw-logs/test.log"],
        }
        assert _item_has_backed_evidence(item) is True

    def test_plain_path_only_is_not_backed(self):
        item = {"supervisor_grade": "ACCEPTED_WITH_LIMITATIONS"}
        assert _item_has_backed_evidence(item) is False

    def test_zero_test_count_is_not_backed(self):
        item = {"supervisor_grade": "ACCEPTED", "test_count": 0}
        assert _item_has_backed_evidence(item) is False


class TestR100RegressionIntegration:
    """Integration test using R100-like fixture data."""

    def test_r100_like_logs_in_reports_not_missing(self, tmp_path):
        """R100-like setup: logs in reports/<run_id>/raw-logs/, not in evidence_root/."""
        run_id = "final-poc-authority-audit"
        evidence_root = tmp_path / ".local" / "evidences" / run_id
        evidence_root.mkdir(parents=True)

        # Create R100-style log locations
        for log_name in [
            "proof-backed-poc-gate-tests.log",
            "autonomous-train-executor-tests.log",
            "autonomous-host-runner-tests.log",
            "product-proof-tests.log",
            "dotnet-commercial-tests.log",
        ]:
            log_path = tmp_path / "reports" / run_id / "raw-logs" / log_name
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text("28 passed\n36 passed\n25 passed\n1295 passed\n1532 passed")

        declaration = {
            "run_id": run_id,
            "evidence_root": str(evidence_root),
            "planned_work_items": [
                {"item_id": "AUDIT-004", "evidence_paths": [
                    f"reports/{run_id}/raw-logs/proof-backed-poc-gate-tests.log",
                    f"reports/{run_id}/raw-logs/dotnet-commercial-tests.log",
                ]},
            ],
        }
        result = detect_missing_raw_logs(evidence_root, declaration=declaration)
        assert result["is_violation"] is False, (
            f"R100 regression: logs should be discovered from reports/{run_id}/raw-logs/ "
            f"but got: {result}"
        )

    def test_r100_like_grades_with_test_count_not_path_only(self):
        """R100-like grades: ACCEPTED_WITH_LIMITATIONS with tests declared."""
        grades = [
            {
                "item_id": "AUDIT-002",
                "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS",
                "test_count": 28,
            },
            {
                "item_id": "AUDIT-003",
                "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS",
                "evidence_paths": ["reports/host-autonomy-runner/raw-logs/sprint2-tests.log"],
            },
        ]
        result = detect_evidence_quality_score(grades)
        assert result["is_violation"] is False, (
            f"R100 regression: ACCEPTED_WITH_LIMITATIONS with test_count/log_paths "
            f"should not be path-only but got: {result}"
        )
