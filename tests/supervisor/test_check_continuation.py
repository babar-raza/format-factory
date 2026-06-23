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
