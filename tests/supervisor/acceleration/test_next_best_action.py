"""Tests for next_best_action.py — R102 Wave 1."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from next_best_action import select_next_actions, select_all_streams, _score_gap


def _gap(stream="mainstream", decision="GOVERNED_SKILL_REQUIRED", work_type="product_source_change",
         priority=100, gap_id="g1", cap="api.save", fmt="FODS", status="NOT_IMPLEMENTED"):
    return {
        "stream": stream,
        "decision": decision,
        "work_type": work_type,
        "priority_score": priority,
        "gap_id": gap_id,
        "capability_path": cap,
        "format": fmt,
        "current_status": status,
    }


def test_select_next_actions_returns_list():
    actions = select_next_actions([_gap()], "mainstream")
    assert isinstance(actions, list)
    assert len(actions) >= 1


def test_select_next_actions_filters_stream():
    gaps = [_gap(stream="mainstream"), _gap(stream="supervisor", gap_id="g2")]
    actions = select_next_actions(gaps, "mainstream")
    targets = [a["target"] for a in actions if a["action_type"] != "run_package_proof"]
    assert "g1" in targets
    assert "g2" not in targets


def test_select_next_actions_handoff_type():
    gaps = [_gap(decision="GOVERNED_HANDOFF_REQUIRED")]
    actions = select_next_actions(gaps, "mainstream")
    handoff_actions = [a for a in actions if a["action_type"] == "generate_handoff"]
    assert len(handoff_actions) >= 1


def test_select_next_actions_anti_skip_violation():
    """Positive: lanes without raw_log_path trigger anti-skip action."""
    gaps = [_gap()]
    ledger = {"lanes": [{"status": "completed", "raw_log_path": ""}]}
    actions = select_next_actions(gaps, "mainstream", ledger)
    violations = [a for a in actions if a["action_type"] == "fix_anti_skip_violation"]
    assert len(violations) >= 1


def test_select_next_actions_no_anti_skip_violation():
    """Negative: lanes with raw_log_path don't trigger anti-skip."""
    gaps = [_gap()]
    ledger = {"lanes": [{"status": "completed", "raw_log_path": "/tmp/log.txt"}]}
    actions = select_next_actions(gaps, "mainstream", ledger)
    violations = [a for a in actions if a["action_type"] == "fix_anti_skip_violation"]
    assert len(violations) == 0


def test_select_all_streams_has_all_four():
    result = select_all_streams([_gap()])
    assert "mainstream" in result
    assert "acceleration" in result
    assert "skills" in result
    assert "supervisor" in result


def test_score_gap_handoff_higher():
    handoff = _gap(decision="GOVERNED_HANDOFF_REQUIRED", priority=100)
    skill = _gap(decision="GOVERNED_SKILL_REQUIRED", priority=100)
    assert _score_gap(handoff) > _score_gap(skill)


def test_max_actions_limit():
    gaps = [_gap(gap_id=f"g{i}") for i in range(20)]
    actions = select_next_actions(gaps, "mainstream", max_actions=3)
    assert len(actions) <= 3


def test_acceleration_stream_has_expand_skill():
    actions = select_next_actions([], "acceleration")
    types = [a["action_type"] for a in actions]
    assert "expand_skill_registry" in types
