"""test_sprint_executor_structural_govblock.py — TC-EXT-010-06

Proves the override loophole closed by TC-EXT-010-02 in
tools/supervisor/sprint_executor.py: the headless run-loop must HALT (not
silently proceed) when check_continuation.py returns
verdict=STOP, reason=structural_govblock_must_be_resolved_first — even though
this reason is deliberately NOT classified as a TRUE_EXTERNAL_GATE.

Background (see CLAUDE.md "GOV_BLOCK Exception", tools/supervisor/
check_continuation.py "Check 8" (TC-GOVBLK-001), and
tools/supervisor/governance_block_registry.py):

  - check_continuation.py's Check 8 + governance_block_registry.py's
    filter_structural_blocks() ALREADY correctly detect a structural GOV_BLOCK
    in `rework_items` and return verdict=STOP,
    reason="structural_govblock_must_be_resolved_first". This detection logic
    is out of scope for this taskcard (already correct, not modified here).

  - BEFORE TC-EXT-010-02, sprint_executor.py's _is_external_gate() returned
    False for this reason (correctly — it is NOT a TRUE_EXTERNAL_GATE, the
    agent CAN resolve it autonomously). Because _is_external_gate() was the
    ONLY halt check in the run-loop, the loop fell through to the generic
    Supreme-Directive override branch and proceeded to run the next sprint
    anyway. That silent-proceed behavior is the loophole TC-EXT-010 closes.

  - TC-EXT-010-02 adds a second, independent predicate
    (_is_structural_govblock_stop()) and an elif branch in cmd_run_loop() that
    halts (return 1) for this specific reason WITHOUT reclassifying it as a
    TRUE_EXTERNAL_GATE.

These tests drive the REAL cmd_run_loop() control flow in-process (not via
subprocess) so the assertions exercise the actual patched code, not a
reimplementation of it. The MissionLock acquisition is force-failed via a
monkeypatched _get_session_id() BEFORE it can touch the real sqlite lock DB —
this is required so the test cannot interfere with the independent autonomous
process that may be running against this same repository (see TC-EXT-010 task
background); real subprocess calls to check_continuation.py / claude CLI /
autonomous_cycle.py are avoided the same way.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor import sprint_executor


# ---------------------------------------------------------------------------
# Unit tests: the two predicate functions in isolation
# ---------------------------------------------------------------------------

def test_is_structural_govblock_stop_true_for_check8_reason():
    assert sprint_executor._is_structural_govblock_stop(
        "structural_govblock_must_be_resolved_first"
    ) is True


def test_is_structural_govblock_stop_case_insensitive():
    assert sprint_executor._is_structural_govblock_stop(
        "STRUCTURAL_GOVBLOCK_MUST_BE_RESOLVED_FIRST"
    ) is True


def test_is_structural_govblock_stop_false_for_empty():
    assert sprint_executor._is_structural_govblock_stop("") is False


def test_is_structural_govblock_stop_false_for_unrelated_reason():
    assert sprint_executor._is_structural_govblock_stop("MAX_ITERATIONS") is False
    assert sprint_executor._is_structural_govblock_stop("APPROVAL_GATE_NO") is False


def test_is_external_gate_does_not_classify_structural_govblock_as_external():
    """Documents the deliberate distinction from CLAUDE.md's GOV_BLOCK Exception:
    structural GOV_BLOCK is non-overridable but explicitly NOT a
    TRUE_EXTERNAL_GATE. Both predicates must agree on this split — if this ever
    flips to True, _is_structural_govblock_stop() becomes redundant dead code
    and the two classifications have silently merged.
    """
    assert sprint_executor._is_external_gate(
        "structural_govblock_must_be_resolved_first"
    ) is False


# ---------------------------------------------------------------------------
# Integration-style proof: cmd_run_loop() actually halts, does not run a sprint
# ---------------------------------------------------------------------------

def _patch_no_mission_lock(monkeypatch):
    # Force the MissionLock acquisition try-block in cmd_run_loop() to fail
    # with a plain Exception (NOT MissionLockConflict) before it ever
    # constructs MissionLock or touches the real sqlite lock DB. This must
    # not interfere with any concurrent controller holding the real lock.
    def _raise(*_a, **_kw):
        raise RuntimeError("test-forced-no-mission-lock")
    monkeypatch.setattr(sprint_executor, "_get_session_id", _raise)


class TestRunLoopHaltsOnStructuralGovBlock:
    def test_halts_and_does_not_invoke_run_sprint(self, monkeypatch):
        """Simulates a rework_items payload containing a structural GOV_BLOCK
        entry (as check_continuation.py's Check 8 would emit) and proves
        cmd_run_loop() halts with exit 1 WITHOUT proceeding to run a sprint.
        """
        _patch_no_mission_lock(monkeypatch)

        structural_cont = {
            "verdict": "STOP",
            "reason": "structural_govblock_must_be_resolved_first",
            "rework_items": ["GOV_BLOCK:monolith_detection_validator [fods]"],
            "_exit_code": 1,
        }
        monkeypatch.setattr(
            sprint_executor, "_check_continuation",
            lambda repo_root: dict(structural_cont),
        )

        sprint_calls = []

        def _spy_run_sprint(sprint_id, repo_root, dry_run=False):
            sprint_calls.append(sprint_id)
            return {"exit_code": 0}

        monkeypatch.setattr(sprint_executor, "cmd_run_sprint", _spy_run_sprint)

        exit_code = sprint_executor.cmd_run_loop(_REPO, max_cycles=3, dry_run=True)

        assert exit_code == 1, (
            "cmd_run_loop must halt (exit 1) on "
            "structural_govblock_must_be_resolved_first, not override and continue"
        )
        assert sprint_calls == [], (
            "cmd_run_loop must NOT proceed to run a sprint after a structural "
            f"GOV_BLOCK stop — but cmd_run_sprint was called for: {sprint_calls}"
        )

    def test_external_gate_still_halts_too(self, monkeypatch):
        """Regression guard: the new elif branch must not disturb the
        pre-existing TRUE_EXTERNAL_GATE halt behavior."""
        _patch_no_mission_lock(monkeypatch)
        gate_cont = {"verdict": "STOP", "reason": "GATE_11_APPROVAL", "rework_items": []}
        monkeypatch.setattr(
            sprint_executor, "_check_continuation", lambda repo_root: dict(gate_cont)
        )
        sprint_calls = []
        monkeypatch.setattr(
            sprint_executor, "cmd_run_sprint",
            lambda *a, **kw: sprint_calls.append(a) or {"exit_code": 0},
        )

        exit_code = sprint_executor.cmd_run_loop(_REPO, max_cycles=3, dry_run=True)

        assert exit_code == 1
        assert sprint_calls == []

    def test_ordinary_stop_reason_still_overrides_and_proceeds(self, monkeypatch):
        """Regression guard: ordinary OVERRIDABLE STOP reasons (e.g.
        APPROVAL_GATE_NO) must still fall through to the Supreme-Directive
        override branch and actually proceed to run a sprint — proves the new
        halt is scoped ONLY to the structural GOV_BLOCK reason, not a
        blanket new stop for every STOP verdict.
        """
        import pytest

        next_sprint_path = _REPO / "reports" / "supervisor" / "next-sprint.md"
        if not next_sprint_path.exists():
            pytest.skip("reports/supervisor/next-sprint.md not present in this checkout")

        _patch_no_mission_lock(monkeypatch)
        ordinary_cont = {
            "verdict": "STOP",
            "reason": "APPROVAL_GATE_NO",
            "rework_items": [],
            "iteration": 0,
            "max_iterations": 12,
        }
        monkeypatch.setattr(
            sprint_executor, "_check_continuation", lambda repo_root: dict(ordinary_cont)
        )
        sprint_calls = []

        def _spy_run_sprint(sprint_id, repo_root, dry_run=False):
            sprint_calls.append(sprint_id)
            return {"exit_code": 0}

        monkeypatch.setattr(sprint_executor, "cmd_run_sprint", _spy_run_sprint)

        exit_code = sprint_executor.cmd_run_loop(_REPO, max_cycles=1, dry_run=True)

        assert sprint_calls != [], (
            "Ordinary overridable STOP reasons must still proceed to run a "
            "sprint (Supreme Directive override) — this guards against the fix "
            "over-broadly blocking non-structural stops."
        )
        assert exit_code == 0
