"""
test_diff_playbook_outputs.py — Tests for diff_playbook_outputs.py (S-F2F-03).

Sprint: S-F2F-03
Scope: diff_playbook_outputs.py — diff_reports() function and CLI.
"""

import importlib.util
import os
import subprocess
import sys
import tempfile

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIFF_TOOL = os.path.join(REPO_ROOT, "tools", "playbook", "diff_playbook_outputs.py")
PYTHONPATH = os.environ.get(
    "PYTHONPATH",
    "C:/Users/prora/AppData/Roaming/Python/Python313/site-packages",
)


def run_tool(args: list[str]) -> tuple[int, str, str]:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    if "PYTHONPATH" not in env:
        env["PYTHONPATH"] = PYTHONPATH
    result = subprocess.run(
        [sys.executable, DIFF_TOOL] + args,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def load_diff_module():
    spec = importlib.util.spec_from_file_location("diff_playbook_outputs", DIFF_TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_report(playbook_id: str, op_results: list, conflicts: list) -> dict:
    return {
        "playbook_id": playbook_id,
        "format_id": "fods",
        "replay_mode": "dry-run",
        "generated_at": "2026-05-09T00:00:00Z",
        "operation_results": op_results,
        "conflicts": conflicts,
    }


# ---------------------------------------------------------------------------
# Tool existence
# ---------------------------------------------------------------------------
class TestDiffToolExists:
    def test_diff_tool_exists(self):
        assert os.path.isfile(DIFF_TOOL), f"Diff tool must exist: {DIFF_TOOL}"


# ---------------------------------------------------------------------------
# diff_reports unit tests
# ---------------------------------------------------------------------------
class TestDiffReports:
    def setup_method(self):
        self.mod = load_diff_module()

    def test_identical_reports_produce_unchanged(self):
        op_results = [{"operation_id": "op-1", "gate": 1, "status": "PASS", "conflict_count": 0}]
        report = make_report("fods-test", op_results, [])
        result = self.mod.diff_reports(report, report)
        assert result["overall_diff"] == "UNCHANGED"
        assert result["regression_count"] == 0
        assert result["improvement_count"] == 0

    def test_regression_detected(self):
        """A PASS → CONFLICT change is a regression."""
        baseline = make_report("fods-test", [
            {"operation_id": "op-1", "gate": 1, "status": "PASS", "conflict_count": 0}
        ], [])
        current = make_report("fods-test", [
            {"operation_id": "op-1", "gate": 1, "status": "CONFLICT", "conflict_count": 1}
        ], [{"operation_id": "op-1", "gate": 1, "target_path": "some/path",
             "issue_type": "missing_input", "severity": "high"}])
        result = self.mod.diff_reports(baseline, current)
        assert result["overall_diff"] == "REGRESSION"
        assert result["regression_count"] >= 1

    def test_improvement_detected(self):
        """A CONFLICT → PASS change is an improvement."""
        baseline = make_report("fods-test", [
            {"operation_id": "op-1", "gate": 1, "status": "CONFLICT", "conflict_count": 1}
        ], [{"operation_id": "op-1", "gate": 1, "target_path": "some/path",
             "issue_type": "missing_input", "severity": "high"}])
        current = make_report("fods-test", [
            {"operation_id": "op-1", "gate": 1, "status": "PASS", "conflict_count": 0}
        ], [])
        result = self.mod.diff_reports(baseline, current)
        assert result["overall_diff"] == "IMPROVEMENT"
        assert result["improvement_count"] >= 1

    def test_new_operation_detected(self):
        baseline = make_report("fods-test", [], [])
        current = make_report("fods-test", [
            {"operation_id": "op-new", "gate": 2, "status": "PASS", "conflict_count": 0}
        ], [])
        result = self.mod.diff_reports(baseline, current)
        op_diffs = {d["operation_id"]: d for d in result["operation_diffs"]}
        assert op_diffs["op-new"]["change"] == "added_in_current"

    def test_removed_operation_detected(self):
        baseline = make_report("fods-test", [
            {"operation_id": "op-removed", "gate": 2, "status": "PASS", "conflict_count": 0}
        ], [])
        current = make_report("fods-test", [], [])
        result = self.mod.diff_reports(baseline, current)
        op_diffs = {d["operation_id"]: d for d in result["operation_diffs"]}
        assert op_diffs["op-removed"]["change"] == "removed_in_current"

    def test_new_conflict_in_current_detected(self):
        baseline = make_report("fods-test", [
            {"operation_id": "op-1", "gate": 1, "status": "PASS", "conflict_count": 0}
        ], [])
        current = make_report("fods-test", [
            {"operation_id": "op-1", "gate": 1, "status": "CONFLICT", "conflict_count": 1}
        ], [{"operation_id": "op-1", "gate": 1, "target_path": "new/path",
             "issue_type": "missing_input", "severity": "medium"}])
        result = self.mod.diff_reports(baseline, current)
        new_conflicts = [
            d for d in result["conflict_diffs"] if d["change"] == "new_conflict_in_current"
        ]
        assert len(new_conflicts) == 1

    def test_authority_note_present(self):
        report = make_report("fods-test", [], [])
        result = self.mod.diff_reports(report, report)
        assert "INFORMATIONAL" in result.get("authority", "")


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------
class TestDiffCLI:
    def _write_report(self, tmpdir: str, name: str, report: dict) -> str:
        path = os.path.join(tmpdir, name)
        with open(path, "w") as f:
            yaml.dump(report, f)
        return path

    def test_identical_reports_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report = make_report("fods-test", [
                {"operation_id": "op-1", "gate": 1, "status": "PASS", "conflict_count": 0}
            ], [])
            baseline = self._write_report(tmpdir, "baseline.yaml", report)
            current = self._write_report(tmpdir, "current.yaml", report)

            rc, stdout, stderr = run_tool(["--baseline", baseline, "--current", current])
            assert rc == 0
            assert "UNCHANGED" in stdout

    def test_regression_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_report = make_report("fods-test", [
                {"operation_id": "op-1", "gate": 1, "status": "PASS", "conflict_count": 0}
            ], [])
            current_report = make_report("fods-test", [
                {"operation_id": "op-1", "gate": 1, "status": "CONFLICT", "conflict_count": 1}
            ], [{"operation_id": "op-1", "gate": 1, "target_path": "path",
                 "issue_type": "missing_input", "severity": "high"}])
            baseline = self._write_report(tmpdir, "baseline.yaml", baseline_report)
            current = self._write_report(tmpdir, "current.yaml", current_report)

            rc, stdout, stderr = run_tool(["--baseline", baseline, "--current", current])
            assert rc != 0
            assert "REGRESSION" in stdout

    def test_output_file_written_when_specified(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report = make_report("fods-test", [], [])
            baseline = self._write_report(tmpdir, "baseline.yaml", report)
            current = self._write_report(tmpdir, "current.yaml", report)
            output = os.path.join(tmpdir, "diff.yaml")

            run_tool(["--baseline", baseline, "--current", current, "--output", output])
            assert os.path.isfile(output)
            with open(output) as f:
                diff = yaml.safe_load(f)
            assert "overall_diff" in diff

    def test_output_rejects_repo_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            report = make_report("fods-test", [], [])
            baseline = self._write_report(tmpdir, "baseline.yaml", report)
            current = self._write_report(tmpdir, "current.yaml", report)
            bad_output = os.path.join(REPO_ROOT, "tools", "playbook", "bad-diff.yaml")

            rc, stdout, stderr = run_tool([
                "--baseline", baseline,
                "--current", current,
                "--output", bad_output,
            ])
            assert rc != 0
