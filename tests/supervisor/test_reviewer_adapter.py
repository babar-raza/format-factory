"""TC-AMD-ADAPT-001: Tests for reviewer_adapter.py.

Verifies:
  - ACCEPTED_VERIFIED → completed status mapping
  - REWORK_REQUIRED → paused status mapping
  - ff_* extension fields are present in output
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from reviewer_adapter import adapt_signal_to_run_state, write_adapted_state


_SAMPLE_SIGNAL = {
    "schema": "format-factory-maturity-signal/v1",
    "project_id": "format-factory",
    "run_id": "test-run-001",
    "timestamp": "2026-06-24T00:00:00+00:00",
    "sprint_verdict": "ACCEPTED_VERIFIED",
    "autonomous_continue": True,
    "iteration": 1,
    "test_results": {"total": 10, "passed": 10, "failed": 0},
    "work_items": [{"id": "TC-001", "grade": "ACCEPTED_VERIFIED"}],
    "rework_items": [],
    "agentic_maturity_score": 4.4,
    "active_gaps": [],
    "next_action_hint": "continue",
    "integration_mode": "adapter_required",
}


def test_status_mapping_accepted_verified():
    """ACCEPTED_VERIFIED sprint_verdict → agent-run-state status=completed."""
    state = adapt_signal_to_run_state(_SAMPLE_SIGNAL)
    assert state["status"] == "completed"
    assert state["schema"] == "agent-run-state/v1"
    assert state["runId"] == "test-run-001"


def test_status_mapping_rework_required():
    """REWORK_REQUIRED sprint_verdict → agent-run-state status=paused."""
    signal = dict(_SAMPLE_SIGNAL, sprint_verdict="REWORK_REQUIRED")
    state = adapt_signal_to_run_state(signal)
    assert state["status"] == "paused"


def test_ff_extension_fields_present():
    """ff_* extension fields are present in the adapted state output."""
    state = adapt_signal_to_run_state(_SAMPLE_SIGNAL)
    assert "ff_sprint_verdict" in state
    assert state["ff_sprint_verdict"] == "ACCEPTED_VERIFIED"
    assert "ff_maturity_score" in state
    assert state["ff_maturity_score"] == 4.4
    assert "ff_autonomous_continue" in state
    assert state["ff_autonomous_continue"] is True
    assert "ff_integration_mode" in state
    assert state["ff_integration_mode"] == "adapter_required"


def test_write_adapted_state_creates_file(tmp_path):
    """write_adapted_state() creates output file with valid JSON."""
    output = tmp_path / "agent-run-state.json"
    ok = write_adapted_state(_SAMPLE_SIGNAL, output)
    assert ok is True
    assert output.exists()
    data = json.loads(output.read_text())
    assert data["status"] == "completed"
    assert data["ff_sprint_verdict"] == "ACCEPTED_VERIFIED"
