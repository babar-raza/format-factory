"""test_lifecycle_audit_mission_scoping.py — SFC-GAP-D (2026-07-17).

Regression tests proving the closure-oracle mission-scoping fix:
  - determinism: identical repo state -> identical verdict across reruns
  - ambient-noise immunity: another mission's global-state noise does not
    change THIS mission's closure verdict
  - explicit opt-in still sees global noise when mission_id is not passed
  - existing (pre-fix) callers, which never pass mission_id, are unaffected
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
    _scope_rework_items,
    build_closure_contract,
    check_sprint_audit_guard,
    run_lifecycle_audit,
)


def _write_plan(tmp_path: Path, tc_ids: list[str]) -> Path:
    plan = tmp_path / "plan.md"
    rows = "\n".join(f"| {tc} | CLOSED |" for tc in tc_ids)
    plan.write_text(
        "# Test Plan\n\n## Taskcard Status Summary\n\n"
        "| TC-ID | Status |\n|-------|--------|\n" + rows + "\n",
        encoding="utf-8",
    )
    return plan


# ── check_sprint_audit_guard: mission scoping ──────────────────────────────

def test_mismatched_mission_is_info_never_blocks(tmp_path):
    audit_log = tmp_path / "sprint-audit-log.json"
    audit_log.write_text(json.dumps({"mission_id": "OTHER-MISSION"}), encoding="utf-8")
    review = tmp_path / "evidence-review.json"
    review.write_text(json.dumps({"status": "ok"}), encoding="utf-8")

    finding = check_sprint_audit_guard(
        repo_root=tmp_path, audit_log_path=audit_log,
        evidence_review_path=review, mission_id="MY-MISSION")

    assert finding is not None
    assert finding["severity"] == "INFO"
    assert finding["type"] == "SPRINT_AUDIT_NO_SIGNAL_FOR_MISSION"


def test_matching_mission_runs_normal_stale_check(tmp_path):
    audit_log = tmp_path / "sprint-audit-log.json"
    audit_log.write_text(json.dumps({"mission_id": "MY-MISSION"}), encoding="utf-8")
    old_time = time.time() - 120
    import os
    os.utime(str(audit_log), (old_time, old_time))
    review = tmp_path / "evidence-review.json"
    review.write_text(json.dumps({"status": "ok"}), encoding="utf-8")

    finding = check_sprint_audit_guard(
        repo_root=tmp_path, audit_log_path=audit_log,
        evidence_review_path=review, mission_id="MY-MISSION")

    assert finding is not None
    assert finding["severity"] == "MEDIUM"
    assert finding["type"] == "SPRINT_AUDIT_UNCONSUMED"


def test_no_mission_id_preserves_global_behavior(tmp_path):
    """Default (mission_id=None) must behave exactly as before the fix."""
    audit_log = tmp_path / "sprint-audit-log.json"
    audit_log.write_text(json.dumps({"mission_id": "SOME-OTHER-MISSION"}), encoding="utf-8")
    old_time = time.time() - 120
    import os
    os.utime(str(audit_log), (old_time, old_time))
    review = tmp_path / "evidence-review.json"
    review.write_text(json.dumps({"status": "ok"}), encoding="utf-8")

    finding = check_sprint_audit_guard(
        repo_root=tmp_path, audit_log_path=audit_log, evidence_review_path=review)

    # No mission_id passed -> global mtime comparison fires MEDIUM regardless
    # of whose mission wrote the file, matching pre-fix behavior exactly.
    assert finding is not None
    assert finding["severity"] == "MEDIUM"
    assert finding["type"] == "SPRINT_AUDIT_UNCONSUMED"


def test_absent_audit_log_still_critical_regardless_of_mission_id(tmp_path):
    review = tmp_path / "evidence-review.json"
    review.write_text(json.dumps({"status": "ok"}), encoding="utf-8")
    audit_log = tmp_path / "sprint-audit-log.json"  # absent

    finding = check_sprint_audit_guard(
        repo_root=tmp_path, audit_log_path=audit_log,
        evidence_review_path=review, mission_id="MY-MISSION")

    assert finding is not None
    assert finding["severity"] == "CRITICAL"
    assert finding["type"] == "SPRINT_AUDIT_NEVER_RAN"


# ── _scope_rework_items ─────────────────────────────────────────────────────

def test_scope_rework_filters_unrelated_mission():
    items = ["LANE_ENFORCEMENT:1_violations", "rework needed for MY-MISSION"]
    scoped = _scope_rework_items(items, "MY-MISSION", plan_path=None)
    assert "rework needed for MY-MISSION" in scoped
    assert "LANE_ENFORCEMENT:1_violations" not in scoped


def test_scope_rework_keeps_govblock_always():
    items = ["GOV_BLOCK:monolith_detection_validator failing"]
    scoped = _scope_rework_items(items, "MY-MISSION", plan_path=None)
    assert scoped == items


def test_scope_rework_none_mission_id_returns_unchanged():
    items = ["anything", "GOV_BLOCK:x"]
    assert _scope_rework_items(items, None, plan_path=None) == items


def test_scope_rework_matches_own_taskcard_id(tmp_path):
    plan = _write_plan(tmp_path, ["TC-MY-001"])
    items = ["rework needed for TC-MY-001", "unrelated item about TC-OTHER-999"]
    scoped = _scope_rework_items(items, "MY-MISSION", plan_path=plan)
    assert "rework needed for TC-MY-001" in scoped
    assert "unrelated item about TC-OTHER-999" not in scoped


# ── build_closure_contract: ledger_lane_scope visibility ───────────────────

def test_closure_contract_reports_scope_field():
    c_global = build_closure_contract({"rework_items": []}, ledger_lane_scope="global")
    c_mission = build_closure_contract({"rework_items": []}, ledger_lane_scope="mission")
    assert c_global["ledger_lane_scope"] == "global"
    assert c_mission["ledger_lane_scope"] == "mission"


# ── determinism + ambient-noise immunity (full run_lifecycle_audit) ───────

def _seed_signal(path: Path, rework: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "autonomous_continue": True,
        "rework_items": rework,
        "stop_reason": "",
    }), encoding="utf-8")


def test_determinism_two_runs_same_verdict(tmp_path):
    (tmp_path / ".local" / "supervisor").mkdir(parents=True)
    _seed_signal(tmp_path / ".local" / "supervisor" / "continuation-signal.json", [])
    plan = _write_plan(tmp_path, ["TC-MY-001"])

    r1 = run_lifecycle_audit(repo_root=tmp_path, mission_id="MY-MISSION", plan_path=plan)
    r2 = run_lifecycle_audit(repo_root=tmp_path, mission_id="MY-MISSION", plan_path=plan)

    assert r1["verdict"] == r2["verdict"]
    assert r1["closure_contract"].get("closure_authorized") == \
        r2["closure_contract"].get("closure_authorized")


def test_ambient_noise_does_not_change_own_mission_verdict(tmp_path):
    """The exact bug hit live: an unrelated mission's rework item must not
    block a mission whose own taskcards are all closed and who has no rework
    of its own."""
    (tmp_path / ".local" / "supervisor").mkdir(parents=True)
    signal_path = tmp_path / ".local" / "supervisor" / "continuation-signal.json"
    plan = _write_plan(tmp_path, ["TC-MY-001"])

    _seed_signal(signal_path, [])
    r1 = run_lifecycle_audit(repo_root=tmp_path, mission_id="MY-MISSION", plan_path=plan)

    # Inject noise belonging to a DIFFERENT mission between runs.
    _seed_signal(signal_path, ["LANE_ENFORCEMENT:1_violations"])
    r2 = run_lifecycle_audit(repo_root=tmp_path, mission_id="MY-MISSION", plan_path=plan)

    assert r1["closure_contract"].get("all_rework_closed") is True
    assert r2["closure_contract"].get("all_rework_closed") is True, (
        "unrelated mission's rework item must not flip this mission's "
        "all_rework_closed to False"
    )


def test_opt_in_global_scope_still_sees_noise(tmp_path):
    """A plan that explicitly does NOT pass mission_id (global/opt-in scope)
    must still see the raw, unscoped rework list — proving the distinction is
    real, not a no-op flag."""
    (tmp_path / ".local" / "supervisor").mkdir(parents=True)
    signal_path = tmp_path / ".local" / "supervisor" / "continuation-signal.json"
    plan = _write_plan(tmp_path, ["TC-MY-001"])
    _seed_signal(signal_path, ["LANE_ENFORCEMENT:1_violations"])

    r = run_lifecycle_audit(repo_root=tmp_path, mission_id=None, plan_path=plan)

    assert r["closure_contract"]["ledger_lane_scope"] == "global"
    assert r["closure_contract"].get("all_rework_closed") is False
