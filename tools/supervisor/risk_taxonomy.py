"""Release Risk Taxonomy (FF-XPLAN-001 W2B-003, PYREL-001).

Classifies release gate failures into risk categories for structured
reporting and decision-making.
"""
from __future__ import annotations

RISK_CATEGORIES = {
    "CRITICAL": {
        "description": "Blocks release — data corruption, security vulnerability, or spec violation",
        "examples": ["Oracle FAIL on valid case", "Schema validation FAIL", "Security test FAIL"],
        "action": "Must fix before any release gate can pass",
    },
    "HIGH": {
        "description": "Blocks release — missing required evidence or failed gate check",
        "examples": ["No oracle verdicts", "D0-only depth", "Build failure", "Import failure"],
        "action": "Must resolve — no workaround",
    },
    "MEDIUM": {
        "description": "Should fix — weakens release confidence but does not block",
        "examples": ["WARN from governance validator", "Missing negative test", "Stale evidence"],
        "action": "Fix if possible, document if deferred",
    },
    "LOW": {
        "description": "Advisory — improvement opportunity",
        "examples": ["Missing documentation", "Suboptimal API", "Style issue"],
        "action": "Track in gap ledger for future sprint",
    },
    "EXTERNAL": {
        "description": "Blocked by external dependency — cannot resolve locally",
        "examples": ["Missing PyPI credentials", "Gate 11 not approved", "LibreOffice not installed"],
        "action": "Classify as BLOCKED_EXTERNAL with exact unblock condition",
    },
}


def classify_gate_failure(gate_id: str, check_id: str, detail: str = "") -> dict:
    """Classify a gate check failure into a risk category."""
    # Gate-specific classification rules
    if gate_id == "G5" and check_id == "gate11_approved":
        return {"risk": "EXTERNAL", "reason": "Gate 11 approval requires Babar Raza business decision"}

    if gate_id == "G2" and check_id == "oracle_depth_minimum_d1":
        return {"risk": "HIGH", "reason": "Oracle depth below D1 — property comparison not implemented"}

    if gate_id == "G2" and check_id == "oracle_verdicts_exist":
        return {"risk": "HIGH", "reason": "No oracle verdicts — oracle has not been executed"}

    if gate_id == "G1":
        return {"risk": "HIGH", "reason": f"Source structure incomplete: {check_id}"}

    if gate_id in ("G3", "G4"):
        return {"risk": "HIGH", "reason": f"Build/install verification failed: {check_id}"}

    return {"risk": "MEDIUM", "reason": f"Unclassified failure: {gate_id}/{check_id}"}
