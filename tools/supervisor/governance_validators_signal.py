"""
governance_validators_signal.py — V67 maturity signal schema validator.

Created as a new file because governance_validators.py (3177/3179 LOC) and
governance_validators_ext.py (1423/1423 LOC) are both at their baseline_loc_cap.
baseline_loc_cap is write-once and cannot be increased.

V67: validate_maturity_signal_schema — blocks on missing required fields or
     wrong schema version in reports/supervisor/maturity-signal.json.
"""
from __future__ import annotations

import json
from pathlib import Path

_REQUIRED_FIELDS = [
    "schema",
    "project_id",
    "run_id",
    "timestamp",
    "sprint_verdict",
    "autonomous_continue",
    "iteration",
    "test_results",
    "work_items",
    "rework_items",
    "agentic_maturity_score",
    "active_gaps",
    "next_action_hint",
    "integration_mode",
]

_EXPECTED_SCHEMA = "format-factory-maturity-signal/v1"


def validate_maturity_signal_schema(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V67 (TC-AMD-MACH-002): Verify reports/supervisor/maturity-signal.json conforms
    to format-factory-maturity-signal/v1 schema.

    Returns WARN when the file does not yet exist (signal not yet produced).
    Returns FAIL (blocks_sprint=True) when the file is present but malformed or
    missing required fields.
    Returns PASS when all required fields are present and schema version matches.
    """
    root = repo_root or Path(__file__).resolve().parent.parent.parent
    signal_path = root / "reports" / "supervisor" / "maturity-signal.json"

    if not signal_path.exists():
        return {
            "validator": "validate_maturity_signal_schema",
            "result": "WARN",
            "blocks_sprint": False,
            "items": [],
            "summary": "V67: maturity-signal.json not found — signal not yet produced",
        }

    try:
        data = json.loads(signal_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "validator": "validate_maturity_signal_schema",
            "result": "FAIL",
            "blocks_sprint": True,
            "items": [str(exc)],
            "summary": f"V67: maturity-signal.json parse error: {exc}",
        }

    missing = [f for f in _REQUIRED_FIELDS if f not in data]
    if missing:
        return {
            "validator": "validate_maturity_signal_schema",
            "result": "FAIL",
            "blocks_sprint": True,
            "items": missing,
            "summary": f"V67: Missing required fields: {missing}",
        }

    actual_schema = data.get("schema", "")
    if actual_schema != _EXPECTED_SCHEMA:
        return {
            "validator": "validate_maturity_signal_schema",
            "result": "FAIL",
            "blocks_sprint": True,
            "items": [actual_schema],
            "summary": f"V67: schema field mismatch: got {actual_schema!r}, expected {_EXPECTED_SCHEMA!r}",
        }

    return {
        "validator": "validate_maturity_signal_schema",
        "result": "PASS",
        "blocks_sprint": False,
        "items": [],
        "summary": f"V67: maturity-signal.json conforms to {_EXPECTED_SCHEMA}",
    }
