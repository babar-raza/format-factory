"""
Tests for tools/supervisor/check_continuation.py
Validates the deterministic 7-condition continuation check.
"""
import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from tools.supervisor.check_continuation import check, main


def _write_signal(tmp_path, overrides=None):
    """Write a valid continuation-signal.json with optional overrides."""
    signal = {
        "autonomous_continue": True,
        "iteration": 3,
        "max_iterations": 12,
        "continuation_state": "YES",
        "hard_stops_detected": [],
        "stop_reason": None,
        "rework_items": [],
    }
    if overrides:
        signal.update(overrides)
    sig_dir = tmp_path / ".local" / "supervisor"
    sig_dir.mkdir(parents=True, exist_ok=True)
    (sig_dir / "continuation-signal.json").write_text(
        json.dumps(signal), encoding="utf-8"
    )
    return signal


def _write_gates(tmp_path, content="AUTONOMOUS_CONTINUE: YES"):
    """Write approval-gates.md."""
    gates_dir = tmp_path / "reports" / "supervisor"
    gates_dir.mkdir(parents=True, exist_ok=True)
    (gates_dir / "approval-gates.md").write_text(content, encoding="utf-8")


def _write_work_items(tmp_path):
    """Write canonical next-work-items.json."""
    wi_dir = tmp_path / ".local" / "supervisor"
    wi_dir.mkdir(parents=True, exist_ok=True)
    (wi_dir / "next-work-items.json").write_text(
        json.dumps({"items": [{"item_id": "T1", "title": "Test"}]}),
        encoding="utf-8",
    )


def _setup_all(tmp_path, signal_overrides=None):
    """Set up all files for a passing check."""
    _write_signal(tmp_path, signal_overrides)
    _write_gates(tmp_path)
    _write_work_items(tmp_path)


# ── All conditions pass ──────────────────────────────────────────────────

def test_all_pass(tmp_path):
    _setup_all(tmp_path)
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"
    assert result["next_work_items_path"] == ".local/supervisor/next-work-items.json"
    assert result["resume_command"] is not None


def test_all_pass_with_rework(tmp_path):
    _setup_all(tmp_path, {"continuation_state": "YES_WITH_REWORK", "rework_items": ["R1"]})
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"
    assert result["rework_items"] == ["R1"]


def test_all_pass_with_limitations(tmp_path):
    _setup_all(tmp_path, {"continuation_state": "YES_WITH_LIMITATIONS"})
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"


# ── Check 1: Missing signal ─────────────────────────────────────────────

def test_missing_signal(tmp_path):
    _write_gates(tmp_path)
    _write_work_items(tmp_path)
    result = check(tmp_path)
    assert result["verdict"] == "STOP"
    assert result["reason"] == "NO_SIGNAL"


def test_invalid_signal_json(tmp_path):
    sig_dir = tmp_path / ".local" / "supervisor"
    sig_dir.mkdir(parents=True, exist_ok=True)
    (sig_dir / "continuation-signal.json").write_text("not json", encoding="utf-8")
    result = check(tmp_path)
    assert result["verdict"] == "STOP"
    assert result["reason"] == "INVALID_SIGNAL"


# ── Check 2: autonomous_continue false ───────────────────────────────────

def test_autonomous_continue_false(tmp_path):
    """When autonomous_continue=False AND gates also say NO, STOP."""
    _setup_all(tmp_path, {"autonomous_continue": False, "stop_reason": "test_reason",
                           "continuation_state": "NO_HARD_STOP"})
    _write_gates(tmp_path, "AUTONOMOUS_CONTINUE: NO")
    result = check(tmp_path)
    assert result["verdict"] == "STOP"
    assert result["reason"] == "AUTONOMOUS_CONTINUE_FALSE"
    assert "test_reason" in result["detail"]


def test_autonomous_continue_false_gates_override(tmp_path):
    """When autonomous_continue=False BUT gates say YES, gates override → CONTINUE."""
    _setup_all(tmp_path, {"autonomous_continue": False, "stop_reason": "test_reason"})
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"


# ── Check 3: continuation_state starts with NO_ ─────────────────────────

def test_continuation_state_no(tmp_path):
    _setup_all(tmp_path, {"continuation_state": "NO_BROKEN_BASELINE"})
    result = check(tmp_path)
    assert result["verdict"] == "STOP"
    assert result["reason"] == "NO_BROKEN_BASELINE"


def test_continuation_state_no_max_iterations(tmp_path):
    _setup_all(tmp_path, {"continuation_state": "NO_MAX_ITERATIONS"})
    result = check(tmp_path)
    assert result["verdict"] == "STOP"
    assert result["reason"] == "NO_MAX_ITERATIONS"


# ── Check 4: hard_stops_detected non-empty ───────────────────────────────

def test_hard_stops_detected(tmp_path):
    _setup_all(tmp_path, {"hard_stops_detected": ["critical_rework_blocks_continuation"]})
    result = check(tmp_path)
    assert result["verdict"] == "STOP"
    assert result["reason"] == "HARD_STOP"


# ── Check 5: iteration >= max_iterations ─────────────────────────────────

def test_max_iterations_reached(tmp_path):
    """TC-PROD-H-003R: max_iterations triggers auto-rollover, not STOP."""
    _setup_all(tmp_path, {"iteration": 12, "max_iterations": 12})
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"
    sig = json.loads(
        (tmp_path / ".local" / "supervisor" / "continuation-signal.json").read_text()
    )
    assert sig["iteration"] == 0, "iteration should reset to 0 after auto-rollover"


def test_iteration_below_max(tmp_path):
    _setup_all(tmp_path, {"iteration": 11, "max_iterations": 12})
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"


# ── Check 6: approval-gates.md ───────────────────────────────────────────

def test_missing_gates(tmp_path):
    _write_signal(tmp_path)
    _write_work_items(tmp_path)
    result = check(tmp_path)
    assert result["verdict"] == "STOP"
    assert result["reason"] == "APPROVAL_GATE_MISSING"


def test_gates_without_yes(tmp_path):
    """TC-PROD-H-012: gates=NO + signal=NO → STOP."""
    _setup_all(tmp_path, {"continuation_state": "NO_HARD_STOP"})
    _write_gates(tmp_path, "AUTONOMOUS_CONTINUE: NO — repair required first")
    result = check(tmp_path)
    assert result["verdict"] == "STOP"


# ── Check 7: next-work-items.json ────────────────────────────────────────

def test_missing_work_items(tmp_path):
    _write_signal(tmp_path)
    _write_gates(tmp_path)
    result = check(tmp_path)
    assert result["verdict"] == "STOP"
    assert result["reason"] == "NO_WORK_ITEMS"


# ── Evidence continuation failure warning ────────────────────────────────

def test_evidence_continuation_warning(tmp_path):
    _setup_all(tmp_path, {
        "evidence_continuation_failed": True,
        "evidence_continuation_error": "import error",
    })
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"
    assert "warning" in result
    assert "import error" in result["warning"]


def test_evidence_continuation_fallback_path(tmp_path):
    """TC-VERI-002: Full fallback — evidence_continuation fails but continuation
    still works via canonical next-work-items.json."""
    _setup_all(tmp_path, {
        "evidence_continuation_failed": True,
        "evidence_continuation_error": "ModuleNotFoundError: No module named 'evidence_continuation'",
    })
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"
    assert "warning" in result
    assert "ModuleNotFoundError" in result["warning"]
    # Verify canonical next-work-items.json is what the agent would use
    wi_path = tmp_path / ".local" / "supervisor" / "next-work-items.json"
    assert wi_path.exists()
    assert result["next_work_items_path"] == ".local/supervisor/next-work-items.json"


# ── Idempotency ─────────────────────────────────────────────────────────

def test_idempotent(tmp_path):
    _setup_all(tmp_path)
    r1 = check(tmp_path)
    r2 = check(tmp_path)
    assert r1["verdict"] == r2["verdict"]
    assert r1["iteration"] == r2["iteration"]
    assert r1["next_work_items_path"] == r2["next_work_items_path"]


# ── CLI exit code ────────────────────────────────────────────────────────

def test_main_exit_0(tmp_path):
    _setup_all(tmp_path)
    code = main(["--repo-root", str(tmp_path)])
    assert code == 0


def test_main_exit_1(tmp_path):
    code = main(["--repo-root", str(tmp_path)])
    assert code == 1


# ── true_with_rework is truthy ───────────────────────────────────────────

def test_true_with_rework_is_truthy(tmp_path):
    _setup_all(tmp_path, {"autonomous_continue": "true_with_rework"})
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"


# ── TC-PROD-H-080: Auto-rollover regression (Check 5) ─────────────────

def test_max_iterations_auto_rollover(tmp_path):
    """When iteration >= max_iterations, auto-rollover resets to 0 and continues."""
    _setup_all(tmp_path, {"iteration": 12, "max_iterations": 12})
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE", (
        f"Expected CONTINUE after auto-rollover, got {result['verdict']} "
        f"reason={result.get('reason')}"
    )
    # Verify signal file was updated
    sig = json.loads(
        (tmp_path / ".local" / "supervisor" / "continuation-signal.json").read_text()
    )
    assert sig["iteration"] == 0, f"iteration should be 0 after rollover, got {sig['iteration']}"


def test_max_iterations_rollover_beyond(tmp_path):
    """When iteration > max_iterations, auto-rollover still fires."""
    _setup_all(tmp_path, {"iteration": 15, "max_iterations": 12})
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"
    sig = json.loads(
        (tmp_path / ".local" / "supervisor" / "continuation-signal.json").read_text()
    )
    assert sig["iteration"] == 0


def test_iteration_rollover_preserves_concurrent_signal_update(tmp_path, monkeypatch):
    """TC-MACH-006 regression: `signal` is read once at the top of check(), then
    many I/O operations happen before the iteration-rollover write. Previously
    that write wrote back the ENTIRE stale in-memory `signal` dict (only
    `iteration` changed), silently clobbering any field a concurrent agent
    updated in continuation-signal.json during that window (AGENTS.md Section
    CO — concurrent agents are the normal state, not an edge case). The fix
    re-reads the file fresh immediately before writing and merges only
    `iteration`. Simulate the race by mutating the on-disk file the moment the
    rollover re-read happens, and assert that mutation survives the write.
    """
    _setup_all(tmp_path, {"iteration": 12, "max_iterations": 12})
    signal_path = tmp_path / ".local" / "supervisor" / "continuation-signal.json"

    _orig_read_text = Path.read_text
    _state = {"injected": False}

    def _patched_read_text(self, *a, **kw):
        text = _orig_read_text(self, *a, **kw)
        if self == signal_path and not _state["injected"]:
            _state["injected"] = True
            # Simulate a concurrent writer updating the signal file in the
            # window between check()'s initial read and the rollover re-read.
            concurrent = json.loads(text)
            concurrent["injected_by_concurrent_writer"] = True
            self.write_text(json.dumps(concurrent), encoding="utf-8")
            return _orig_read_text(self, *a, **kw)
        return text

    monkeypatch.setattr(Path, "read_text", _patched_read_text)

    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"

    final = json.loads(signal_path.read_text(encoding="utf-8"))
    assert final["iteration"] == 0, "iteration should have rolled over to 0"
    assert final.get("injected_by_concurrent_writer") is True, (
        "TC-MACH-006 regression: rollover write clobbered a concurrent update "
        "made between the initial signal read and the rollover write"
    )


# ── TC-PROD-H-081: Staleness detector regression (Check 6) ────────────

def test_stale_gates_no_but_signal_yes_continues(tmp_path):
    """Stale gates (NO) + live signal (YES_*) should CONTINUE with warning."""
    _setup_all(tmp_path, {"continuation_state": "YES_RESET_CLEAN"})
    _write_gates(tmp_path, "AUTONOMOUS_CONTINUE: NO")
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE", (
        f"Expected CONTINUE (stale gates overridden by signal), got {result['verdict']} "
        f"reason={result.get('reason')}"
    )


def test_real_gates_no_and_signal_no_stops(tmp_path):
    """Real gates (NO) + real signal (NO_*) should STOP."""
    _setup_all(tmp_path, {"continuation_state": "NO_HARD_STOP"})
    _write_gates(tmp_path, "AUTONOMOUS_CONTINUE: NO")
    result = check(tmp_path)
    assert result["verdict"] == "STOP"


def test_gates_yes_signal_yes_continues(tmp_path):
    """Both gates and signal agree YES — normal continue path."""
    _setup_all(tmp_path, {"continuation_state": "YES_RESET_CLEAN"})
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"


# ── TC-SPW-003B: Check 2d — blocking gap gate ─────────────────────────

def _write_gap_ledger(tmp_path, gaps: list) -> None:
    """Write product-code-gap-ledger.yaml with the given gap list."""
    import yaml
    ledger_dir = tmp_path / "reports" / "product-quality"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    (ledger_dir / "product-code-gap-ledger.yaml").write_text(
        yaml.dump({"gaps": gaps}),
        encoding="utf-8",
    )


def test_blocking_gap_stops_when_format_in_scope(tmp_path):
    """Check 2d: BLOCKING+OPEN+confirmed gap for targeted format → STOP."""
    _setup_all(tmp_path, {"format_targets": ["fods"]})
    _write_gap_ledger(tmp_path, [{
        "gap_id": "PCG-006",
        "product": "fods",
        "severity": "blocking",
        "status": "OPEN",
        "severity_confirmed": True,
    }])
    result = check(tmp_path)
    assert result["verdict"] == "STOP"
    assert result.get("reason") == "blocking_gap_unresolved"
    assert "PCG-006" in result.get("blocking_gaps", [])


def test_blocking_gap_passes_when_format_not_in_scope(tmp_path):
    """Check 2d: BLOCKING gap for a format NOT in format_targets → CONTINUE."""
    _setup_all(tmp_path, {"format_targets": ["fodt"]})  # fods gap, not fodt
    _write_gap_ledger(tmp_path, [{
        "gap_id": "PCG-006",
        "product": "fods",
        "severity": "blocking",
        "status": "OPEN",
        "severity_confirmed": True,
    }])
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"


def test_blocking_gap_passes_when_no_format_targets(tmp_path):
    """Check 2d: No format_targets in signal → gap gate skips (non-blocking)."""
    _setup_all(tmp_path)  # no format_targets
    _write_gap_ledger(tmp_path, [{
        "gap_id": "PCG-006",
        "product": "fods",
        "severity": "blocking",
        "status": "OPEN",
        "severity_confirmed": True,
    }])
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"


def test_open_but_unconfirmed_gap_does_not_stop(tmp_path):
    """Check 2d: BLOCKING+OPEN but severity_confirmed=False → does NOT trigger stop."""
    _setup_all(tmp_path, {"format_targets": ["fods"]})
    _write_gap_ledger(tmp_path, [{
        "gap_id": "PCG-NEW",
        "product": "fods",
        "severity": "blocking",
        "status": "OPEN",
        "severity_confirmed": False,  # not confirmed
    }])
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"


def test_closed_blocking_gap_does_not_stop(tmp_path):
    """Check 2d: BLOCKING but CLOSED gap → does NOT trigger stop."""
    _setup_all(tmp_path, {"format_targets": ["fods"]})
    _write_gap_ledger(tmp_path, [{
        "gap_id": "PCG-OLD",
        "product": "fods",
        "severity": "blocking",
        "status": "CLOSED",
        "severity_confirmed": True,
    }])
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"


def test_no_gap_ledger_does_not_stop(tmp_path):
    """Check 2d: No product-code-gap-ledger.yaml → non-blocking, CONTINUE."""
    _setup_all(tmp_path, {"format_targets": ["fods"]})
    # Deliberately do NOT write a gap ledger
    result = check(tmp_path)
    assert result["verdict"] == "CONTINUE"


# ── TC-MACH-004: fail-closed on malformed gate-states.yaml / gap ledger ──

def test_malformed_gap_ledger_fails_closed(tmp_path):
    """TC-MACH-004: a gap ledger that EXISTS but fails to parse must STOP
    (fail closed), not silently warn-and-CONTINUE. Previously this only
    printed a WARNING to stderr and fell through to CONTINUE — a malformed
    ledger (plausible under concurrent writes from other agents, see
    AGENTS.md Section CO) would silently disable the BLOCKING-gap gate.
    """
    _setup_all(tmp_path, {"format_targets": ["fods"]})
    ledger_dir = tmp_path / "reports" / "product-quality"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    (ledger_dir / "product-code-gap-ledger.yaml").write_text(
        "gaps: [unterminated: [oops\n", encoding="utf-8"
    )
    result = check(tmp_path)
    assert result["verdict"] == "STOP"
    assert result.get("reason") == "gap_ledger_unreadable"


def test_malformed_gate_states_fails_closed(tmp_path):
    """TC-MACH-004: gate-states.yaml that EXISTS but fails to parse must STOP
    (fail closed), matching ACTIVE_PLAN_LOCK_CORRUPT's posture, rather than
    silently skipping Check 11's TRUE_EXTERNAL_GATE (Gate 11 authorization).
    """
    _setup_all(tmp_path)
    registry_dir = tmp_path / "registry"
    registry_dir.mkdir(parents=True, exist_ok=True)
    (registry_dir / "gate-states.yaml").write_text(
        "format_gate_states: [unterminated: [oops\n", encoding="utf-8"
    )
    result = check(tmp_path)
    assert result["verdict"] == "STOP"
    assert result.get("reason") == "gate_11_state_unreadable"
