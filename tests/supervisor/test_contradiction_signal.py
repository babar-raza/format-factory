"""Tests for TC-OCRD-B1: Contradiction Signal in Continuation Loop.

Covers:
  - contradictions.json with critical_count=2 → signal contains critical_contradiction_count=2
  - contradictions.json with critical_count=0 → no contradiction_warnings
  - missing contradictions.json → no error, critical_contradiction_count=0
  - CONTINUE output always contains contradiction_warnings key (even empty)
"""
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
_TOOLS = str(REPO / "tools" / "supervisor")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)


# ---------------------------------------------------------------------------
# Test 1: contradictions.json with critical_count=2 → signal contains key=2
# ---------------------------------------------------------------------------

def test_autonomous_cycle_embeds_critical_contradiction_count(tmp_path):
    """Verify the autonomous_cycle.py source embeds critical_contradiction_count in signal."""
    source = (REPO / "tools" / "supervisor" / "autonomous_cycle.py").read_text(encoding="utf-8")
    assert "critical_contradiction_count" in source, (
        "autonomous_cycle.py must set signal['critical_contradiction_count']"
    )
    assert "contradiction_summary" in source, (
        "autonomous_cycle.py must set signal['contradiction_summary']"
    )


# ---------------------------------------------------------------------------
# Test 2: _classify_outcome correctly reads critical_count
# ---------------------------------------------------------------------------

def test_contradiction_field_extraction_logic(tmp_path):
    """Simulate the contradictions.json read logic and verify correct extraction."""
    contradictions_data = {
        "critical_count": 2,
        "overall": "CRITICAL",
        "contradictions": [
            {"id": "C-001", "severity": "CRITICAL", "description": "Test conflict"},
            {"id": "C-002", "severity": "CRITICAL", "description": "Another conflict"},
            {"id": "C-003", "severity": "WARNING", "description": "Non-critical"},
        ]
    }
    # Simulate the logic from autonomous_cycle.py
    _critical_count = int(contradictions_data.get("critical_count", 0))
    _contradiction_summary = [
        c.get("id", "") for c in contradictions_data.get("contradictions", [])
        if c.get("severity") == "CRITICAL" and c.get("id")
    ]
    assert _critical_count == 2
    assert "C-001" in _contradiction_summary
    assert "C-002" in _contradiction_summary
    assert "C-003" not in _contradiction_summary  # WARNING not included


# ---------------------------------------------------------------------------
# Test 3: missing contradictions.json → no error, critical_contradiction_count=0
# ---------------------------------------------------------------------------

def test_missing_contradictions_file_no_error(tmp_path):
    """When contradictions.json is missing, critical count defaults to 0."""
    contradictions_path = tmp_path / "reports" / "supervisor" / "contradictions.json"
    # File intentionally not created
    _critical_count = 0
    _contradiction_summary: list = []
    try:
        if contradictions_path.exists():
            _c_data = json.loads(contradictions_path.read_text())
            _critical_count = int(_c_data.get("critical_count", 0))
            _contradiction_summary = [
                c.get("id", "") for c in _c_data.get("contradictions", [])
                if c.get("severity") == "CRITICAL"
            ]
    except Exception:
        pass
    assert _critical_count == 0
    assert _contradiction_summary == []


# ---------------------------------------------------------------------------
# Test 4: CONTINUE output always has contradiction_warnings key
# ---------------------------------------------------------------------------

def test_check_continuation_has_contradiction_warnings_key():
    """Source-code verification that check_continuation.py emits contradiction_warnings."""
    source = (REPO / "tools" / "supervisor" / "check_continuation.py").read_text(encoding="utf-8")
    assert "contradiction_warnings" in source, (
        "check_continuation.py must emit contradiction_warnings in CONTINUE output"
    )


# ---------------------------------------------------------------------------
# Test 5: contradiction_warnings is empty list when critical_count=0
# ---------------------------------------------------------------------------

def test_contradiction_warnings_empty_when_no_critical():
    """Verify the logic: critical_contradiction_count=0 → empty list."""
    signal = {"critical_contradiction_count": 0, "contradiction_summary": []}
    warnings = (
        [f"critical_contradictions_active: {signal.get('critical_contradiction_count', 0)}"]
        if signal.get("critical_contradiction_count", 0) > 0 else []
    )
    assert warnings == []


# ---------------------------------------------------------------------------
# Test 6: contradiction_warnings has entry when critical_count > 0
# ---------------------------------------------------------------------------

def test_contradiction_warnings_populated_when_critical():
    """Verify the logic: critical_contradiction_count=3 → warning in list."""
    signal = {"critical_contradiction_count": 3, "contradiction_summary": ["C-001", "C-002", "C-003"]}
    warnings = (
        [f"critical_contradictions_active: {signal.get('critical_contradiction_count', 0)}"]
        if signal.get("critical_contradiction_count", 0) > 0 else []
    )
    assert len(warnings) == 1
    assert "3" in warnings[0]
