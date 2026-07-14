"""
test_lifecycle_guards.py — Tests for TC-VWR-006 (velvet-swinging-wreath)

Verifies that:
  - G4 check_sprint_audit_guard returns CRITICAL (not None) when audit log is absent
    (TC-VWR-006-01: was a graceful skip/None before this fix)
  - G3X check fires CRITICAL when MAX_ITERATIONS and behavioral proof missing
    (TC-VWR-006-03: prevents false mission completion via iteration exhaustion)

TC-VWR-006-02 / TC-VWR-006-03 (velvet-swinging-wreath, 2026-07-12)
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from lifecycle_audit import (  # noqa: E402
    check_sprint_audit_guard,
    run_lifecycle_audit,
    _MACHINERY_LEDGER_PATH_REL,
)


# ---------------------------------------------------------------------------
# Test 1: G4 — audit log ABSENT → CRITICAL (TC-VWR-006-02)
# ---------------------------------------------------------------------------

def test_g4_absent_audit_log_is_critical(tmp_path):
    """TC-VWR-006-02-T1: When sprint-audit-log.json is absent but evidence-review.json
    exists, check_sprint_audit_guard must return a CRITICAL finding (not None)."""
    # Create only evidence-review.json — do NOT create sprint-audit-log.json
    review = tmp_path / "evidence-review.json"
    review.write_text(json.dumps({"status": "ok"}), encoding="utf-8")

    audit_log = tmp_path / "sprint-audit-log.json"  # does NOT exist

    finding = check_sprint_audit_guard(
        repo_root=tmp_path,
        audit_log_path=audit_log,
        evidence_review_path=review,
    )

    assert finding is not None, (
        "G4 must return a finding when audit log is absent (TC-VWR-006-01 fix)"
    )
    assert finding["severity"] == "CRITICAL", (
        f"Expected CRITICAL severity for absent audit log, got: {finding['severity']}"
    )
    assert finding.get("guard_id") == "G4_SPRINT_AUDIT"
    assert "ABSENT" in finding["finding_id"] or "never" in finding["description"].lower()


# ---------------------------------------------------------------------------
# Test 2: G4 — audit log STALE (exists but older than review) → MEDIUM
# ---------------------------------------------------------------------------

def test_g4_stale_audit_log_is_medium(tmp_path):
    """TC-VWR-006-02-T2: When sprint-audit-log.json exists but is >60s older than
    evidence-review.json, check_sprint_audit_guard must return MEDIUM (stale warning)."""
    audit_log = tmp_path / "sprint-audit-log.json"
    audit_log.write_text(json.dumps({"runs": []}), encoding="utf-8")

    # Make audit_log appear 120 seconds old compared to the review file
    old_time = time.time() - 120
    import os
    os.utime(str(audit_log), (old_time, old_time))

    review = tmp_path / "evidence-review.json"
    review.write_text(json.dumps({"status": "ok"}), encoding="utf-8")
    # review mtime = now, audit_log mtime = 120s ago → review newer by >60s

    finding = check_sprint_audit_guard(
        repo_root=tmp_path,
        audit_log_path=audit_log,
        evidence_review_path=review,
    )

    assert finding is not None, "G4 should fire MEDIUM when audit log is stale"
    assert finding["severity"] == "MEDIUM"
    assert finding.get("guard_id") == "G4_SPRINT_AUDIT"


# ---------------------------------------------------------------------------
# Test 3: G4 — audit log current → None (pass)
# ---------------------------------------------------------------------------

def test_g4_current_audit_log_passes(tmp_path):
    """TC-VWR-006-02-T3: When sprint-audit-log.json is current (newer or same as review),
    check_sprint_audit_guard must return None."""
    review = tmp_path / "evidence-review.json"
    review.write_text(json.dumps({"status": "ok"}), encoding="utf-8")

    old_time = time.time() - 120
    import os
    os.utime(str(review), (old_time, old_time))

    audit_log = tmp_path / "sprint-audit-log.json"
    audit_log.write_text(json.dumps({"runs": []}), encoding="utf-8")
    # audit_log mtime = now, review mtime = 120s ago → audit log is NEWER → OK

    finding = check_sprint_audit_guard(
        repo_root=tmp_path,
        audit_log_path=audit_log,
        evidence_review_path=review,
    )

    assert finding is None, (
        f"G4 must return None when audit log is current, got: {finding}"
    )


# ---------------------------------------------------------------------------
# Test 4: G3X — MAX_ITERATIONS + missing behavioral proof → CRITICAL in audit result
# ---------------------------------------------------------------------------

def test_g3x_iter_limit_without_behavioral_proof(tmp_path):
    """TC-VWR-006-03-T1: When the continuation signal shows iteration >= max_iterations
    AND mission-ledger shows current_behavioral_iterations < required, run_lifecycle_audit
    must include a G3X CRITICAL finding to block premature TERMINAL_CLOSED."""
    # Set up repo structure
    local_super = tmp_path / ".local" / "supervisor"
    local_super.mkdir(parents=True)

    # Continuation signal with stop_reason=MAX_ITERATIONS to trigger G3 guard
    signal_path = local_super / "continuation-signal.json"
    signal_path.write_text(json.dumps({
        "autonomous_continue": True,
        "iteration": 10,
        "max_iterations": 5,
        "stop_reason": "MAX_ITERATIONS",
        "track": "machinery",
        "rework_items": [],
        "mission_id": "TEST-G3X-VWR-001",
    }), encoding="utf-8")

    # Mission ledger: 0 iterations completed (below required 2)
    machinery_dir = local_super / "machinery"
    machinery_dir.mkdir(parents=True)
    ledger_path = machinery_dir / "mission-ledger.json"
    ledger_path.write_text(json.dumps({
        "schema_version": "1.0",
        "mission_id": "TEST-G3X-VWR-001",
        "mission_type": "machinery_hardening",
        "behavioral_iterations_required": 2,
        "current_behavioral_iterations": 0,
        "stop_status": "RUNNING",
    }), encoding="utf-8")

    # Write a minimal plan file with machinery_hardening type
    plan_path = tmp_path / "plans" / ".claude" / "test-g3x-plan.md"
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text(
        "# Test G3X Plan\n\n**mission_id:** TEST-G3X-VWR-001\n**plan_type:** machinery_hardening\n\n"
        "| TC-ID | Status |\n|-------|--------|\n| TC-G3X-001 | CLOSED |\n",
        encoding="utf-8",
    )

    result = run_lifecycle_audit(
        repo_root=tmp_path,
        plan_path=str(plan_path),
        mission_id="TEST-G3X-VWR-001",
    )

    findings_by_guard = {f.get("guard_id"): f for f in result.get("findings", [])}
    guard_ids = list(findings_by_guard.keys())

    # G3X must fire when G3 (iteration limit exceeded) + behavioral proof missing
    assert "G3X" in guard_ids, (
        f"G3X guard must fire when iteration >= max_iterations and behavioral proof is missing. "
        f"Found guards: {guard_ids}\nFull result: {json.dumps(result, indent=2)}"
    )
    g3x_finding = findings_by_guard["G3X"]
    assert g3x_finding["severity"] == "CRITICAL", (
        f"G3X must be CRITICAL, got: {g3x_finding['severity']}"
    )
    # Audit must require iteration
    assert result["verdict"] == "AUDIT_REQUIRES_ITERATION", (
        f"Verdict must be AUDIT_REQUIRES_ITERATION when G3X fires, got: {result['verdict']}"
    )
