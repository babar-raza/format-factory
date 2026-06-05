"""
R100 — Continuation State Machine Unit Tests
Tests classify_continuation_state() with all 8 states and priority ordering.
"""
import sys
import tempfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from autonomous_cycle import classify_continuation_state


def _policies_path(force_stop=False):
    """Create a temporary policies file and return its path."""
    content = {
        "autonomous_continuation": {
            "force_stop": force_stop,
            "max_iterations": 12,
        }
    }
    p = Path(tempfile.mktemp(suffix=".yaml"))
    p.write_text(yaml.dump(content), encoding="utf-8")
    return p


def test_yes_state():
    """All accepted, no issues → YES."""
    state = classify_continuation_state(
        auto_continue_value=True,
        at_max_iterations=False,
        hard_stops=[],
        overclaimed=[],
        rework_items=[],
        review={},
        policies_path=_policies_path(),
    )
    assert state == "YES"


def test_yes_with_rework():
    """Rework items but continuation allowed → YES_WITH_REWORK."""
    state = classify_continuation_state(
        auto_continue_value="true_with_rework",
        at_max_iterations=False,
        hard_stops=[],
        overclaimed=[],
        rework_items=["item-1"],
        review={},
        policies_path=_policies_path(),
    )
    assert state == "YES_WITH_REWORK"


def test_no_max_iterations():
    """Max iterations reached → NO_MAX_ITERATIONS."""
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=True,
        hard_stops=["max_iterations_reached"],
        overclaimed=[],
        rework_items=[],
        review={},
        policies_path=_policies_path(),
    )
    assert state == "NO_MAX_ITERATIONS"


def test_no_unsafe_source_state():
    """Overclaimed items → NO_UNSAFE_SOURCE_STATE (highest priority after policy)."""
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=True,  # Also at max, but overclaim has higher priority
        hard_stops=["max_iterations_reached"],
        overclaimed=["item-1"],
        rework_items=[],
        review={},
        policies_path=_policies_path(),
    )
    assert state == "NO_UNSAFE_SOURCE_STATE"


def test_no_broken_baseline():
    """Hard stops (non-iteration) → NO_BROKEN_BASELINE."""
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=False,
        hard_stops=["critical_rework_blocks_continuation"],
        overclaimed=[],
        rework_items=[],
        review={},
        policies_path=_policies_path(),
    )
    assert state == "NO_BROKEN_BASELINE"


def test_no_external_gate():
    """Falsy auto_continue but no other blockers → NO_EXTERNAL_GATE."""
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=False,
        hard_stops=[],
        overclaimed=[],
        rework_items=[],
        review={},
        policies_path=_policies_path(),
    )
    assert state == "NO_EXTERNAL_GATE"


def test_no_policy_block():
    """Policy force_stop → NO_POLICY_BLOCK (highest priority)."""
    state = classify_continuation_state(
        auto_continue_value=True,
        at_max_iterations=False,
        hard_stops=[],
        overclaimed=[],
        rework_items=[],
        review={},
        policies_path=_policies_path(force_stop=True),
    )
    assert state == "NO_POLICY_BLOCK"


def test_priority_overclaim_beats_max_iterations():
    """Overclaimed takes precedence over max_iterations."""
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=True,
        hard_stops=["max_iterations_reached"],
        overclaimed=["item-X"],
        rework_items=[],
        review={},
        policies_path=_policies_path(),
    )
    assert state == "NO_UNSAFE_SOURCE_STATE"


def test_priority_policy_beats_overclaim():
    """Policy block takes precedence over overclaim."""
    state = classify_continuation_state(
        auto_continue_value=False,
        at_max_iterations=False,
        hard_stops=[],
        overclaimed=["item-X"],
        rework_items=[],
        review={},
        policies_path=_policies_path(force_stop=True),
    )
    assert state == "NO_POLICY_BLOCK"


def test_nonexistent_policies_path():
    """Missing policies file doesn't crash, falls through to normal logic."""
    state = classify_continuation_state(
        auto_continue_value=True,
        at_max_iterations=False,
        hard_stops=[],
        overclaimed=[],
        rework_items=[],
        review={},
        policies_path=Path("/nonexistent/policies.yaml"),
    )
    assert state == "YES"


def test_none_policies_path():
    """None policies path doesn't crash."""
    state = classify_continuation_state(
        auto_continue_value=True,
        at_max_iterations=False,
        hard_stops=[],
        overclaimed=[],
        rework_items=[],
        review={},
        policies_path=None,
    )
    assert state == "YES"
