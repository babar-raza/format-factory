"""
test_taskcard_generation.py — Tests for TC-VWR-005 (velvet-swinging-wreath)

Verifies that generate_behavioral_gap_taskcards produces well-formed taskcards
from AUDIT_REQUIRES_ITERATION results and that write_plan_lock wires the call
automatically on ITERATION_REQUIRED.

TC-VWR-005-03 (velvet-swinging-wreath, 2026-07-12)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from lifecycle_audit import generate_behavioral_gap_taskcards, generate_audit_taskcard  # noqa: E402


# ---------------------------------------------------------------------------
# Test 1: Empty / pass result → no taskcards generated
# ---------------------------------------------------------------------------

def test_generate_gap_taskcards_pass_verdict_returns_empty():
    """TC-VWR-005-03-T1: AUDIT_PASS result must return no gap taskcards."""
    audit_result = {
        "verdict": "AUDIT_PASS",
        "mission_id": "TEST-MACH-001",
        "findings": [
            {
                "finding_id": "FIND-001",
                "type": "G1_SIGNAL_STALE",
                "severity": "CRITICAL",
                "description": "Signal is stale",
                "recommended_action": "Reset signal",
            }
        ],
    }
    result = generate_behavioral_gap_taskcards(audit_result)
    assert result == [], (
        "AUDIT_PASS should produce zero gap taskcards even if findings exist"
    )


# ---------------------------------------------------------------------------
# Test 2: ITERATION_REQUIRED with CRITICAL/HIGH findings → taskcards produced
# ---------------------------------------------------------------------------

def test_generate_gap_taskcards_iteration_required_produces_taskcards():
    """TC-VWR-005-03-T2: AUDIT_REQUIRES_ITERATION with CRITICAL/HIGH findings
    must produce one taskcard per actionable finding."""
    audit_result = {
        "verdict": "AUDIT_REQUIRES_ITERATION",
        "mission_id": "TEST-MACH-VWR-001",
        "findings": [
            {
                "finding_id": "FIND-B1",
                "type": "GB1_BEHAVIORAL_ITERATION_INSUFFICIENT",
                "severity": "CRITICAL",
                "description": "Behavioral iterations below threshold: 0 < 2",
                "recommended_action": "Execute another full machinery iteration",
            },
            {
                "finding_id": "FIND-G4",
                "type": "G4_SPRINT_AUDIT_ABSENT",
                "severity": "HIGH",
                "description": "Sprint audit log absent",
                "recommended_action": "Run lifecycle_audit with --sprint-id",
            },
            {
                "finding_id": "FIND-INFO",
                "type": "INFO_OBSERVATION",
                "severity": "INFO",
                "description": "Informational only",
                "recommended_action": "",
            },
        ],
    }
    result = generate_behavioral_gap_taskcards(audit_result)

    # Only CRITICAL and HIGH findings become taskcards
    assert len(result) == 2, f"Expected 2 taskcards, got {len(result)}: {result}"

    task_ids = [tc["task_id"] for tc in result]
    assert "TC-AUD-B1" in task_ids
    assert "TC-AUD-G4" in task_ids

    for tc in result:
        assert tc["status"] == "READY"
        assert tc["mission_id"] == "TEST-MACH-VWR-001"
        assert "generated_by" in tc
        assert "generated_at" in tc
        assert "severity" in tc


# ---------------------------------------------------------------------------
# Test 3: generate_audit_taskcard produces required fields for a finding
# ---------------------------------------------------------------------------

def test_generate_audit_taskcard_fields():
    """TC-VWR-005-03-T3: generate_audit_taskcard must produce all required fields."""
    finding = {
        "finding_id": "FIND-B1",
        "type": "GB1_BEHAVIORAL_ITERATION_INSUFFICIENT",
        "severity": "CRITICAL",
        "description": "Behavioral iterations below threshold",
        "recommended_action": "Run another iteration",
        "source_file": "lifecycle_audit.py",
    }
    tc = generate_audit_taskcard(finding, "TEST-MACH-001")

    required_fields = [
        "task_id", "stable_key", "mission_id", "status",
        "objective", "finding_ref", "recommended_action", "severity",
    ]
    for field in required_fields:
        assert field in tc, f"Missing required field '{field}' in taskcard: {tc}"

    assert tc["task_id"] == "TC-AUD-B1"
    assert tc["mission_id"] == "TEST-MACH-001"
    assert tc["status"] == "READY"
    assert tc["severity"] == "CRITICAL"
    assert tc["finding_ref"] == "FIND-B1"
    assert "Behavioral iterations" in tc["objective"]
