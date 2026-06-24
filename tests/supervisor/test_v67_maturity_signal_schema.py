"""TC-AMD-MACH-002: Tests for V67 validate_maturity_signal_schema.

Verifies:
  - PASS on valid signal with all required fields
  - WARN when signal file does not exist
  - FAIL when required fields are missing
  - FAIL when schema version field has wrong value
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from governance_validators_signal import validate_maturity_signal_schema

_VALID_SIGNAL = {
    "schema": "format-factory-maturity-signal/v1",
    "project_id": "format-factory",
    "run_id": "test-run-001",
    "timestamp": "2026-06-24T00:00:00+00:00",
    "sprint_verdict": "ACCEPTED_VERIFIED",
    "autonomous_continue": True,
    "iteration": 1,
    "test_results": {"total": 10, "passed": 10, "failed": 0},
    "work_items": [],
    "rework_items": [],
    "agentic_maturity_score": 4.4,
    "active_gaps": [],
    "next_action_hint": "continue",
    "integration_mode": "adapter_required",
}


def _write_signal(tmp_path: Path, data: dict) -> Path:
    """Write a signal file to tmp_path/reports/supervisor/maturity-signal.json."""
    sig_dir = tmp_path / "reports" / "supervisor"
    sig_dir.mkdir(parents=True, exist_ok=True)
    sig_path = sig_dir / "maturity-signal.json"
    sig_path.write_text(json.dumps(data), encoding="utf-8")
    return sig_path


def test_v67_passes_valid_signal(tmp_path):
    """PASS when all required fields are present and schema version is correct."""
    _write_signal(tmp_path, _VALID_SIGNAL)
    result = validate_maturity_signal_schema({}, repo_root=tmp_path)
    assert result["result"] == "PASS"
    assert result["blocks_sprint"] is False


def test_v67_warns_missing_file(tmp_path):
    """WARN when maturity-signal.json does not exist (signal not yet produced)."""
    result = validate_maturity_signal_schema({}, repo_root=tmp_path)
    assert result["result"] == "WARN"
    assert result["blocks_sprint"] is False


def test_v67_fails_missing_fields(tmp_path):
    """FAIL when required fields are missing from the signal."""
    _write_signal(tmp_path, {"schema": "format-factory-maturity-signal/v1"})
    result = validate_maturity_signal_schema({}, repo_root=tmp_path)
    assert result["result"] == "FAIL"
    assert result["blocks_sprint"] is True
    # Missing fields should be listed
    assert len(result["items"]) > 0


def test_v67_fails_wrong_schema_value(tmp_path):
    """FAIL when schema field contains wrong version string."""
    bad_signal = dict(_VALID_SIGNAL)
    bad_signal["schema"] = "wrong-schema/v99"
    _write_signal(tmp_path, bad_signal)
    result = validate_maturity_signal_schema({}, repo_root=tmp_path)
    assert result["result"] == "FAIL"
    assert result["blocks_sprint"] is True
    assert "wrong-schema/v99" in result["items"][0]
