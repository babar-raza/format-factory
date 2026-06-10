"""Tests for evidence_auto_packager.py.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-3-001
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from tools.supervisor.evidence_auto_packager import pack, _aggregate_tests, _collect_changed_files


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_LEDGER = {
    "schema_version": "1.0",
    "lanes": [
        {
            "lane_id": "LANE-001",
            "sprint_id": "TEST-SPRINT-001",
            "status": "completed",
            "files_changed": ["src/python/abw/abw_codec.py", "tests/python/abw/test_foo.py"],
            "test_count": 12,
            "tests_passed": 12,
            "tests_failed": 0,
            "evidence_artifacts": [
                {"path": ".local/evidences/test/raw-logs/lane1.log", "type": "raw_log", "description": "lane 1 log"}
            ],
        },
        {
            "lane_id": "LANE-002",
            "sprint_id": "TEST-SPRINT-001",
            "status": "completed",
            "files_changed": ["src/python/gnumeric/gnumeric_codec.py"],
            "test_count": 8,
            "tests_passed": 8,
            "tests_failed": 0,
            "evidence_artifacts": [],
        },
    ],
}

SAMPLE_WORK_ITEMS = [
    {
        "item_id": "W1-FOO",
        "title": "Implement foo()",
        "status": "completed",
        "grade": "PASS",
        "evidence_paths": ["src/python/abw/abw_codec.py"],
        "test_results": {"passed": 7, "failed": 0, "skipped": 0, "errors": 0},
    },
    {
        "item_id": "W2-BAR",
        "title": "Implement bar()",
        "status": "completed",
        "grade": "PASS",
        "evidence_paths": ["src/python/gnumeric/gnumeric_codec.py"],
        "test_results": {"passed": 5, "failed": 0, "skipped": 0, "errors": 0},
    },
]


# ---------------------------------------------------------------------------
# Unit: _aggregate_tests
# ---------------------------------------------------------------------------

class TestAggregateTests:
    def test_basic_aggregation(self):
        lanes = [
            {"tests_passed": 10, "tests_failed": 0, "test_count": 10},
            {"tests_passed": 5, "tests_failed": 1, "test_count": 6},
        ]
        result = _aggregate_tests(lanes)
        assert result["passed"] == 15
        assert result["failed"] == 1

    def test_empty_lanes(self):
        result = _aggregate_tests([])
        assert result["passed"] == 0
        assert result["failed"] == 0

    def test_skipped_derived_from_total(self):
        lanes = [{"tests_passed": 8, "tests_failed": 0, "test_count": 10}]
        result = _aggregate_tests(lanes)
        assert result["skipped"] == 2

    def test_returns_dict_with_required_keys(self):
        result = _aggregate_tests([])
        assert "passed" in result
        assert "failed" in result
        assert "skipped" in result
        assert "errors" in result


# ---------------------------------------------------------------------------
# Unit: _collect_changed_files
# ---------------------------------------------------------------------------

class TestCollectChangedFiles:
    def test_deduplication(self):
        lanes = [
            {"files_changed": ["a.py", "b.py"]},
            {"files_changed": ["b.py", "c.py"]},
        ]
        result = _collect_changed_files(lanes)
        assert result == ["a.py", "b.py", "c.py"]

    def test_empty_lanes(self):
        assert _collect_changed_files([]) == []

    def test_order_preserved(self):
        lanes = [{"files_changed": ["z.py", "a.py"]}]
        result = _collect_changed_files(lanes)
        assert result == ["z.py", "a.py"]


# ---------------------------------------------------------------------------
# Integration: pack() function
# ---------------------------------------------------------------------------

class TestPack:
    def test_pack_returns_dict(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps(SAMPLE_LEDGER), encoding="utf-8")
        result = pack(
            sprint_id="TEST-SPRINT-001",
            run_id="test-run-001",
            evidence_root=".local/evidences/test-run-001",
            ledger_path=ledger_file,
        )
        assert isinstance(result, dict)

    def test_required_fields_present(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps(SAMPLE_LEDGER), encoding="utf-8")
        result = pack(
            sprint_id="TEST-SPRINT-001",
            run_id="test-run-001",
            evidence_root=".local/evidences/test-run-001",
            ledger_path=ledger_file,
        )
        required = [
            "run_id", "sprint_id", "evidence_root", "start_time", "end_time",
            "git_head_start", "git_head_end", "git_status_final", "declared_scope",
            "planned_work_items", "completed_work_items", "incomplete_work_items",
            "changed_files", "tests_run", "test_results",
            "evidence_artifacts", "reports_created",
            "worker_self_verdict", "worker_self_grade", "next_recommended_work",
        ]
        for field in required:
            assert field in result, f"Missing required field: {field}"

    def test_sprint_id_populated(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps(SAMPLE_LEDGER), encoding="utf-8")
        result = pack(
            sprint_id="TEST-SPRINT-001",
            run_id="test-run-001",
            evidence_root=".local/evidences/test-run-001",
            ledger_path=ledger_file,
        )
        assert result["sprint_id"] == "TEST-SPRINT-001"
        assert result["run_id"] == "test-run-001"

    def test_test_results_aggregated_from_ledger(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps(SAMPLE_LEDGER), encoding="utf-8")
        result = pack(
            sprint_id="TEST-SPRINT-001",
            run_id="test-run-001",
            evidence_root=".local/evidences/test-run-001",
            ledger_path=ledger_file,
        )
        assert result["test_results"]["passed"] == 20  # 12 + 8
        assert result["test_results"]["failed"] == 0

    def test_changed_files_collected(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps(SAMPLE_LEDGER), encoding="utf-8")
        result = pack(
            sprint_id="TEST-SPRINT-001",
            run_id="test-run-001",
            evidence_root=".local/evidences/test-run-001",
            ledger_path=ledger_file,
        )
        assert "src/python/abw/abw_codec.py" in result["changed_files"]
        assert "src/python/gnumeric/gnumeric_codec.py" in result["changed_files"]

    def test_worker_verdict_placeholder(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps(SAMPLE_LEDGER), encoding="utf-8")
        result = pack(
            sprint_id="TEST-SPRINT-001",
            run_id="test-run-001",
            evidence_root=".local/evidences/test-run-001",
            ledger_path=ledger_file,
        )
        assert result["worker_self_verdict"] == "PENDING_WORKER_FILL"
        assert result["worker_self_grade"] == "PENDING_WORKER_FILL"

    def test_explicit_work_items_used(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps({"schema_version": "1.0", "lanes": []}), encoding="utf-8")
        items_file = tmp_path / "items.json"
        items_file.write_text(json.dumps(SAMPLE_WORK_ITEMS), encoding="utf-8")
        result = pack(
            sprint_id="TEST-SPRINT-001",
            run_id="test-run-001",
            evidence_root=".local/evidences/test-run-001",
            ledger_path=ledger_file,
            work_items_path=items_file,
        )
        assert len(result["planned_work_items"]) == 2
        assert result["test_results"]["passed"] == 12  # 7+5

    def test_completed_work_items_extracted(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps({"schema_version": "1.0", "lanes": []}), encoding="utf-8")
        items_file = tmp_path / "items.json"
        items_file.write_text(json.dumps(SAMPLE_WORK_ITEMS), encoding="utf-8")
        result = pack(
            sprint_id="TEST-SPRINT-001",
            run_id="test-run-001",
            evidence_root=".local/evidences/test-run-001",
            ledger_path=ledger_file,
            work_items_path=items_file,
        )
        assert "W1-FOO" in result["completed_work_items"]
        assert "W2-BAR" in result["completed_work_items"]
        assert result["incomplete_work_items"] == []

    def test_output_written_as_yaml(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps(SAMPLE_LEDGER), encoding="utf-8")
        output = tmp_path / "output.yaml"
        pack(
            sprint_id="TEST-SPRINT-001",
            run_id="test-run-001",
            evidence_root=".local/evidences/test-run-001",
            ledger_path=ledger_file,
            output_path=output,
        )
        assert output.exists()
        loaded = yaml.safe_load(output.read_text(encoding="utf-8"))
        assert loaded["sprint_id"] == "TEST-SPRINT-001"

    def test_empty_ledger_handled(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps({"schema_version": "1.0", "lanes": []}), encoding="utf-8")
        result = pack(
            sprint_id="EMPTY-SPRINT",
            run_id="empty-run",
            evidence_root=".local/evidences/empty-run",
            ledger_path=ledger_file,
        )
        assert result["tests_run"] == 0
        assert result["changed_files"] == []

    def test_missing_ledger_handled_gracefully(self, tmp_path):
        missing = tmp_path / "nonexistent.json"
        result = pack(
            sprint_id="TEST-SPRINT",
            run_id="test-run",
            evidence_root=".local/evidences/test-run",
            ledger_path=missing,
        )
        # Should not raise; returns empty-data declaration
        assert "sprint_id" in result

    def test_output_directory_created(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps({"schema_version": "1.0", "lanes": []}), encoding="utf-8")
        nested_output = tmp_path / "new_dir" / "subdir" / "declaration.yaml"
        pack(
            sprint_id="TEST-SPRINT",
            run_id="test-run",
            evidence_root=".local/evidences/test-run",
            ledger_path=ledger_file,
            output_path=nested_output,
        )
        assert nested_output.exists()

    def test_git_head_fields_populated(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps({"schema_version": "1.0", "lanes": []}), encoding="utf-8")
        result = pack(
            sprint_id="TEST-SPRINT",
            run_id="test-run",
            evidence_root=".local/evidences/test-run",
            ledger_path=ledger_file,
        )
        # Git fields should not be empty strings
        assert result["git_head_start"]
        assert result["git_head_end"]
        assert result["git_status_final"]

    def test_start_end_time_override(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps({"schema_version": "1.0", "lanes": []}), encoding="utf-8")
        result = pack(
            sprint_id="TEST-SPRINT",
            run_id="test-run",
            evidence_root=".local/evidences/test-run",
            ledger_path=ledger_file,
            start_time="2026-01-01T00:00:00Z",
            end_time="2026-01-01T02:00:00Z",
        )
        assert result["start_time"] == "2026-01-01T00:00:00Z"
        assert result["end_time"] == "2026-01-01T02:00:00Z"

    def test_evidence_root_in_reports_created(self, tmp_path):
        ledger_file = tmp_path / "ledger.json"
        ledger_file.write_text(json.dumps({"schema_version": "1.0", "lanes": []}), encoding="utf-8")
        result = pack(
            sprint_id="TEST-SPRINT",
            run_id="test-run",
            evidence_root=".local/evidences/test-run",
            ledger_path=ledger_file,
        )
        decl_path = ".local/evidences/test-run/evidence-declaration.yaml"
        assert decl_path in result["reports_created"]
