"""Tests for TC-FGSQ-011: reconcile_gap_ledger_files() — gap ledger drift detection.

Verifies that OPEN gap entries referencing absent files are detected and reported,
and that consecutive-cycle escalation tracks correctly.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from autonomous_cycle_extensions import reconcile_gap_ledger_files


def _write_ledger(tmp_path: Path, gaps: list) -> Path:
    ledger_path = tmp_path / "gap-ledger.yaml"
    ledger_path.write_text(yaml.dump({"gaps": gaps}), encoding="utf-8")
    return ledger_path


def test_open_gap_with_absent_file_is_reported(tmp_path):
    """An OPEN gap whose files: entry does not exist → reported as drifted."""
    ledger = _write_ledger(tmp_path, [{
        "gap_id": "PCG-TEST-001",
        "status": "OPEN",
        "files": ["src/net/fods/NonExistent.cs"],
    }])
    result = reconcile_gap_ledger_files(
        repo_root=tmp_path,
        ledger_path=ledger,
        drift_state_path=tmp_path / "gap-drift-state.json",
        drift_report_path=tmp_path / "gap-ledger-drift.json",
    )
    assert result["gaps_checked"] == 1
    assert len(result["drifted"]) == 1
    drift = result["drifted"][0]
    assert drift["gap_id"] == "PCG-TEST-001"
    assert "src/net/fods/NonExistent.cs" in drift["absent_files"]
    assert drift["consecutive_absent_cycles"] == 1
    assert not drift["escalated"]


def test_open_gap_with_present_file_is_clean(tmp_path):
    """An OPEN gap whose files: all exist → not in drifted list."""
    real_file = tmp_path / "src" / "net" / "fods" / "FodsDocument.cs"
    real_file.parent.mkdir(parents=True)
    real_file.write_text("// real file", encoding="utf-8")
    ledger = _write_ledger(tmp_path, [{
        "gap_id": "PCG-TEST-002",
        "status": "OPEN",
        "files": ["src/net/fods/FodsDocument.cs"],
    }])
    result = reconcile_gap_ledger_files(
        repo_root=tmp_path,
        ledger_path=ledger,
        drift_state_path=tmp_path / "gap-drift-state.json",
        drift_report_path=tmp_path / "gap-ledger-drift.json",
    )
    assert result["gaps_checked"] == 1
    assert len(result["drifted"]) == 0
    assert len(result["escalated"]) == 0


def test_consecutive_absent_cycles_increment(tmp_path):
    """Three consecutive cycles with absent file → escalated=True."""
    ledger = _write_ledger(tmp_path, [{
        "gap_id": "PCG-TEST-003",
        "status": "OPEN",
        "files": ["src/net/fods/Gone.cs"],
    }])
    state = tmp_path / "state.json"
    report = tmp_path / "report.json"

    # Simulate 2 prior cycles with absent file
    state.write_text(json.dumps({"PCG-TEST-003": {"consecutive_absent_cycles": 2}}), encoding="utf-8")

    result = reconcile_gap_ledger_files(
        repo_root=tmp_path,
        ledger_path=ledger,
        drift_state_path=state,
        drift_report_path=report,
    )
    assert result["drifted"][0]["consecutive_absent_cycles"] == 3
    assert result["drifted"][0]["escalated"] is True
    assert len(result["escalated"]) == 1


def test_closed_gap_is_skipped(tmp_path):
    """CLOSED gaps are not checked for file drift."""
    ledger = _write_ledger(tmp_path, [{
        "gap_id": "PCG-TEST-004",
        "status": "CLOSED",
        "files": ["src/net/fods/AlsoGone.cs"],
    }])
    result = reconcile_gap_ledger_files(
        repo_root=tmp_path,
        ledger_path=ledger,
        drift_state_path=tmp_path / "state.json",
        drift_report_path=tmp_path / "report.json",
    )
    assert result["gaps_checked"] == 0
    assert len(result["drifted"]) == 0


def test_drift_report_json_is_written(tmp_path):
    """The drift report JSON is written at the expected path."""
    ledger = _write_ledger(tmp_path, [{
        "gap_id": "PCG-TEST-005",
        "status": "OPEN",
        "files": ["src/net/fods/Missing.cs"],
    }])
    report_path = tmp_path / "gap-ledger-drift.json"
    reconcile_gap_ledger_files(
        repo_root=tmp_path,
        ledger_path=ledger,
        drift_state_path=tmp_path / "state.json",
        drift_report_path=report_path,
    )
    assert report_path.exists()
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["gaps_checked"] == 1
    assert len(data["drifted"]) == 1


def test_missing_ledger_returns_empty(tmp_path):
    """If the ledger file does not exist, returns empty dict (non-blocking)."""
    result = reconcile_gap_ledger_files(
        repo_root=tmp_path,
        ledger_path=tmp_path / "does-not-exist.yaml",
        drift_state_path=tmp_path / "state.json",
        drift_report_path=tmp_path / "report.json",
    )
    assert result == {}
