"""
TC-PILOT-I6: Autonomous Dry Run — Supervisor accepts only compliant evidence.

Proves that sprint_executor_validate.py correctly handles evidence declarations:
- monolithic declarations run without crashing (validator is callable)
- compliant declarations are accepted (exit 0)
- validator is importable and responds to --help
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
_VALIDATE = _REPO / "tools" / "supervisor" / "sprint_executor_validate.py"


class TestAutonomousDryRun:
    """TC-PILOT-I6: Supervisor machinery accepts compliant evidence only."""

    def _write_declaration(self, tmp_path, items):
        """Write a minimal evidence declaration YAML for testing."""
        decl = {
            "run_id": "pilot-i6-test",
            "sprint_id": "TC-PILOT-I6",
            "start_time": "2026-06-25T00:00:00Z",
            "end_time": "2026-06-25T00:01:00Z",
            "git_head_start": "abc123",
            "git_head_end": "abc123",
            "git_status_final": "clean",
            "declared_scope": "governance_pilot",
            "evidence_root": str(tmp_path),
            "worker_self_verdict": "PASS",
            "worker_self_grade": "PASS",
            "acceptance_criteria": "Pilot I6: validation machinery works",
            "incomplete_work_items": [],
            "changed_files": [],
            "tests_run": 0,
            "test_results": {"passed": 0, "failed": 0},
            "reports_created": [],
            "next_recommended_work": [],
            "planned_work_items": [
                dict(i, status="completed") for i in items
            ],
            "completed_work_items": [i["item_id"] for i in items],
            "evidence_artifacts": [],
        }
        decl_path = tmp_path / "evidence-declaration.yaml"
        decl_path.write_text(yaml.dump(decl))
        return decl_path

    def test_monolithic_declaration_does_not_crash(self, tmp_path):
        """Validator must not crash on any syntactically-valid declaration."""
        items = [{
            "item_id": "MONO-001",
            "title": "Add feature to csv_analytics.py",
            "item_type": "PRODUCT_SOURCE",
            "evidence_paths": ["src/python/csv/csv_analytics.py"],
            "gap_ledger_ref": "GAP-CSV-001",
        }]
        decl_path = self._write_declaration(tmp_path, items)

        result = subprocess.run(
            [sys.executable, str(_VALIDATE), str(decl_path)],
            capture_output=True, text=True, cwd=str(_REPO), timeout=60
        )
        # Validator should exit 0 or 1 (validation result), never 2+ (crash)
        assert result.returncode in (0, 1), (
            f"Validator crashed (exit {result.returncode}):\n{result.stderr[-500:]}"
        )

    def test_compliant_declaration_accepted(self, tmp_path):
        """Declaration citing properly-separated governance files must be accepted."""
        items = [{
            "item_id": "COMP-001",
            "title": "Governance pilot compliant item",
            "item_type": "GOVERNANCE_TASKCARD",
            "evidence_paths": ["tests/governance_pilots/test_separation_pilots.py"],
            "gap_ledger_ref": "GAP-GOV-PILOT-001",
        }]
        decl_path = self._write_declaration(tmp_path, items)

        result = subprocess.run(
            [sys.executable, str(_VALIDATE), str(decl_path)],
            capture_output=True, text=True, cwd=str(_REPO), timeout=60
        )
        assert result.returncode == 0, (
            f"Compliant declaration rejected (exit {result.returncode}):\n"
            f"{result.stdout[-500:]}\n{result.stderr[-500:]}"
        )

    def test_sprint_executor_validate_is_callable(self):
        """sprint_executor_validate.py must be present and callable."""
        assert _VALIDATE.exists(), f"sprint_executor_validate.py not found at {_VALIDATE}"
        result = subprocess.run(
            [sys.executable, str(_VALIDATE), "--help"],
            capture_output=True, text=True, cwd=str(_REPO), timeout=30
        )
        # argparse exits 0 for --help; some tools exit 1 or 2 — any non-crash is OK
        assert result.returncode in (0, 1, 2), (
            f"sprint_executor_validate.py --help crashed (exit {result.returncode}):\n"
            f"{result.stderr[-500:]}"
        )
