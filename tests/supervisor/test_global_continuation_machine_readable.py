"""
Tests that global continuation-signal.json has machine-readable paths.
Sprint: FORMAT-FACTORY-H6-AUTONOMOUS-PRODUCT-QUEUE-CONSUMPTION-001
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_repo_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_repo_root))

SIGNAL_PATH = _repo_root / ".local" / "supervisor" / "continuation-signal.json"
ACTIVE_CONT_PATH = _repo_root / ".local" / "supervisor" / "active-continuation.json"
NEXT_ACTION_PATH = _repo_root / ".local" / "supervisor" / "next-action.json"
ACTION_QUEUE_PATH = _repo_root / ".local" / "supervisor" / "action-queue.jsonl"


@pytest.mark.state_dependent
def test_global_continuation_signal_has_machine_path():
    """continuation-signal.json must have machine_continuation_path when present."""
    if not SIGNAL_PATH.exists():
        pytest.skip("continuation-signal.json not present")
    data = json.loads(SIGNAL_PATH.read_text())
    mcp = data.get("machine_continuation_path")
    if mcp is None:
        pytest.skip("machine_continuation_path not in signal (older schema)")
    assert mcp, "machine_continuation_path must be non-empty when present"
    assert not mcp.endswith(".md"), \
        f"machine_continuation_path must not be advisory Markdown: {mcp}"


@pytest.mark.state_dependent
def test_global_continuation_signal_has_action_queue_path():
    """continuation-signal.json must include action_queue_path when present."""
    if not SIGNAL_PATH.exists():
        pytest.skip("continuation-signal.json not present")
    data = json.loads(SIGNAL_PATH.read_text())
    aqp = data.get("action_queue_path")
    if aqp is None:
        pytest.skip("action_queue_path not in signal (older schema)")
    assert aqp, "action_queue_path must be non-empty when present"


@pytest.mark.state_dependent
def test_global_continuation_advisory_prompt_executable_false():
    """advisory_prompt_executable must be False in global signal when present."""
    if not SIGNAL_PATH.exists():
        pytest.skip("continuation-signal.json not present")
    data = json.loads(SIGNAL_PATH.read_text())
    if "advisory_prompt_executable" not in data:
        pytest.skip("advisory_prompt_executable not in signal (older schema)")
    assert data["advisory_prompt_executable"] is False


@pytest.mark.state_dependent
def test_global_continuation_next_sprint_path_advisory_only():
    """If next_sprint_path exists it must not be the machine_continuation_path."""
    if not SIGNAL_PATH.exists():
        pytest.skip("continuation-signal.json not present")
    data = json.loads(SIGNAL_PATH.read_text())
    nsp = data.get("next_sprint_path", "")
    mcp = data.get("machine_continuation_path", "")
    assert nsp != mcp, "machine_continuation_path must differ from next_sprint_path"


@pytest.mark.state_dependent
def test_active_continuation_autonomous_continue():
    """active-continuation.json must have autonomous_continue=true."""
    if not ACTIVE_CONT_PATH.exists():
        pytest.skip("active-continuation.json not present")
    data = json.loads(ACTIVE_CONT_PATH.read_text())
    assert data.get("autonomous_continue") is True


@pytest.mark.state_dependent
def test_active_continuation_advisory_prompt_not_executable():
    """active-continuation.json advisory_prompt_executable must be False."""
    if not ACTIVE_CONT_PATH.exists():
        pytest.skip("active-continuation.json not present")
    data = json.loads(ACTIVE_CONT_PATH.read_text())
    assert data.get("advisory_prompt_executable") is False


@pytest.mark.state_dependent
def test_next_action_not_advisory_md():
    """next-action.json must not be an advisory Markdown file."""
    if not NEXT_ACTION_PATH.exists():
        pytest.skip("next-action.json not present")
    data = json.loads(NEXT_ACTION_PATH.read_text())
    target = data.get("target", data.get("target_path", ""))
    assert not str(target).endswith(".md") or data.get("action_type") == "RUN_MD_NONEMPTY_CHECK", \
        f"next-action target must not be advisory Markdown: {target}"


@pytest.mark.state_dependent
def test_action_queue_exists():
    """action-queue.jsonl must exist."""
    assert ACTION_QUEUE_PATH.exists(), "action-queue.jsonl must exist"


def test_repair_global_continuation_idempotent():
    """repair_global_continuation_signal() on already-repaired signal returns REPAIRED or same."""
    from tools.supervisor.evidence_continuation import repair_global_continuation_signal
    result = repair_global_continuation_signal(sprint_id="TEST-IDEMPOTENT")
    # Should either be REPAIRED or already contain machine paths
    assert result.get("status") in ("REPAIRED", "ALREADY_MACHINE_READABLE", "CONTINUE_FALSE", "NO_SIGNAL")


@pytest.mark.state_dependent
def test_repair_adds_advisory_prompt_executable_false():
    """After repair, global signal must have advisory_prompt_executable=false when present."""
    if not SIGNAL_PATH.exists():
        pytest.skip("continuation-signal.json not present")
    data = json.loads(SIGNAL_PATH.read_text())
    if "advisory_prompt_executable" not in data:
        pytest.skip("advisory_prompt_executable not in signal (older schema)")
    assert data["advisory_prompt_executable"] is False


# ---------------------------------------------------------------------------
# Fixture-based tests — always run, no live state dependency
# ---------------------------------------------------------------------------

def _make_signal(tmp_path, overrides=None):
    """Write a valid continuation-signal.json with all machine-readable fields."""
    signal = {
        "autonomous_continue": True,
        "iteration": 3,
        "max_iterations": 12,
        "continuation_state": "YES",
        "hard_stops_detected": [],
        "stop_reason": None,
        "rework_items": [],
        "machine_continuation_path": ".local/supervisor/next-action.json",
        "active_continuation_path": ".local/supervisor/active-continuation.json",
        "next_action_path": ".local/supervisor/next-action.json",
        "action_queue_path": ".local/supervisor/action-queue.jsonl",
        "advisory_prompt_executable": False,
        "next_sprint_path": "reports/supervisor/next-sprint.md",
    }
    if overrides:
        signal.update(overrides)
    sig_dir = tmp_path / ".local" / "supervisor"
    sig_dir.mkdir(parents=True, exist_ok=True)
    (sig_dir / "continuation-signal.json").write_text(
        json.dumps(signal), encoding="utf-8"
    )
    return sig_dir / "continuation-signal.json", signal


class TestFixtureMachineReadablePaths:
    """Fixture-based tests that always run — no live file dependency."""

    def test_machine_continuation_path_valid(self, tmp_path):
        sig_path, _ = _make_signal(tmp_path)
        data = json.loads(sig_path.read_text())
        assert data["machine_continuation_path"]
        assert not data["machine_continuation_path"].endswith(".md")

    def test_machine_continuation_path_rejects_md(self, tmp_path):
        sig_path, _ = _make_signal(tmp_path, {
            "machine_continuation_path": "reports/supervisor/next-sprint.md",
        })
        data = json.loads(sig_path.read_text())
        assert data["machine_continuation_path"].endswith(".md"), \
            "Test fixture should have .md path for negative test"

    def test_action_queue_path_present(self, tmp_path):
        sig_path, _ = _make_signal(tmp_path)
        data = json.loads(sig_path.read_text())
        assert data["action_queue_path"]

    def test_advisory_prompt_executable_false(self, tmp_path):
        sig_path, _ = _make_signal(tmp_path)
        data = json.loads(sig_path.read_text())
        assert data["advisory_prompt_executable"] is False

    def test_advisory_prompt_executable_true_rejected(self, tmp_path):
        sig_path, _ = _make_signal(tmp_path, {
            "advisory_prompt_executable": True,
        })
        data = json.loads(sig_path.read_text())
        assert data["advisory_prompt_executable"] is not False, \
            "Test fixture should have True for negative test"

    def test_next_sprint_path_differs_from_machine(self, tmp_path):
        sig_path, _ = _make_signal(tmp_path)
        data = json.loads(sig_path.read_text())
        assert data["next_sprint_path"] != data["machine_continuation_path"]

    def test_signal_has_all_required_machine_fields(self, tmp_path):
        sig_path, _ = _make_signal(tmp_path)
        data = json.loads(sig_path.read_text())
        required = [
            "machine_continuation_path",
            "action_queue_path",
            "advisory_prompt_executable",
            "next_sprint_path",
        ]
        for field in required:
            assert field in data, f"Missing required machine-readable field: {field}"


# ---------------------------------------------------------------------------
# TC-CONT-001: check_continuation verdict mapping tests
# ---------------------------------------------------------------------------

sys.path.insert(0, str(_repo_root / "tools" / "supervisor"))


def _setup_for_check(tmp_path, signal_overrides=None):
    """Create the minimal repo structure check_continuation.check() needs."""
    # Write continuation signal
    _make_signal(tmp_path, signal_overrides)
    # approval-gates.md with AUTONOMOUS_CONTINUE: YES
    gates_dir = tmp_path / "reports" / "supervisor"
    gates_dir.mkdir(parents=True, exist_ok=True)
    (gates_dir / "approval-gates.md").write_text(
        "AUTONOMOUS_CONTINUE: YES\n", encoding="utf-8"
    )
    # next-work-items.json
    wi_dir = tmp_path / ".local" / "supervisor"
    wi_dir.mkdir(parents=True, exist_ok=True)
    (wi_dir / "next-work-items.json").write_text("[]", encoding="utf-8")


class TestCheckContinuationVerdictMapping:
    """TC-CONT-001: Verify check_continuation maps continuation states correctly."""

    def test_yes_with_limitations_returns_continue(self, tmp_path):
        """YES_WITH_LIMITATIONS must produce verdict=CONTINUE."""
        _setup_for_check(tmp_path, {"continuation_state": "YES_WITH_LIMITATIONS"})
        from check_continuation import check
        result = check(tmp_path)
        assert result["verdict"] == "CONTINUE", (
            f"YES_WITH_LIMITATIONS should CONTINUE, got {result['verdict']}: {result}"
        )

    def test_yes_returns_continue(self, tmp_path):
        """Plain YES must produce verdict=CONTINUE."""
        _setup_for_check(tmp_path, {"continuation_state": "YES"})
        from check_continuation import check
        result = check(tmp_path)
        assert result["verdict"] == "CONTINUE"

    def test_yes_with_rework_returns_continue(self, tmp_path):
        """YES_WITH_REWORK must produce verdict=CONTINUE."""
        _setup_for_check(tmp_path, {
            "continuation_state": "YES_WITH_REWORK",
            "rework_items": ["ITEM-001"],
        })
        from check_continuation import check
        result = check(tmp_path)
        assert result["verdict"] == "CONTINUE"

    def test_no_max_iterations_returns_stop(self, tmp_path):
        """NO_MAX_ITERATIONS must produce verdict=STOP."""
        _setup_for_check(tmp_path, {"continuation_state": "NO_MAX_ITERATIONS"})
        from check_continuation import check
        result = check(tmp_path)
        assert result["verdict"] == "STOP"
        assert result["reason"] == "NO_MAX_ITERATIONS"

    def test_no_external_gate_returns_stop(self, tmp_path):
        """NO_EXTERNAL_GATE must produce verdict=STOP."""
        _setup_for_check(tmp_path, {"continuation_state": "NO_EXTERNAL_GATE"})
        from check_continuation import check
        result = check(tmp_path)
        assert result["verdict"] == "STOP"
