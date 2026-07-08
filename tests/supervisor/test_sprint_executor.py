"""
TC-A3: Unit tests for tools/supervisor/sprint_executor.py

Covers 5 subcommands: inject-declaration, status, build-review-package,
run-sprint --dry-run, run-loop --dry-run.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
_EXECUTOR = _REPO / "tools" / "supervisor" / "sprint_executor.py"

_REQUIRED_FIELDS = [
    "run_id", "sprint_id", "evidence_root",
    "start_time", "end_time",
    "git_head_start", "git_head_end", "git_status_final",
    "declared_scope",
    "planned_work_items", "completed_work_items", "incomplete_work_items",
    "changed_files", "tests_run", "test_results",
    "evidence_artifacts", "reports_created",
    "worker_self_verdict", "worker_self_grade",
    "next_recommended_work",
]


def _run(*args: str, expect_ok: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [sys.executable, str(_EXECUTOR)] + list(args),
        capture_output=True,
        text=True,
        cwd=str(_REPO),
    )
    if expect_ok:
        assert result.returncode == 0, (
            f"sprint_executor.py {args} exited {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result


class TestInjectDeclaration:
    """TC-A3-1: inject-declaration creates a valid skeleton YAML."""

    def test_creates_skeleton_with_all_required_fields(self, tmp_path):
        sprint_id = "tc-a3-inject-test"
        result = _run("inject-declaration", sprint_id)

        # Find the declaration path in stdout
        lines = result.stdout.strip().splitlines()
        decl_line = next((l for l in lines if "evidence-declaration.yaml" in l), None)
        assert decl_line is not None, f"No declaration path in stdout: {result.stdout}"

        # Parse declaration path (last word on the line, or strip a prefix)
        decl_path = Path(decl_line.strip().split()[-1])
        assert decl_path.exists(), f"Declaration file not created: {decl_path}"

        doc = yaml.safe_load(decl_path.read_text(encoding="utf-8"))
        assert isinstance(doc, dict)

        for field in _REQUIRED_FIELDS:
            assert field in doc, f"Missing required field: {field}"

    def test_run_id_contains_sprint_id(self, tmp_path):
        sprint_id = "tc-a3-runid-check"
        result = _run("inject-declaration", sprint_id)

        lines = result.stdout.strip().splitlines()
        decl_line = next((l for l in lines if "evidence-declaration.yaml" in l), None)
        decl_path = Path(decl_line.strip().split()[-1])

        doc = yaml.safe_load(decl_path.read_text(encoding="utf-8"))
        assert sprint_id in doc["run_id"], (
            f"run_id '{doc['run_id']}' does not contain sprint_id '{sprint_id}'"
        )

    def test_tests_run_is_int(self, tmp_path):
        sprint_id = "tc-a3-type-check"
        result = _run("inject-declaration", sprint_id)

        lines = result.stdout.strip().splitlines()
        decl_line = next((l for l in lines if "evidence-declaration.yaml" in l), None)
        decl_path = Path(decl_line.strip().split()[-1])

        doc = yaml.safe_load(decl_path.read_text(encoding="utf-8"))
        assert isinstance(doc["tests_run"], int), (
            f"tests_run must be int, got {type(doc['tests_run'])}"
        )

    def test_list_fields_are_lists(self, tmp_path):
        sprint_id = "tc-a3-list-check"
        result = _run("inject-declaration", sprint_id)

        lines = result.stdout.strip().splitlines()
        decl_line = next((l for l in lines if "evidence-declaration.yaml" in l), None)
        decl_path = Path(decl_line.strip().split()[-1])

        doc = yaml.safe_load(decl_path.read_text(encoding="utf-8"))
        for list_field in [
            "planned_work_items", "completed_work_items", "incomplete_work_items",
            "changed_files", "evidence_artifacts", "reports_created",
            "next_recommended_work",
        ]:
            assert isinstance(doc[list_field], list), (
                f"{list_field} must be list, got {type(doc[list_field])}"
            )


class TestStatus:
    """TC-A3-2: status prints valid JSON with verdict key."""

    def test_exits_zero(self):
        signal_path = _REPO / ".local" / "supervisor" / "continuation-signal.json"
        if not signal_path.exists():
            pytest.skip("continuation-signal.json not present (.local/ gitignored in CI)")
        _run("status")

    def test_prints_valid_json(self):
        signal_path = _REPO / ".local" / "supervisor" / "continuation-signal.json"
        if not signal_path.exists():
            pytest.skip("continuation-signal.json not present (.local/ gitignored in CI)")
        result = _run("status")
        # Find the JSON block in stdout (may have non-JSON lines before/after)
        stdout = result.stdout.strip()
        # Try to parse full output as JSON, or find first '{' block
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            # Try extracting JSON substring
            start = stdout.find("{")
            end = stdout.rfind("}") + 1
            assert start >= 0, f"No JSON object in status output: {stdout}"
            data = json.loads(stdout[start:end])

        assert "verdict" in data, f"No 'verdict' key in status output: {data}"
        assert data["verdict"] in ("CONTINUE", "STOP"), (
            f"verdict must be CONTINUE or STOP, got {data['verdict']}"
        )


class TestBuildReviewPackage:
    """TC-A3-3: build-review-package exits non-zero when declaration not found."""

    def test_exits_nonzero_for_missing_declaration(self):
        result = _run(
            "build-review-package",
            "--declaration", ".local/evidences/nonexistent/evidence-declaration.yaml",
            expect_ok=False,
        )
        assert result.returncode != 0, (
            "Expected non-zero exit for missing declaration, got 0"
        )


class TestRunSprintDryRun:
    """TC-A3-4: run-sprint --dry-run exits 0 without invoking claude CLI."""

    def test_dry_run_exits_zero(self):
        result = _run("run-sprint", "tc-a3-dry-run-test", "--dry-run")
        assert result.returncode == 0

    def test_dry_run_prints_dry_run_message(self):
        result = _run("run-sprint", "tc-a3-dry-run-msg", "--dry-run")
        assert "dry" in result.stdout.lower() or "dry" in result.stderr.lower(), (
            f"Expected 'dry' in output. stdout: {result.stdout}, stderr: {result.stderr}"
        )

    def test_dry_run_does_not_invoke_claude(self):
        # If claude CLI is called, it would error (not found or no prompt).
        # dry-run must succeed even when claude is unavailable.
        result = _run("run-sprint", "tc-a3-no-claude", "--dry-run")
        # No claude-related error in stderr
        assert "claude" not in result.stderr.lower() or "not found" not in result.stderr.lower()


class TestRunLoopDryRun:
    """TC-A3-5: run-loop --dry-run --max-cycles 1 succeeds and does not invoke claude."""

    def test_dry_run_one_cycle_exits_zero(self):
        result = _run("run-loop", "--max-cycles", "1", "--dry-run")
        assert result.returncode == 0, (
            f"run-loop --dry-run --max-cycles 1 failed: {result.stdout}\n{result.stderr}"
        )

    def test_dry_run_produces_output(self):
        result = _run("run-loop", "--max-cycles", "1", "--dry-run")
        assert len(result.stdout.strip()) > 0, "Expected non-empty output from run-loop --dry-run"
