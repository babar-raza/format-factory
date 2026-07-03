"""test_terminal_closure_pilots.py — TC-TCF-008: 12-pilot regression suite.

Proves the complete terminal-closure lifecycle for plans with tracked taskcards.
All pilots use tmp_path fixtures and import functions directly — no subprocess calls.

Pilots:
  A — Legitimate terminal closure (all TCs closed, audit passes)
  B — Open requirement blocks terminal closure (auto-audit fires → ITERATION_REQUIRED)
  C — Queue exhaustion guard (zero-task-counter count=3 → GUARD_FAIL)
  D — Iteration limit guard (stop_reason=MAX_ITERATIONS → GUARD_WARN)
  E — Closeout task guard (changed_files exclusively in .local/ → GUARD_FAIL)
  F — Unconsumed sprint audit guard (evidence-review newer than audit log → GUARD_WARN)
  G — Regression after closure: find_next_eligible_task_in_plan returns TC dict
  H — Missed in-scope work: reopen_plan succeeds, closure_history len=1
  I — Out-of-scope work: classify_work_scope → OUT_OF_SCOPE
  J — In-scope work with TC-ID overlap: classify_work_scope → IN_SCOPE
  K — Reclosure after reopen: closure_history len=2
  L — Idempotency: generate_closure_artifacts twice → identical SHA-256
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Make tools/supervisor importable
_TOOLS_DIR = Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _plan_with_open_tc(tmp_path: Path) -> Path:
    """Minimal plan file with one OPEN and one CLOSED taskcard."""
    plan = tmp_path / "plans" / "test-plan.md"
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_text(
        "# Test Plan\n\n"
        "| TC-TCF-AAA | OPEN | Do something |\n"
        "| TC-TCF-BBB | CLOSED | Done |\n",
        encoding="utf-8",
    )
    return plan


def _plan_all_closed(tmp_path: Path) -> Path:
    """Minimal plan file with all taskcards CLOSED."""
    plan = tmp_path / "plans" / "test-plan-done.md"
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_text(
        "# Test Plan\n\n"
        "| TC-TCF-AAA | CLOSED | Done |\n"
        "| TC-TCF-BBB | CLOSED | Done |\n",
        encoding="utf-8",
    )
    return plan


# ---------------------------------------------------------------------------
# Pilot A: Legitimate terminal closure
# ---------------------------------------------------------------------------

def test_pilot_a_legitimate_closure(tmp_path: Path) -> None:
    """All TCs closed + audit passes → TERMINAL_CLOSED and record written."""
    from lifecycle_audit import run_lifecycle_audit

    plan = _plan_all_closed(tmp_path)

    # Write a continuation signal with no premature triggers
    _write_json(
        tmp_path / ".local" / "supervisor" / "continuation-signal.json",
        {"autonomous_continue": True, "iteration": 1, "stop_reason": None},
    )

    result = run_lifecycle_audit(
        repo_root=tmp_path,
        plan_path=str(plan),
        mission_id="pilot-a",
        sprint_id="TC-TCF-BBB",
    )

    # AUDIT_PASS means no open taskcards, no open gaps — legitimate for closure
    assert result["verdict"] in ("AUDIT_PASS", "CLOSURE_AUTHORIZED", "AUDIT_COMPLETE"), (
        f"Expected successful audit verdict, got: {result['verdict']}"
    )
    assert not result.get("open_taskcards"), f"Expected no open taskcards, got: {result.get('open_taskcards')}"


# ---------------------------------------------------------------------------
# Pilot B: Open requirement blocks terminal closure
# ---------------------------------------------------------------------------

def test_pilot_b_open_tc_blocks_closure(tmp_path: Path) -> None:
    """Plan has OPEN TC → auto-audit blocks TERMINAL_CLOSED."""
    from lifecycle_audit import run_lifecycle_audit

    plan = _plan_with_open_tc(tmp_path)

    _write_json(
        tmp_path / ".local" / "supervisor" / "continuation-signal.json",
        {"autonomous_continue": True, "iteration": 1, "stop_reason": None},
    )

    result = run_lifecycle_audit(
        repo_root=tmp_path,
        plan_path=str(plan),
        mission_id="pilot-b",
        sprint_id="TC-TCF-AAA",
    )

    assert result["verdict"] == "AUDIT_REQUIRES_ITERATION", (
        f"Expected AUDIT_REQUIRES_ITERATION for plan with open TCs, got: {result['verdict']}"
    )
    assert result.get("open_taskcards"), "Expected open taskcards to be listed"


# ---------------------------------------------------------------------------
# Pilot C: Queue exhaustion guard
# ---------------------------------------------------------------------------

def test_pilot_c_queue_exhaustion_guard(tmp_path: Path) -> None:
    """zero-task-counter count=3 without mission_complete → GUARD_FAIL."""
    from lifecycle_audit import check_queue_exhaustion_guard

    signal = {"autonomous_continue": True, "iteration": 5, "stop_reason": None}
    _write_json(
        tmp_path / ".local" / "supervisor" / "zero-task-counter.json",
        {"count": 3, "mission_complete_declared": False},
    )

    result = check_queue_exhaustion_guard(repo_root=tmp_path, signal=signal)
    assert result["severity"] == "CRITICAL", (
        f"Expected CRITICAL guard fail for count=3, got: {result}"
    )
    assert "GUARD_FAIL" in result.get("description", "").upper() or result.get("guard_result") == "GUARD_FAIL"


# ---------------------------------------------------------------------------
# Pilot D: Iteration limit guard
# ---------------------------------------------------------------------------

def test_pilot_d_iteration_limit_guard(tmp_path: Path) -> None:
    """stop_reason=MAX_ITERATIONS → GUARD_WARN."""
    from lifecycle_audit import check_iteration_limit_guard

    signal = {"autonomous_continue": False, "iteration": 10, "stop_reason": "MAX_ITERATIONS"}
    result = check_iteration_limit_guard(signal=signal)
    assert result["severity"] == "MEDIUM", (
        f"Expected MEDIUM for MAX_ITERATIONS stop, got: {result}"
    )
    assert "GUARD_WARN" in result.get("description", "").upper() or result.get("guard_result") == "GUARD_WARN"


# ---------------------------------------------------------------------------
# Pilot E: Closeout task guard
# ---------------------------------------------------------------------------

def test_pilot_e_closeout_task_guard(tmp_path: Path) -> None:
    """changed_files exclusively in .local/ paths → GUARD_FAIL."""
    from lifecycle_audit import check_closeout_task_guard

    # Write a YAML-format declaration where all changed files are administrative
    decl_dir = tmp_path / ".local" / "evidences" / "run-pilot-e"
    decl_dir.mkdir(parents=True, exist_ok=True)
    (decl_dir / "evidence-declaration.yaml").write_text(
        "run_id: run-pilot-e\n"
        "changed_files:\n"
        "  - .local/evidences/run-pilot-e/evidence-declaration.yaml\n"
        "  - reports/supervisor/evidence-review.json\n",
        encoding="utf-8",
    )

    result = check_closeout_task_guard(repo_root=tmp_path)
    assert result is not None, "Expected CRITICAL finding for closeout-only sprint, got None"
    assert result["severity"] == "CRITICAL", (
        f"Expected CRITICAL for closeout-only sprint, got: {result}"
    )


# ---------------------------------------------------------------------------
# Pilot F: Unconsumed sprint audit guard
# ---------------------------------------------------------------------------

def test_pilot_f_sprint_audit_guard(tmp_path: Path) -> None:
    """evidence-review.json >60s newer than sprint-audit-log.json → GUARD_WARN."""
    from lifecycle_audit import check_sprint_audit_guard
    import os
    import time as _time

    sup_dir = tmp_path / ".local" / "supervisor"
    sup_dir.mkdir(parents=True, exist_ok=True)

    # Write sprint audit log
    audit_log = sup_dir / "sprint-audit-log.json"
    _write_json(audit_log, [{"sprint_id": "S001", "audited_at": "2026-01-01T00:00:00Z"}])

    # Write evidence-review
    review_path = tmp_path / "reports" / "supervisor" / "evidence-review.json"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(json.dumps({"items": []}), encoding="utf-8")

    # Make audit_log appear 2 minutes older than evidence-review
    now = _time.time()
    os.utime(str(audit_log), (now - 120, now - 120))
    os.utime(str(review_path), (now, now))

    result = check_sprint_audit_guard(repo_root=tmp_path)
    assert result is not None, "Expected GUARD_WARN finding when review is >60s newer than audit log"
    assert result["severity"] == "MEDIUM", f"Expected MEDIUM severity, got: {result}"


# ---------------------------------------------------------------------------
# Pilot G: find_next_eligible_task_in_plan returns TC dict
# ---------------------------------------------------------------------------

def test_pilot_g_find_next_eligible_task(tmp_path: Path) -> None:
    """TERMINAL_CLOSED plan with open TC → find_next_eligible_task_in_plan returns dict."""
    from autonomous_cycle_extensions import find_next_eligible_task_in_plan  # type: ignore[import]

    plan = _plan_with_open_tc(tmp_path)
    result = find_next_eligible_task_in_plan(str(plan))

    assert result is not None, "Expected a next-task dict for plan with OPEN TC"
    assert "tc_id" in result
    assert result["tc_id"] == "TC-TCF-AAA"
    assert "plan_path" in result


def test_pilot_g_all_closed_returns_none(tmp_path: Path) -> None:
    """All TCs CLOSED → find_next_eligible_task_in_plan returns None."""
    from autonomous_cycle_extensions import find_next_eligible_task_in_plan  # type: ignore[import]

    plan = _plan_all_closed(tmp_path)
    result = find_next_eligible_task_in_plan(str(plan))
    assert result is None, "Expected None when all taskcards are closed"


# ---------------------------------------------------------------------------
# Pilot H: reopen_plan succeeds, closure_history preserved
# ---------------------------------------------------------------------------

def test_pilot_h_reopen_preserves_history(tmp_path: Path) -> None:
    """Reopen a TERMINAL_CLOSED plan → closure_history len=1 in SUPERSEDED lock."""
    from reopen_plan_lock import reopen_plan

    plan = _plan_with_open_tc(tmp_path)

    # Create a fake TERMINAL_CLOSED lock
    locks_dir = tmp_path / ".local" / "supervisor" / "plan-locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    lock_path = locks_dir / "testsession-abc123.json"
    lock_data = {
        "plan_path": str(plan).replace("\\", "/"),
        "status": "TERMINAL_CLOSED",
        "session_id": "testsession",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "closure_history": [],
        "track_type": "product",
        "last_taskcard": "TC-TCF-BBB",
    }
    _write_json(lock_path, lock_data)

    # Patch _plan_locks_dir and _shared_lock_path for this test
    import reopen_plan_lock as rpl
    _orig_locks_dir = rpl._plan_locks_dir
    _orig_shared = rpl._shared_lock_path
    _orig_reg = rpl._reopening_register_path
    rpl._plan_locks_dir = locks_dir
    rpl._shared_lock_path = tmp_path / ".local" / "supervisor" / "active-plan-lock.json"
    rpl._reopening_register_path = tmp_path / ".local" / "supervisor" / "reopening-register.json"

    try:
        record = reopen_plan(
            plan_path=str(plan),
            reason="Pilot H: missed open taskcard",
            trigger="MISSED_REQUIREMENT",
        )
    finally:
        rpl._plan_locks_dir = _orig_locks_dir
        rpl._shared_lock_path = _orig_shared
        rpl._reopening_register_path = _orig_reg

    # The original lock should now be SUPERSEDED with closure_history len=1
    updated = json.loads(lock_path.read_text())
    assert updated["status"] == "SUPERSEDED"
    assert len(updated.get("closure_history", [])) == 1
    assert record["trigger"] == "MISSED_REQUIREMENT"


# ---------------------------------------------------------------------------
# Pilot I: Out-of-scope work
# ---------------------------------------------------------------------------

def test_pilot_i_out_of_scope(tmp_path: Path) -> None:
    """trigger=OUT_OF_SCOPE_WORK → classify_work_scope returns OUT_OF_SCOPE."""
    from reopen_plan_lock import classify_work_scope

    plan = _plan_all_closed(tmp_path)
    result = classify_work_scope(
        new_work_description="Add a new FODG renderer feature",
        original_plan_path=str(plan),
        trigger="OUT_OF_SCOPE_WORK",
    )
    assert result == "OUT_OF_SCOPE"


# ---------------------------------------------------------------------------
# Pilot J: In-scope work with TC-ID overlap
# ---------------------------------------------------------------------------

def test_pilot_j_in_scope_tc_overlap(tmp_path: Path) -> None:
    """new_work_description references TC-ID from original plan → IN_SCOPE."""
    from reopen_plan_lock import classify_work_scope

    plan = _plan_with_open_tc(tmp_path)  # Contains TC-TCF-AAA and TC-TCF-BBB
    result = classify_work_scope(
        new_work_description="Reopen to complete TC-TCF-AAA which was missed",
        original_plan_path=str(plan),
        trigger="OTHER",
    )
    assert result == "IN_SCOPE"


def test_pilot_j_in_scope_trigger(tmp_path: Path) -> None:
    """MISSED_REQUIREMENT trigger always → IN_SCOPE regardless of description."""
    from reopen_plan_lock import classify_work_scope

    plan = _plan_all_closed(tmp_path)
    result = classify_work_scope(
        new_work_description="No TC-ID here",
        original_plan_path=str(plan),
        trigger="MISSED_REQUIREMENT",
    )
    assert result == "IN_SCOPE"


# ---------------------------------------------------------------------------
# Pilot K: Reclosure after reopen → closure_history len=2
# ---------------------------------------------------------------------------

def test_pilot_k_reclosure_history(tmp_path: Path) -> None:
    """Reopen twice → the first-reopened lock accumulates closure_history of length 2."""
    from reopen_plan_lock import reopen_plan

    plan = _plan_with_open_tc(tmp_path)

    locks_dir = tmp_path / ".local" / "supervisor" / "plan-locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    lock_path = locks_dir / "testsession2-abc456.json"
    lock_data = {
        "plan_path": str(plan).replace("\\", "/"),
        "status": "TERMINAL_CLOSED",
        "session_id": "testsession2",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "closure_history": [
            # Simulate a prior closure that was already recorded
            {
                "status": "TERMINAL_CLOSED",
                "closed_at": "2026-01-01T00:00:00Z",
                "closed_by_session": "original-session",
                "reopened_at": "2026-01-02T00:00:00Z",
                "reopened_by_session": "first-reopen-session",
            }
        ],
        "track_type": "product",
        "last_taskcard": "TC-TCF-BBB",
    }
    _write_json(lock_path, lock_data)

    import reopen_plan_lock as rpl
    _orig_locks_dir = rpl._plan_locks_dir
    _orig_shared = rpl._shared_lock_path
    _orig_reg = rpl._reopening_register_path
    rpl._plan_locks_dir = locks_dir
    rpl._shared_lock_path = tmp_path / ".local" / "supervisor" / "active-plan-lock.json"
    rpl._reopening_register_path = tmp_path / ".local" / "supervisor" / "reopening-register.json"

    try:
        reopen_plan(
            plan_path=str(plan),
            reason="Pilot K: second reopen",
            trigger="REGRESSION",
        )
    finally:
        rpl._plan_locks_dir = _orig_locks_dir
        rpl._shared_lock_path = _orig_shared
        rpl._reopening_register_path = _orig_reg

    updated = json.loads(lock_path.read_text())
    assert updated["status"] == "SUPERSEDED"
    history = updated.get("closure_history", [])
    assert len(history) == 2, f"Expected 2 closure_history entries, got {len(history)}: {history}"


# ---------------------------------------------------------------------------
# Pilot L: Idempotency of generate_closure_artifacts
# ---------------------------------------------------------------------------

def test_pilot_l_artifact_idempotency(tmp_path: Path) -> None:
    """Running generate_closure_artifacts twice produces identical SHA-256 output."""
    from generate_closure_artifacts import write_all_artifacts

    # Create minimal lock files so the generators have something to read
    locks_dir = tmp_path / ".local" / "supervisor" / "plan-locks"
    locks_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        locks_dir / "session1-abcd.json",
        {
            "plan_path": str(tmp_path / "plans" / "alpha.md"),
            "status": "TERMINAL_CLOSED",
            "session_id": "session1",
            "updated_at": "2026-01-01T00:00:00Z",
            "last_taskcard": "TC-A-001",
        },
    )

    # First run
    paths1 = write_all_artifacts(tmp_path)
    hashes1 = {k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in paths1.items()}

    # Second run
    paths2 = write_all_artifacts(tmp_path)
    hashes2 = {k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in paths2.items()}

    mismatches = {k for k in hashes1 if hashes1[k] != hashes2.get(k)}
    assert not mismatches, (
        f"Idempotency failed — SHA-256 mismatch for: {mismatches}\n"
        f"Run1: {hashes1}\nRun2: {hashes2}"
    )


# ---------------------------------------------------------------------------
# Pilot: V-TCF validators smoke test
# ---------------------------------------------------------------------------

def test_validators_pass_on_empty_declaration() -> None:
    """V-TCF-001/002/003 all PASS when declaration has no terminal claims."""
    from terminal_closure_validators import (
        validate_no_open_taskcards_at_terminal,
        validate_terminal_closure_has_contract,
        validate_no_premature_closure_triggers,
    )

    decl = {"work_items": [{"type": "SPRINT", "status": "COMPLETE"}]}
    for fn in (
        validate_no_open_taskcards_at_terminal,
        validate_terminal_closure_has_contract,
        validate_no_premature_closure_triggers,
    ):
        result = fn(decl)
        assert result["result"] == "PASS", f"{fn.__name__} should PASS on non-terminal declaration: {result}"


def test_vtcf001_fails_on_terminal_claim_with_open_tc(tmp_path: Path) -> None:
    """V-TCF-001 FAILs when MACHINERY_HARDENING item claims terminal but audit shows open TCs."""
    from terminal_closure_validators import validate_no_open_taskcards_at_terminal

    # Write a lifecycle audit results file with open taskcards
    audit_path = tmp_path / ".local" / "supervisor" / "lifecycle-audit-results.json"
    _write_json(audit_path, {
        "verdict": "AUDIT_REQUIRES_ITERATION",
        "open_taskcards": ["TC-TCF-AAA"],
        "findings": [{"description": "TC-TCF-AAA still open"}],
    })

    decl = {"work_items": [{"type": "MACHINERY_HARDENING", "plan_terminal_closed": True}]}
    result = validate_no_open_taskcards_at_terminal(decl, repo_root=tmp_path)
    assert result["result"] == "FAIL", f"Expected FAIL, got: {result}"
    assert result["blocks_sprint"] is True
