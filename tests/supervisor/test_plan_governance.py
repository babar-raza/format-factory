"""
test_plan_governance.py — Governance tests for plan binding contract, forbidden path
enforcement, and terminal lock semantics.

Tests:
  1. validate_plan_binding_allows_unbound: no lock files → allowed
  2. validate_plan_binding_blocks_forbidden_mutation: binding_contract forbidden_mutation_paths blocks target
  3. snoopy_not_fallback_when_different_plan_active: active lock with forbidden list blocks snoopy
  4. master_plan_memory_raises_value_error_as_active_plan: write_lock raises ValueError for ledger file
  5. terminal_locked_plan_blocks_validate_plan_binding: TERMINAL_CLOSED lock blocks its own active_plan_path
  6. ledger_file_blocked_by_forbidden_guard: guard raises ValueError for master-plan-memory.md
  7. validate_plan_binding_allows_when_no_binding_contract: lock without binding_contract does not block
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

import write_plan_lock as wpl
from write_plan_lock import write_lock, validate_plan_binding, FORBIDDEN_AS_ACTIVE_PLAN


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _patch_dirs(monkeypatch, tmp_path):
    """Redirect lock file paths to tmp_path for isolation."""
    shared = tmp_path / "active-plan-lock.json"
    keyed_dir = tmp_path / "plan-locks"
    keyed_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(wpl, "_shared_lock_path", shared)
    monkeypatch.setattr(wpl, "_plan_locks_dir", keyed_dir)
    return shared, keyed_dir


def _write_raw_lock(keyed_dir: Path, session_id: str, data: dict) -> Path:
    """Write a raw lock file to the keyed dir without calling write_lock()."""
    lf = keyed_dir / f"{session_id}.json"
    lf.write_text(json.dumps(data), encoding="utf-8")
    return lf


# ---------------------------------------------------------------------------
# Test 1: validate_plan_binding allows when no lock dir exists
# ---------------------------------------------------------------------------

def test_validate_plan_binding_allows_unbound(monkeypatch, tmp_path):
    """No lock files present → validate_plan_binding returns (True, 'no_lock_dir')."""
    empty_dir = tmp_path / "plan-locks-nonexistent"
    monkeypatch.setattr(wpl, "_plan_locks_dir", empty_dir)

    allowed, reason = validate_plan_binding("plans/snoopy-juggling-seal.md")
    assert allowed is True
    assert reason == "no_lock_dir"


# ---------------------------------------------------------------------------
# Test 2: validate_plan_binding blocks when target is in forbidden_mutation_paths
# ---------------------------------------------------------------------------

def test_validate_plan_binding_blocks_forbidden_mutation(monkeypatch, tmp_path):
    """Lock with binding_contract.forbidden_mutation_paths blocks the listed target."""
    _, keyed_dir = _patch_dirs(monkeypatch, tmp_path)

    _write_raw_lock(keyed_dir, "session-gov-test-2", {
        "plan_path": "C:/Users/prora/.claude/plans/some-plan.md",
        "status": "IN_PROGRESS",
        "session_id": "session-gov-test-2",
        "binding_contract": {
            "active_plan_path": "C:/Users/prora/.claude/plans/some-plan.md",
            "forbidden_mutation_paths": [
                "plans/snoopy-juggling-seal.md",
                "plans/master-plan-memory.md",
            ],
        },
    })

    allowed, reason = validate_plan_binding("plans/snoopy-juggling-seal.md")
    assert allowed is False
    assert "forbidden_mutation_path" in reason


# ---------------------------------------------------------------------------
# Test 3: snoopy is not a fallback when a different plan is active
# ---------------------------------------------------------------------------

def test_snoopy_not_fallback_when_different_plan_active(monkeypatch, tmp_path):
    """Active plan lock with snoopy in forbidden_mutation_paths must block snoopy writes."""
    _, keyed_dir = _patch_dirs(monkeypatch, tmp_path)

    _write_raw_lock(keyed_dir, "session-gov-test-3", {
        "plan_path": "C:/Users/prora/.claude/plans/other-plan.md",
        "status": "IN_PROGRESS",
        "session_id": "session-gov-test-3",
        "binding_contract": {
            "active_plan_path": "C:/Users/prora/.claude/plans/other-plan.md",
            "forbidden_mutation_paths": [
                "plans/master-plan-memory.md",
                "plans/snoopy-juggling-seal.md",
            ],
        },
    })

    allowed, reason = validate_plan_binding("plans/snoopy-juggling-seal.md", intent="harden")
    assert allowed is False, "snoopy must be blocked when listed in forbidden_mutation_paths"


# ---------------------------------------------------------------------------
# Test 4: master-plan-memory.md raises ValueError as active plan
# ---------------------------------------------------------------------------

def test_master_plan_memory_raises_value_error_as_active_plan(monkeypatch, tmp_path):
    """write_lock with plans/master-plan-memory.md must raise ValueError."""
    _patch_dirs(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match="protected ledger file"):
        write_lock("plans/master-plan-memory.md", session_id="session-gov-test-4")


# ---------------------------------------------------------------------------
# Test 5: TERMINAL_CLOSED lock blocks its own active_plan_path via validate_plan_binding
# ---------------------------------------------------------------------------

def test_terminal_locked_plan_blocks_validate_plan_binding(monkeypatch, tmp_path):
    """TERMINAL_CLOSED lock blocks the plan_path stored in binding_contract.active_plan_path."""
    _, keyed_dir = _patch_dirs(monkeypatch, tmp_path)

    _write_raw_lock(keyed_dir, "session-gov-test-5", {
        "plan_path": "C:/Users/prora/.claude/plans/closed-plan.md",
        "status": "TERMINAL_CLOSED",
        "session_id": "session-gov-test-5",
        "binding_contract": {
            "active_plan_path": "C:/Users/prora/.claude/plans/closed-plan.md",
            "forbidden_mutation_paths": [],
        },
    })

    allowed, reason = validate_plan_binding(
        "C:/Users/prora/.claude/plans/closed-plan.md"
    )
    assert allowed is False
    assert reason == "terminal_closed_plan"


# ---------------------------------------------------------------------------
# Test 6: FORBIDDEN_AS_ACTIVE_PLAN guard: ledger path raises ValueError
# ---------------------------------------------------------------------------

def test_ledger_file_blocked_by_forbidden_guard(monkeypatch, tmp_path):
    """FORBIDDEN_AS_ACTIVE_PLAN constant must list master-plan-memory.md."""
    assert any(
        "master-plan-memory.md" in f for f in FORBIDDEN_AS_ACTIVE_PLAN
    ), "FORBIDDEN_AS_ACTIVE_PLAN must contain master-plan-memory.md"

    _patch_dirs(monkeypatch, tmp_path)
    with pytest.raises(ValueError):
        write_lock("plans/master-plan-memory.md", session_id="session-gov-test-6")


# ---------------------------------------------------------------------------
# Test 7: validate_plan_binding allows when no binding_contract is present
# ---------------------------------------------------------------------------

def test_validate_plan_binding_allows_when_no_binding_contract(monkeypatch, tmp_path):
    """Lock file without binding_contract should not block any path."""
    _, keyed_dir = _patch_dirs(monkeypatch, tmp_path)

    _write_raw_lock(keyed_dir, "session-gov-test-7", {
        "plan_path": "C:/Users/prora/.claude/plans/some-other-plan.md",
        "status": "IN_PROGRESS",
        "session_id": "session-gov-test-7",
        # no binding_contract key
    })

    allowed, reason = validate_plan_binding("plans/snoopy-juggling-seal.md")
    assert allowed is True
    assert reason == "allowed"
