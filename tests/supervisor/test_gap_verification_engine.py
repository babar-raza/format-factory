"""Tests for gap_verification_engine.py — multi-level gap verification.

TC-FL-014: Phase 5 of the feedback loop redesign (pure-knitting-dusk plan).
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from gap_verification_engine import verify_level_0, verify_level_1, verify_level_2, verify_closed_gaps


# ── Level 0 Tests ─────────────────────────────────────────────────────────────

class TestLevel0:
    """Level 0: test file exists matching capability name."""

    def test_pass_when_test_file_exists(self, tmp_path):
        """Create a test file matching the capability name."""
        test_dir = tmp_path / "tests" / "python" / "csv"
        test_dir.mkdir(parents=True)
        (test_dir / "test_csv_probe.py").write_text("# test", encoding="utf-8")

        result = verify_level_0("CSV", "Probe", tmp_path)
        assert result["verdict"] == "PASS"
        assert "test_csv_probe.py" in result["test_files"]

    def test_fail_no_matching_file(self, tmp_path):
        test_dir = tmp_path / "tests" / "python" / "csv"
        test_dir.mkdir(parents=True)
        (test_dir / "test_csv_other.py").write_text("# test", encoding="utf-8")

        result = verify_level_0("CSV", "Save Same Format", tmp_path)
        assert result["verdict"] == "FAIL"

    def test_fail_missing_dir(self, tmp_path):
        result = verify_level_0("nonexistent", "Load", tmp_path)
        assert result["verdict"] == "FAIL"
        assert "not found" in result["reason"]

    def test_case_insensitive_match(self, tmp_path):
        test_dir = tmp_path / "tests" / "python" / "fods"
        test_dir.mkdir(parents=True)
        (test_dir / "test_fods_LOAD_roundtrip.py").write_text("# test", encoding="utf-8")

        result = verify_level_0("FODS", "load", tmp_path)
        assert result["verdict"] == "PASS"


# ── Level 1 Tests ─────────────────────────────────────────────────────────────

class TestLevel1:
    """Level 1: matching tests execute and pass."""

    def test_pass_when_tests_pass(self, tmp_path):
        test_dir = tmp_path / "tests" / "python" / "csv"
        test_dir.mkdir(parents=True)
        (test_dir / "test_csv_probe.py").write_text("# test", encoding="utf-8")

        result = verify_level_1("CSV", "Probe", {"passed": 12, "failed": 0}, tmp_path)
        assert result["verdict"] == "PASS"
        assert result["passed"] == 12
        assert result["level_0"]["verdict"] == "PASS"

    def test_fail_when_tests_failing(self, tmp_path):
        test_dir = tmp_path / "tests" / "python" / "csv"
        test_dir.mkdir(parents=True)
        (test_dir / "test_csv_probe.py").write_text("# test", encoding="utf-8")

        result = verify_level_1("CSV", "Probe", {"passed": 10, "failed": 2}, tmp_path)
        assert result["verdict"] == "FAIL"
        assert result["failed"] == 2

    def test_fail_when_l0_fails(self, tmp_path):
        result = verify_level_1("nonexistent", "Load", {"passed": 5, "failed": 0}, tmp_path)
        assert result["verdict"] == "FAIL"
        assert result["reason"] == "L0 prerequisite failed"

    def test_fail_zero_passed(self, tmp_path):
        test_dir = tmp_path / "tests" / "python" / "csv"
        test_dir.mkdir(parents=True)
        (test_dir / "test_csv_probe.py").write_text("# test", encoding="utf-8")

        result = verify_level_1("CSV", "Probe", {"passed": 0, "failed": 0}, tmp_path)
        assert result["verdict"] == "FAIL"


# ── Level 2 Tests ─────────────────────────────────────────────────────────────

class TestLevel2:
    """Level 2: graded declaration cites gap with ACCEPTED evidence."""

    def test_pass_accepted_verified(self):
        result = verify_level_2({
            "supervisor_grade": "ACCEPTED_VERIFIED",
            "item_id": "WI-1",
            "evidence_paths_found": ["tests/test_x.py"],
        })
        assert result["verdict"] == "PASS"
        assert result["grade"] == "ACCEPTED_VERIFIED"

    def test_fail_overclaimed(self):
        result = verify_level_2({
            "supervisor_grade": "OVERCLAIMED",
            "item_id": "WI-2",
            "evidence_paths_found": [],
        })
        assert result["verdict"] == "FAIL"

    def test_fail_rework_required(self):
        result = verify_level_2({
            "supervisor_grade": "REWORK_REQUIRED",
            "item_id": "WI-3",
        })
        assert result["verdict"] == "FAIL"

    def test_pass_accepted_with_limitations(self):
        result = verify_level_2({
            "supervisor_grade": "ACCEPTED_WITH_LIMITATIONS",
            "item_id": "WI-4",
        })
        assert result["verdict"] == "PASS"


# ── verify_closed_gaps Tests ─────────────────────────────────────────────────

class TestVerifyClosedGaps:
    """End-to-end verification of closed gaps."""

    def test_assigns_level_2_for_accepted(self, tmp_path):
        test_dir = tmp_path / "tests" / "python" / "csv"
        test_dir.mkdir(parents=True)
        (test_dir / "test_csv_probe_csv.py").write_text("# test", encoding="utf-8")

        closure_result = {
            "closed": 1,
            "closures_applied": [
                ("GAP-CSV-FOSS-PROBE_CSV-001", {
                    "item_id": "WI-1",
                    "supervisor_grade": "ACCEPTED_VERIFIED",
                    "evidence_paths_found": ["tests/python/csv/test_csv_probe_csv.py"],
                }),
            ],
        }
        verifications = verify_closed_gaps(
            closure_result, {"passed": 10, "failed": 0}, {}, tmp_path
        )
        assert len(verifications) == 1
        v = verifications[0]
        assert v["gap_id"] == "GAP-CSV-FOSS-PROBE_CSV-001"
        assert v["verification_level"] == 2
        assert v["level_2"]["verdict"] == "PASS"

    def test_empty_closures(self, tmp_path):
        closure_result = {"closed": 0, "closures_applied": []}
        verifications = verify_closed_gaps(closure_result, {}, {}, tmp_path)
        assert len(verifications) == 0

    def test_unparseable_gap_id(self, tmp_path):
        closure_result = {
            "closed": 1,
            "closures_applied": [
                ("BADID", {
                    "supervisor_grade": "ACCEPTED_VERIFIED",
                    "item_id": "WI-BAD",
                }),
            ],
        }
        verifications = verify_closed_gaps(closure_result, {}, {}, tmp_path)
        assert len(verifications) == 1
        # L0 and L1 should be SKIP or FAIL, L2 should still work
        assert verifications[0]["level_2"]["verdict"] == "PASS"
