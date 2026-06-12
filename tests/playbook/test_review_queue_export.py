"""
test_review_queue_export.py — Tests for export_review_queue.py (S-F2F-03).

Sprint: S-F2F-03
Scope: export_review_queue.py — build_review_queue() function and CLI.
"""

import os
import subprocess
import sys
import tempfile

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXPORT_TOOL = os.path.join(REPO_ROOT, "tools", "playbook", "export_review_queue.py")
REPLAY_TOOL = os.path.join(REPO_ROOT, "tools", "playbook", "replay_acquisition_playbook.py")
VALID_FIXTURE = os.path.join(
    REPO_ROOT, "tests", "playbook", "fixtures", "replay-valid-acquisition-playbook.yaml"
)
MISSING_INPUT_FIXTURE = os.path.join(
    REPO_ROOT, "tests", "playbook", "fixtures", "replay-with-missing-inputs.yaml"
)
SCHEMA = os.path.join(REPO_ROOT, "schemas", "playbook", "acquisition-playbook.schema.json")
REVIEW_QUEUE_SCHEMA = os.path.join(
    REPO_ROOT, "schemas", "playbook", "review-queue.schema.json"
)
PYTHONPATH = os.environ.get(
    "PYTHONPATH",
    "C:/Users/prora/AppData/Roaming/Python/Python313/site-packages",
)


def run_tool(script: str, args: list[str]) -> tuple[int, str, str]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    if "PYTHONPATH" not in env:
        env["PYTHONPATH"] = PYTHONPATH
    result = subprocess.run(
        [sys.executable, script] + args,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def make_dry_run_report(fixture_path: str, output_dir: str) -> str:
    """Generate a dry-run report YAML from a fixture and return its path."""
    report_path = os.path.join(output_dir, "dry-run-report.yaml")
    # We need the dry-run report — generate it via export-review-queue
    # (which internally calls dry-run). Actually, let's produce it by
    # calling the replay tool's dry-run and capturing the output as YAML.
    # Since dry-run prints to stdout (not YAML), we use build_review_queue directly.
    # For testing purposes, construct a minimal valid report dict.
    return report_path


# ---------------------------------------------------------------------------
# Tool existence
# ---------------------------------------------------------------------------
class TestExportToolExists:
    def test_export_tool_exists(self):
        assert os.path.isfile(EXPORT_TOOL), f"Export tool must exist: {EXPORT_TOOL}"

    def test_review_queue_schema_exists(self):
        assert os.path.isfile(REVIEW_QUEUE_SCHEMA), (
            f"Review queue schema must exist: {REVIEW_QUEUE_SCHEMA}"
        )


# ---------------------------------------------------------------------------
# build_review_queue unit tests (import the function directly)
# ---------------------------------------------------------------------------
class TestBuildReviewQueue:
    def _import_build_review_queue(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("export_review_queue", EXPORT_TOOL)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.build_review_queue

    def test_empty_conflicts_produces_valid_empty_queue(self):
        build_rq = self._import_build_review_queue()
        report = {
            "playbook_id": "fods-test",
            "format_id": "fods",
            "conflicts": [],
        }
        queue = build_rq("fods", report)
        assert queue["schema_version"] == "1.0"
        assert queue["source_format_id"] == "fods"
        assert queue["summary"]["total_items"] == 0
        assert queue["summary"]["open_items"] == 0
        assert queue["summary"]["blocks_apply_mode"] is False
        assert queue["governance"]["cannot_approve_gates"] is True
        assert queue["governance"]["high_severity_blocks_apply"] is True
        assert queue["items"] == []

    def test_high_severity_conflict_blocks_apply(self):
        build_rq = self._import_build_review_queue()
        report = {
            "playbook_id": "fods-test",
            "format_id": "fods",
            "conflicts": [
                {
                    "operation_id": "test-op",
                    "gate": 1,
                    "target_path": "some/path.yaml",
                    "issue_type": "missing_input",
                    "severity": "high",
                    "deterministic_failure_reason": "Required file is absent",
                    "required_action": "Verify the file exists",
                }
            ],
        }
        queue = build_rq("fods", report)
        assert queue["summary"]["total_items"] == 1
        assert queue["summary"]["high_count"] == 1
        assert queue["summary"]["blocks_apply_mode"] is True
        item = queue["items"][0]
        assert item["blocks_apply_mode"] is True
        assert item["severity"] == "high"

    def test_blocker_severity_conflict_blocks_apply(self):
        build_rq = self._import_build_review_queue()
        report = {
            "playbook_id": "fods-test",
            "format_id": "fods",
            "conflicts": [
                {
                    "operation_id": "test-op",
                    "gate": 2,
                    "target_path": "some/path.yaml",
                    "issue_type": "policy_violation",
                    "severity": "blocker",
                    "deterministic_failure_reason": "Policy violation detected",
                    "required_action": "Human review required",
                }
            ],
        }
        queue = build_rq("fods", report)
        assert queue["summary"]["blocker_count"] == 1
        assert queue["summary"]["blocks_apply_mode"] is True

    def test_medium_severity_does_not_block_apply(self):
        build_rq = self._import_build_review_queue()
        report = {
            "playbook_id": "fods-test",
            "format_id": "fods",
            "conflicts": [
                {
                    "operation_id": "test-op",
                    "gate": 1,
                    "target_path": "some/output.yaml",
                    "issue_type": "target_mismatch",
                    "severity": "medium",
                    "deterministic_failure_reason": "Output absent",
                    "required_action": "Check if output should exist",
                }
            ],
        }
        queue = build_rq("fods", report)
        item = queue["items"][0]
        assert item["blocks_apply_mode"] is False
        assert queue["summary"]["medium_count"] == 1

    def test_queue_id_format(self):
        """Queue ID must start with 'rq-{format_id}-'."""
        build_rq = self._import_build_review_queue()
        report = {"playbook_id": "fods-test", "format_id": "fods", "conflicts": []}
        queue = build_rq("fods", report)
        assert queue["queue_id"].startswith("rq-fods-"), (
            f"queue_id must start with 'rq-fods-'. Got: {queue['queue_id']}"
        )

    def test_item_ids_sequential(self):
        """Item IDs must follow RQ-001, RQ-002, ... pattern."""
        build_rq = self._import_build_review_queue()
        conflicts = [
            {
                "operation_id": f"op-{i}",
                "gate": 1,
                "target_path": f"path/{i}.yaml",
                "issue_type": "missing_input",
                "severity": "high",
                "deterministic_failure_reason": f"Reason {i}",
                "required_action": f"Action {i}",
            }
            for i in range(3)
        ]
        report = {"playbook_id": "fods-test", "format_id": "fods", "conflicts": conflicts}
        queue = build_rq("fods", report)
        ids = [item["item_id"] for item in queue["items"]]
        assert ids == ["RQ-001", "RQ-002", "RQ-003"]

    def test_governance_block_always_correct(self):
        """Governance block must always have all required true values."""
        build_rq = self._import_build_review_queue()
        report = {"playbook_id": "fods-test", "format_id": "fods", "conflicts": []}
        queue = build_rq("fods", report)
        gov = queue["governance"]
        assert gov["cannot_approve_gates"] is True
        assert gov["cannot_replace_dec034"] is True
        assert gov["cannot_replace_evidence_contracts"] is True
        assert gov["cannot_replace_human_approval"] is True
        assert gov["high_severity_blocks_apply"] is True
        assert gov["gate_progress_requires_resolution"] is True


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------
class TestExportQueueCLI:
    def _make_dry_run_report(self) -> dict:
        """Produce a minimal valid dry-run report dict for testing."""
        return {
            "playbook_id": "fods-test-missing-inputs-fixture",
            "format_id": "fods",
            "replay_mode": "dry-run",
            "generated_at": "2026-05-09T00:00:00Z",
            "conflicts": [
                {
                    "operation_id": "test-missing-input-op",
                    "gate": 3,
                    "target_path": "this/path/does/not/exist/input.yaml",
                    "issue_type": "missing_input",
                    "severity": "high",
                    "deterministic_failure_reason": "Required input is absent",
                    "required_action": "Verify the file exists",
                }
            ],
        }

    def test_export_from_report_produces_valid_queue(self):
        """export_review_queue.py CLI produces a valid queue from a report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = os.path.join(tmpdir, "dry-run-report.yaml")
            queue_path = os.path.join(tmpdir, "queue.yaml")
            report = self._make_dry_run_report()
            with open(report_path, "w") as f:
                yaml.dump(report, f)

            rc, stdout, stderr = run_tool(EXPORT_TOOL, [
                "--format-id", "fods",
                "--dry-run-report", report_path,
                "--output", queue_path,
            ])
            assert rc != 0  # conflicts → non-zero
            assert "CONFLICTS" in stdout
            assert os.path.isfile(queue_path)

            with open(queue_path) as f:
                queue = yaml.safe_load(f)

            assert queue["summary"]["total_items"] == 1
            assert queue["governance"]["cannot_approve_gates"] is True

    def test_export_rejects_repo_output_path(self):
        """export_review_queue.py rejects --output inside committed repo dirs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = os.path.join(tmpdir, "report.yaml")
            report = self._make_dry_run_report()
            with open(report_path, "w") as f:
                yaml.dump(report, f)

            bad_output = os.path.join(REPO_ROOT, "tools", "playbook", "bad-output.yaml")
            rc, stdout, stderr = run_tool(EXPORT_TOOL, [
                "--format-id", "fods",
                "--dry-run-report", report_path,
                "--output", bad_output,
            ])
            assert rc != 0
            assert "EXPORT_ERROR" in stderr or "committed repo" in stderr

    def test_export_empty_conflicts_exits_zero(self):
        """export_review_queue.py exits 0 for an empty conflict list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = os.path.join(tmpdir, "report.yaml")
            queue_path = os.path.join(tmpdir, "queue.yaml")
            report = {
                "playbook_id": "fods-test",
                "format_id": "fods",
                "conflicts": [],
            }
            with open(report_path, "w") as f:
                yaml.dump(report, f)

            rc, stdout, stderr = run_tool(EXPORT_TOOL, [
                "--format-id", "fods",
                "--dry-run-report", report_path,
                "--output", queue_path,
            ])
            assert rc == 0
            assert "PASS" in stdout
