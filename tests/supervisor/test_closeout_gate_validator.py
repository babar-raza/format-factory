"""Tests for the closeout gate validator.

Verifies that sprint closeout is enforced by executable code, not docs.
"""

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from validate_closeout_gate import (
    check_declaration_exists,
    check_package_exists,
    check_raw_logs_exist,
    check_lane_ledger_exists,
    check_state_ledger_exists,
    check_no_rework_remaining,
    check_no_runnable_next_action,
    check_accepted_not_with_rework_final,
    check_prompt_rework_consistency,
    run_closeout_gate,
)


@pytest.fixture
def evidence_root(tmp_path):
    """Create a minimal valid evidence root."""
    root = tmp_path / ".local" / "evidences" / "test-run"
    root.mkdir(parents=True)
    # Create required files
    (root / "evidence-declaration.yaml").write_text("run_id: test\n")
    (root / "raw-logs").mkdir()
    (root / "raw-logs" / "test.log").write_text("1 passed\n")
    (root / "lane-ledger.yaml").write_text("lanes: []\n")
    (root / "state-ledger.yaml").write_text("state: {}\n")
    # Create review dir
    review_dir = tmp_path / ".local" / "supervisor" / "reviews" / "test-run"
    review_dir.mkdir(parents=True)
    (review_dir / "declaration-review-package.zip").write_bytes(b"PK")
    # Create continuation signal with no rework
    sig_dir = tmp_path / ".local" / "supervisor"
    sig_dir.mkdir(parents=True, exist_ok=True)
    (sig_dir / "continuation-signal.json").write_text(json.dumps({
        "autonomous_continue": False,
        "rework_items": [],
        "safe_lanes_available": False,
    }))
    # Create next-action as health check
    (sig_dir / "next-action.json").write_text(json.dumps({
        "action_type": "QUEUE_HEALTH_CHECK",
    }))
    # Create CLAUDE.md as repo root marker
    (tmp_path / "CLAUDE.md").write_text("marker\n")
    return root


class TestDeclarationExists:
    def test_pass_when_present(self, evidence_root):
        result = check_declaration_exists(evidence_root)
        assert result["passed"] is True

    def test_fail_when_missing(self, tmp_path):
        root = tmp_path / "empty"
        root.mkdir()
        result = check_declaration_exists(root)
        assert result["passed"] is False


class TestPackageExists:
    def test_pass_when_present(self, evidence_root):
        result = check_package_exists(evidence_root)
        assert result["passed"] is True

    def test_fail_when_missing(self, tmp_path):
        root = tmp_path / ".local" / "evidences" / "no-pkg"
        root.mkdir(parents=True)
        (tmp_path / "CLAUDE.md").write_text("x")
        result = check_package_exists(root)
        assert result["passed"] is False


class TestRawLogsExist:
    def test_pass_with_logs(self, evidence_root):
        result = check_raw_logs_exist(evidence_root)
        assert result["passed"] is True

    def test_fail_empty_dir(self, tmp_path):
        root = tmp_path / "no-logs"
        root.mkdir()
        (root / "raw-logs").mkdir()
        result = check_raw_logs_exist(root)
        assert result["passed"] is False

    def test_fail_no_dir(self, tmp_path):
        root = tmp_path / "no-logs-dir"
        root.mkdir()
        result = check_raw_logs_exist(root)
        assert result["passed"] is False


class TestLaneLedgerExists:
    def test_pass(self, evidence_root):
        result = check_lane_ledger_exists(evidence_root)
        assert result["passed"] is True

    def test_fail(self, tmp_path):
        root = tmp_path / "no-ledger"
        root.mkdir()
        result = check_lane_ledger_exists(root)
        assert result["passed"] is False


class TestStateLedgerExists:
    def test_pass(self, evidence_root):
        result = check_state_ledger_exists(evidence_root)
        assert result["passed"] is True

    def test_fail(self, tmp_path):
        root = tmp_path / "no-ledger"
        root.mkdir()
        result = check_state_ledger_exists(root)
        assert result["passed"] is False


class TestNoReworkRemaining:
    def test_pass_no_rework(self, evidence_root):
        result = check_no_rework_remaining(evidence_root)
        assert result["passed"] is True

    def test_fail_rework_present(self, evidence_root):
        repo_root = evidence_root.parent.parent.parent
        sig = repo_root / ".local" / "supervisor" / "continuation-signal.json"
        sig.write_text(json.dumps({
            "autonomous_continue": "true_with_rework",
            "rework_items": ["RCHE-002"],
        }))
        result = check_no_rework_remaining(evidence_root)
        assert result["passed"] is False
        assert "RCHE-002" in result["rework_items"]


class TestNoRunnableNextAction:
    def test_pass_health_check(self, evidence_root):
        result = check_no_runnable_next_action(evidence_root)
        assert result["passed"] is True

    def test_fail_executable_action(self, evidence_root):
        repo_root = evidence_root.parent.parent.parent
        action = repo_root / ".local" / "supervisor" / "next-action.json"
        action.write_text(json.dumps({
            "action_type": "PRODUCT_SOURCE_PATCH_BOUNDED",
        }))
        result = check_no_runnable_next_action(evidence_root)
        assert result["passed"] is False


class TestAcceptedNotWithReworkFinal:
    def test_pass_no_rework_grades(self, evidence_root):
        result = check_accepted_not_with_rework_final(evidence_root)
        assert result["passed"] is True

    def test_fail_rework_in_grades(self, evidence_root):
        repo_root = evidence_root.parent.parent.parent
        review_dir = repo_root / ".local" / "supervisor" / "reviews" / "test-run"
        review_dir.mkdir(parents=True, exist_ok=True)
        (review_dir / "item-grades.json").write_text(json.dumps([
            {"item_id": "X-001", "grade": "ACCEPTED"},
            {"item_id": "X-002", "grade": "REWORK_REQUIRED"},
        ]))
        result = check_accepted_not_with_rework_final(evidence_root)
        assert result["passed"] is False


class TestPromptReworkConsistency:
    def test_pass_consistent(self, evidence_root):
        result = check_prompt_rework_consistency(evidence_root)
        assert result["passed"] is True

    def test_fail_contradiction(self, evidence_root):
        repo_root = evidence_root.parent.parent.parent
        review_dir = repo_root / ".local" / "supervisor" / "reviews" / "test-run"
        review_dir.mkdir(parents=True, exist_ok=True)
        (review_dir / "item-grades.json").write_text(json.dumps([
            {"item_id": "X-002", "grade": "REWORK_REQUIRED"},
        ]))
        sprint_dir = repo_root / "reports" / "supervisor"
        sprint_dir.mkdir(parents=True, exist_ok=True)
        (sprint_dir / "next-sprint.md").write_text("## Rework: None\nDo product work.\n")
        result = check_prompt_rework_consistency(evidence_root)
        assert result["passed"] is False


class TestRunCloseoutGate:
    def test_all_pass(self, evidence_root):
        result = run_closeout_gate(evidence_root)
        assert result["verdict"] == "PASS"
        assert result["failed_count"] == 0

    def test_fail_missing_declaration(self, tmp_path):
        root = tmp_path / ".local" / "evidences" / "bad-run"
        root.mkdir(parents=True)
        (tmp_path / "CLAUDE.md").write_text("x")
        result = run_closeout_gate(root)
        assert result["verdict"] == "FAIL"
        assert result["failed_count"] > 0


class TestCloseoutGateResultKeys:
    """Regression: run_closeout_gate must return the documented key names."""

    def test_result_has_correct_keys(self, tmp_path):
        """Result dict uses passed_count/total_gates/gates, not passed/total/checks."""
        root = tmp_path / ".local" / "evidences" / "key-test"
        root.mkdir(parents=True)
        (tmp_path / "CLAUDE.md").write_text("x")
        result = run_closeout_gate(root)
        assert "passed_count" in result, "Missing key 'passed_count' (was 'passed'?)"
        assert "total_gates" in result, "Missing key 'total_gates' (was 'total'?)"
        assert "gates" in result, "Missing key 'gates' (was 'checks'?)"
        assert "verdict" in result
        assert "failed_count" in result
        # Negative: old keys must not exist
        assert "passed" not in result or result.get("passed") is None
        assert "total" not in result or result.get("total") is None
        assert "checks" not in result or result.get("checks") is None


class TestPackage196Scenario:
    """Reproduce the exact failure state from package 196."""

    def test_package_196_state_blocks(self, tmp_path):
        """The exact state that caused premature stop must be detected."""
        root = tmp_path / ".local" / "evidences" / "test-run"
        root.mkdir(parents=True)
        (root / "evidence-declaration.yaml").write_text("run_id: test\n")
        (root / "raw-logs").mkdir()
        (root / "raw-logs" / "test.log").write_text("22 passed\n")
        # Missing lane and state ledgers
        # Rework present in signal
        (tmp_path / "CLAUDE.md").write_text("x")
        sig_dir = tmp_path / ".local" / "supervisor"
        sig_dir.mkdir(parents=True, exist_ok=True)
        (sig_dir / "continuation-signal.json").write_text(json.dumps({
            "autonomous_continue": "true_with_rework",
            "rework_items": ["RCHE-002"],
            "safe_lanes_available": True,
            "continuation_state": "YES_WITH_REWORK",
        }))
        (sig_dir / "next-action.json").write_text(json.dumps({
            "action_type": "QUEUE_HEALTH_CHECK",
        }))

        result = run_closeout_gate(root)
        assert result["verdict"] == "FAIL"
        failed_gates = [g["gate"] for g in result["gates"] if not g["passed"]]
        assert "lane_ledger_exists" in failed_gates
        assert "state_ledger_exists" in failed_gates
        assert "no_rework_remaining" in failed_gates
