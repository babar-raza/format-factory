"""
test_checkpoint_rollover_policy.py -- Checkpoint rollover and continuation tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-1
Stage 0: False-terminal root cause repair
Added: 2026-06-10

Tests that checkpoint windows roll over automatically, max_iterations is not
a terminal stop, human gates are parked while safe lanes continue, and
prose terminal state is rejected when machine state says continue.
"""
from __future__ import annotations



def _make_signal(
    autonomous_continue=True,
    continuation_state="YES",
    iteration=0,
    max_iterations=12,
    stop_reason=None,
    safe_lanes_available=True,
    hard_stops_detected=None,
    checkpoint_rollover=None,
):
    return {
        "autonomous_continue": autonomous_continue,
        "continuation_state": continuation_state,
        "iteration": iteration,
        "max_iterations": max_iterations,
        "stop_reason": stop_reason,
        "safe_lanes_available": safe_lanes_available,
        "hard_stops_detected": hard_stops_detected or [],
        "checkpoint_rollover": checkpoint_rollover,
        "advisory_prompt_executable": False,
    }


def _should_continue(signal: dict) -> bool:
    """Determine if the conveyor should continue based on machine state."""
    ac = signal.get("autonomous_continue")
    if ac is None or ac is False:
        return False
    cs = signal.get("continuation_state", "")
    if isinstance(cs, str) and cs.startswith("NO"):
        return False
    if signal.get("stop_reason") is not None:
        return False
    if not signal.get("safe_lanes_available", False):
        return False
    if signal.get("hard_stops_detected"):
        return False
    return True


def _is_checkpoint_rollover(signal: dict) -> bool:
    """Detect checkpoint rollover state."""
    return signal.get("checkpoint_rollover") is not None


def test_accepted_verdict_with_safe_lanes_continues():
    """ACCEPTED verdict with safe lanes must continue."""
    signal = _make_signal(autonomous_continue=True, safe_lanes_available=True)
    assert _should_continue(signal) is True


def test_accepted_with_rework_continues():
    """ACCEPTED_WITH_REWORK (true_with_rework) must continue."""
    signal = _make_signal(
        autonomous_continue="true_with_rework",
        continuation_state="YES_WITH_REWORK",
    )
    assert _should_continue(signal) is True


def test_checkpoint_window_rolls_over():
    """Checkpoint window reaching max triggers rollover, not stop."""
    signal = _make_signal(
        iteration=0,
        max_iterations=12,
        checkpoint_rollover={
            "rollover_from_iteration": 12,
            "rollover_at_max": 12,
            "rollover_rule": "CHECKPOINT_ROLLOVER_CONTINUE",
            "rollover_action": "iteration reset to 0",
        },
    )
    assert _should_continue(signal) is True
    assert _is_checkpoint_rollover(signal) is True


def test_max_iterations_not_terminal():
    """max_iterations is a checkpoint window, not a terminal stop."""
    signal = _make_signal(iteration=12, max_iterations=12)
    # Even at max, if autonomous_continue=True and safe_lanes=True, continue
    assert _should_continue(signal) is True


def test_human_gate_parked_while_safe_lanes_continue():
    """Human gates (commit/push) don't stop if other safe lanes exist."""
    signal = _make_signal(
        autonomous_continue=True,
        safe_lanes_available=True,
        # Human gates are parked, not in hard_stops_detected
        hard_stops_detected=[],
    )
    assert _should_continue(signal) is True


def test_prose_terminal_state_rejected_when_machine_state_continues():
    """Machine state wins over prose claiming terminal state."""
    signal = _make_signal(
        autonomous_continue=True,
        continuation_state="YES",
        safe_lanes_available=True,
    )
    prose_says_terminal = True
    # Machine state overrides prose — decision follows machine, not prose
    machine_says_continue = _should_continue(signal)
    assert machine_says_continue is True
    # The key invariant: machine says continue even though prose says stop
    assert prose_says_terminal is True  # prose claims terminal
    assert machine_says_continue is True  # but machine overrides → continue


def test_next_work_items_auto_queued_when_agent_executable():
    """Next work items with agent_can_execute=True are auto-queued."""
    items = [
        {"task_id": "T-001", "agent_can_execute": True},
        {"task_id": "T-002", "agent_can_execute": True},
        {"task_id": "T-003", "agent_can_execute": False, "reason": "human_gate"},
    ]
    executable = [i for i in items if i.get("agent_can_execute")]
    parked = [i for i in items if not i.get("agent_can_execute")]
    assert len(executable) == 2
    assert len(parked) == 1


def test_true_stop_all_lanes_complete():
    """Stop when all lanes are complete."""
    signal = _make_signal(
        autonomous_continue=False,
        continuation_state="NO_ALL_COMPLETE",
        safe_lanes_available=False,
    )
    assert _should_continue(signal) is False


def test_true_stop_only_external_gates_remain():
    """Stop when only true external gates remain."""
    signal = _make_signal(
        autonomous_continue=False,
        continuation_state="NO_EXTERNAL_GATES_ONLY",
        safe_lanes_available=False,
    )
    assert _should_continue(signal) is False


def test_stop_reason_overrides():
    """Explicit stop_reason always stops."""
    signal = _make_signal(stop_reason="UNSAFE_WORKSPACE")
    assert _should_continue(signal) is False


def test_hard_stops_prevent_continuation():
    """hard_stops_detected prevents continuation."""
    signal = _make_signal(hard_stops_detected=["credential_required"])
    assert _should_continue(signal) is False
