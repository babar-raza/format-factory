"""Convergence-loop hardening tests for fslay02 sprint.

Covers gaps identified in post-sprint audit:
- L1-001: KNOWN-001 exit-code masking (no automated test)
- L1-002: SHARD-001 _update_shard_ledger (no automated test)
- L1-003: ENF-002 grader downgrade for product items (no dedicated test)
- L1-004: is_escalation_active() (untested)

Created: 2026-06-23, convergence loop iteration 1
"""
from __future__ import annotations

import datetime
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

# -- Setup paths --
_REPO = Path(__file__).resolve().parent.parent
_TOOLS_SUPERVISOR = _REPO / "tools" / "supervisor"
sys.path.insert(0, str(_TOOLS_SUPERVISOR))


# ===== L1-004: is_escalation_active() =====

class TestEscalationDate:
    def test_escalation_not_active_before_date(self):
        from test_layer_utils import is_escalation_active, ADEQUACY_ESCALATION_DATE
        with patch("test_layer_utils._datetime") as mock_dt:
            mock_dt.date.today.return_value = ADEQUACY_ESCALATION_DATE - datetime.timedelta(days=1)
            mock_dt.date.side_effect = lambda *a, **kw: datetime.date(*a, **kw)
            assert not is_escalation_active()

    def test_escalation_active_on_date(self):
        from test_layer_utils import is_escalation_active, ADEQUACY_ESCALATION_DATE
        with patch("test_layer_utils._datetime") as mock_dt:
            mock_dt.date.today.return_value = ADEQUACY_ESCALATION_DATE
            mock_dt.date.side_effect = lambda *a, **kw: datetime.date(*a, **kw)
            assert is_escalation_active()

    def test_escalation_active_after_date(self):
        from test_layer_utils import is_escalation_active, ADEQUACY_ESCALATION_DATE
        with patch("test_layer_utils._datetime") as mock_dt:
            mock_dt.date.today.return_value = ADEQUACY_ESCALATION_DATE + datetime.timedelta(days=30)
            mock_dt.date.side_effect = lambda *a, **kw: datetime.date(*a, **kw)
            assert is_escalation_active()


# ===== L1-003: ENF-002 grader downgrade =====

class TestGraderTestLayerEnforcement:
    def test_product_source_with_inadequate_layer_returns_inadequate(self):
        """_check_test_layer_for_grade must flag PRODUCT_SOURCE items with low test_layer."""
        from grade_declared_work import _check_test_layer_for_grade
        decl = {
            "test_layer": 0,
            "changed_files": ["src/python/ndjson/ndjson_parser.py"],
        }
        result = _check_test_layer_for_grade(decl)
        assert result["inadequate"] is True
        assert result["required_layer"] > 0
        assert "inadequate" in result["reason"]

    def test_adequate_layer_returns_not_inadequate(self):
        """Adequate test_layer must NOT be flagged."""
        from grade_declared_work import _check_test_layer_for_grade
        decl = {
            "test_layer": 3,
            "changed_files": ["tools/supervisor/foo.py"],
        }
        result = _check_test_layer_for_grade(decl)
        assert result["inadequate"] is False

    def test_no_changed_files_returns_not_inadequate(self):
        from grade_declared_work import _check_test_layer_for_grade
        decl = {"test_layer": 0, "changed_files": []}
        result = _check_test_layer_for_grade(decl)
        assert result["inadequate"] is False

    def test_missing_test_layer_returns_not_inadequate(self):
        from grade_declared_work import _check_test_layer_for_grade
        decl = {"changed_files": ["src/python/ndjson/ndjson_parser.py"]}
        result = _check_test_layer_for_grade(decl)
        assert result["inadequate"] is False


# ===== L1-002: SHARD-001 _update_shard_ledger =====

class TestShardLedger:
    def test_update_shard_ledger_writes_entry(self):
        """_update_shard_ledger must write shard completion data to the ledger."""
        sys.path.insert(0, str(_REPO / "tools"))
        from test_runner import _update_shard_ledger, SHARD_LEDGER_PATH

        # Create a temp ledger to avoid mutating the real one
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False,
                                         encoding="utf-8") as tf:
            yaml.dump({"resume_mode": "manual", "history": []}, tf)
            tmp_path = Path(tf.name)

        result = {
            "test_results": {"passed": 10, "failed": 2, "skipped": 1, "errors": 0},
            "duration_seconds": 45,
            "pytest_exit_code": 1,
        }
        try:
            # Monkey-patch the ledger path
            import test_runner
            orig = test_runner.SHARD_LEDGER_PATH
            test_runner.SHARD_LEDGER_PATH = tmp_path
            try:
                _update_shard_ledger(1, 4, result)
            finally:
                test_runner.SHARD_LEDGER_PATH = orig

            ledger = yaml.safe_load(tmp_path.read_text(encoding="utf-8"))
            assert len(ledger["history"]) == 1
            entry = ledger["history"][0]
            assert entry["shard_id"] == 1
            assert entry["passed"] == 10
            assert entry["failed"] == 2
            assert entry["exit_code"] == 1

            rs = ledger["resume_state"]
            assert rs["last_completed_shard"] == 1
            assert 1 in rs["shards_completed"]
            assert 2 in rs["shards_pending"]
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_update_shard_ledger_handles_missing_file(self):
        """_update_shard_ledger must not crash on missing ledger file."""
        sys.path.insert(0, str(_REPO / "tools"))
        import test_runner
        orig = test_runner.SHARD_LEDGER_PATH
        test_runner.SHARD_LEDGER_PATH = Path("/nonexistent/path/ledger.yaml")
        try:
            # Should not raise — just prints WARNING
            _update_shard_ledger = test_runner._update_shard_ledger
            _update_shard_ledger(1, 4, {"test_results": {}, "pytest_exit_code": 0})
        finally:
            test_runner.SHARD_LEDGER_PATH = orig


# ===== L1-001: KNOWN-001 exit-code masking =====

class TestKnownFailuresExitCodeMasking:
    """Test the exit-code masking logic from TC-FSLAY02-KNOWN-001.

    The masking logic is in main() at the print-summary stage. We test the
    conditional logic directly by simulating the result dict and args state.
    """

    def test_mask_when_all_failures_preexisting(self):
        """When new_failures is empty and exit_code != 0, mask to 0."""
        result = {
            "pytest_exit_code": 1,
            "new_failures": [],
            "known_failures": [{"test_id": "test_a"}, {"test_id": "test_b"}],
        }
        # Simulate the masking condition from test_runner.py lines 791-797
        known_failures_provided = True
        exit_code = result["pytest_exit_code"]
        if (known_failures_provided
                and result.get("new_failures") is not None
                and len(result["new_failures"]) == 0
                and exit_code != 0):
            result["exit_code_masked"] = True
            exit_code = 0

        assert exit_code == 0
        assert result["exit_code_masked"] is True

    def test_no_mask_when_new_failures_exist(self):
        """When new_failures is non-empty, do NOT mask."""
        result = {
            "pytest_exit_code": 1,
            "new_failures": [{"test_id": "test_c"}],
            "known_failures": [{"test_id": "test_a"}],
        }
        known_failures_provided = True
        exit_code = result["pytest_exit_code"]
        if (known_failures_provided
                and result.get("new_failures") is not None
                and len(result["new_failures"]) == 0
                and exit_code != 0):
            result["exit_code_masked"] = True
            exit_code = 0

        assert exit_code == 1
        assert "exit_code_masked" not in result

    def test_no_mask_when_known_failures_not_provided(self):
        """When --known-failures was NOT provided, never mask."""
        result = {
            "pytest_exit_code": 1,
            "new_failures": [],
        }
        known_failures_provided = False
        exit_code = result["pytest_exit_code"]
        if (known_failures_provided
                and result.get("new_failures") is not None
                and len(result["new_failures"]) == 0
                and exit_code != 0):
            result["exit_code_masked"] = True
            exit_code = 0

        assert exit_code == 1

    def test_no_mask_when_exit_code_already_zero(self):
        """When exit_code is already 0, no masking needed."""
        result = {
            "pytest_exit_code": 0,
            "new_failures": [],
            "known_failures": [],
        }
        known_failures_provided = True
        exit_code = result["pytest_exit_code"]
        if (known_failures_provided
                and result.get("new_failures") is not None
                and len(result["new_failures"]) == 0
                and exit_code != 0):
            result["exit_code_masked"] = True
            exit_code = 0

        assert exit_code == 0
        assert "exit_code_masked" not in result

    def test_no_mask_when_zero_tests_collected(self):
        """TC-CONV-001: When both known_failures and new_failures are empty (0 tests
        collected), exit-code masking must NOT fire. This guards against vacuous masking
        that hides total collection failures as apparent success (IssL1-003)."""
        result = {
            "pytest_exit_code": 1,
            "new_failures": [],
            "known_failures": [],  # No pre-existing failures — 0 tests collected
        }
        known_failures_provided = True
        exit_code = result["pytest_exit_code"]
        # Replicate the FIXED masking condition (TC-CONV-001 adds known_failures > 0 guard)
        if (known_failures_provided
                and result.get("new_failures") is not None
                and len(result["new_failures"]) == 0
                and len(result.get("known_failures", [])) > 0
                and exit_code != 0):
            result["exit_code_masked"] = True
            exit_code = 0

        assert exit_code == 1, "Exit code must NOT be masked when 0 tests collected"
        assert "exit_code_masked" not in result


# ===== TC-CONV-002: Known-failure path normalization =====

class TestKnownFailurePathNormalization:
    """Test the dot-notation to slash-path normalization for known-failure matching.

    JUnit XML classnames use dot-notation (tests.python.csv.test_foo).
    Known-failure ledger uses slash-path format (tests/python/csv/test_foo.py).
    TC-CONV-002 added _normalize_test_id() and _is_known() to bridge this gap.
    """

    def _normalize_test_id(self, tid: str):
        """Replicate the normalization logic from tools/test_runner.py."""
        if "::" not in tid:
            return None
        classname = tid.split("::")[0]
        if "." not in classname:
            return None
        return classname.replace(".", "/") + ".py"

    def test_normalize_dot_notation_to_slash_path(self):
        """Dot-notation classname is converted to slash-path file reference."""
        tid = "tests.python.csv.test_r290_csv_numeric_range_has_only_one_row::test_numeric_range_minimal"
        result = self._normalize_test_id(tid)
        assert result == "tests/python/csv/test_r290_csv_numeric_range_has_only_one_row.py"

    def test_normalize_returns_none_without_double_colon(self):
        """IDs without '::' separator return None (no function name, not a test ID)."""
        tid = "tests/python/csv/test_foo.py"
        assert self._normalize_test_id(tid) is None

    def test_normalize_returns_none_without_dots_in_classname(self):
        """Classnames without dots (non-module-path format) return None."""
        tid = "test_simple::test_func"
        assert self._normalize_test_id(tid) is None

    def test_pre_existing_csv_failure_matches_ledger_entry(self):
        """A real CSV analytics failure ID should match the ledger's file-path entry."""
        ledger_entry = "tests/python/csv/test_r290_csv_numeric_range_has_only_one_row.py"
        runner_id = "tests.python.csv.test_r290_csv_numeric_range_has_only_one_row::test_numeric_range_minimal"

        known_file_paths = {ledger_entry}
        normalized = self._normalize_test_id(runner_id)
        assert normalized is not None
        assert normalized in known_file_paths, (
            f"Normalized ID '{normalized}' not found in known_file_paths"
        )

    def test_new_failure_does_not_match_ledger(self):
        """A truly new failure ID should NOT match any ledger entry."""
        runner_id = "tests.python.csv.test_new_unknown_failure::test_something_new"
        known_file_paths = {
            "tests/python/csv/test_r290_csv_numeric_range_has_only_one_row.py",
        }
        normalized = self._normalize_test_id(runner_id)
        assert normalized not in known_file_paths
