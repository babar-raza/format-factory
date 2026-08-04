"""Tests for the FF6 goal-driven continuation actuator.

The property under test is not "does it print nicely" but "can it stop for the
wrong reason". The generic actuator (``check_continuation.py``) currently
returns STOP/SESSION_MISMATCH against a signal from 2026-07-16 because it is
signal-derived. These tests pin that the goal driver cannot fail that way.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from tools.ff6 import goal_driver as gd


@pytest.fixture
def mission(tmp_path: Path) -> dict[str, Path]:
    """A self-contained mission: 2 products, neither certified."""
    goal = tmp_path / "product-goal.yaml"
    goal.write_text(
        yaml.safe_dump(
            {
                "goal_id": "TEST-GOAL-001",
                "products": [
                    {"format_id": "alpha"},
                    {"format_id": "beta"},
                ],
            }
        ),
        encoding="utf-8",
    )
    state = tmp_path / "controller-state.yaml"
    state.write_text(
        yaml.safe_dump(
            {
                "promotion": {"alpha": "UNASSESSED", "beta": "UNASSESSED"},
                "last_verified_event": {"event_id": "FF6-EVENT-000051"},
                "active_task": {"task_id": "SOME_STAGE"},
                "next_task": {"task_id": "SOME_STAGE", "unlock_condition": "do it"},
            }
        ),
        encoding="utf-8",
    )
    directive = tmp_path / "directive.yaml"
    directive.write_text(
        yaml.safe_dump({"status": "SOME_STAGE_READY"}), encoding="utf-8"
    )
    return {"goal": goal, "state": state, "directive": directive}


def _evaluate(mission: dict[str, Path]) -> dict:
    return gd.evaluate(
        goal_path=mission["goal"],
        state_path=mission["state"],
        directive_path=mission["directive"],
    )


def _set_promotion(mission: dict[str, Path], **promotion: str) -> None:
    document = yaml.safe_load(mission["state"].read_text(encoding="utf-8"))
    document["promotion"].update(promotion)
    mission["state"].write_text(yaml.safe_dump(document), encoding="utf-8")


# ── The mission ends only at its own definition of done ────────────────────


def test_continues_while_any_format_is_uncertified(mission: dict[str, Path]) -> None:
    result = _evaluate(mission)
    assert result["verdict"] == "CONTINUE"
    assert result["goal_achieved"] is False
    assert result["certified_count"] == 0


def test_still_continues_when_all_but_one_are_certified(
    mission: dict[str, Path],
) -> None:
    """Partial completion is not completion; 5/6 must not read as done."""
    _set_promotion(mission, alpha="CERTIFIED")
    result = _evaluate(mission)
    assert result["verdict"] == "CONTINUE"
    assert result["certified_count"] == 1
    assert result["required_count"] == 2


def test_goal_achieved_only_when_every_format_is_certified(
    mission: dict[str, Path],
) -> None:
    _set_promotion(mission, alpha="CERTIFIED", beta="CERTIFIED")
    result = _evaluate(mission)
    assert result["verdict"] == "GOAL_ACHIEVED"
    assert result["goal_achieved"] is True


@pytest.mark.parametrize("near_miss", ["CERTIFIED_PENDING", "certified", "ASSESSED"])
def test_only_the_exact_certified_state_counts(
    mission: dict[str, Path], near_miss: str
) -> None:
    """No lookalike status may be read as certification."""
    _set_promotion(mission, alpha=near_miss, beta=near_miss)
    assert _evaluate(mission)["verdict"] == "CONTINUE"


# ── It cannot stop for the reasons the generic actuator stops for ──────────


def test_verdict_does_not_depend_on_any_session_identity(
    mission: dict[str, Path],
) -> None:
    """The failure mode this replaces: STOP because a signal names another chat."""
    first = _evaluate(mission)
    second = _evaluate(mission)
    assert first == second
    assert first["session_independent"] is True
    assert "session_id" not in json.dumps(first)


def test_verdict_has_no_iteration_budget_to_exhaust(mission: dict[str, Path]) -> None:
    """MAX_ITERATIONS cannot arise: there is no counter in the computation.

    Asserts on the result's *keys*, not its prose -- the explanatory `notes`
    field legitimately mentions iteration budgets while describing their absence.
    """
    result = _evaluate(mission)
    assert not [key for key in result if "iteration" in key.lower()]
    assert "max_iterations" not in result


def test_repeated_evaluation_never_degrades_to_stop(mission: dict[str, Path]) -> None:
    """Twenty invocations, as a long autonomous run would make."""
    for _ in range(20):
        assert _evaluate(mission)["verdict"] == "CONTINUE"


def test_verdict_is_derived_from_state_not_from_a_signal_file(
    mission: dict[str, Path],
) -> None:
    assert _evaluate(mission)["derivation"] == "state_derived"


# ── Blocking is only ever an explicitly recorded external gate ─────────────


def test_blocks_only_on_a_recorded_external_gate(mission: dict[str, Path]) -> None:
    mission["directive"].write_text(
        yaml.safe_dump(
            {
                "status": "SOME_STAGE_READY",
                "structural_gaps_20260804": [
                    {
                        "id": "GAP-XYZ",
                        "status": "BLOCKED_EXTERNAL_PUBLICATION_CREDENTIALS",
                        "finding": "PyPI credentials unavailable",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    result = _evaluate(mission)
    assert result["verdict"] == "BLOCKED"
    assert result["external_blockers"][0]["id"] == "GAP-XYZ"


def test_ordinary_open_gaps_do_not_block(mission: dict[str, Path]) -> None:
    """An OPEN gap is work to do, not a reason to stop."""
    mission["directive"].write_text(
        yaml.safe_dump(
            {
                "status": "SOME_STAGE_READY",
                "structural_gaps_20260804": [
                    {"id": "GAP-001", "status": "OPEN", "finding": "lots to do"},
                    {"id": "GAP-002", "status": "PARTIALLY_FIXED", "finding": "more"},
                ],
            }
        ),
        encoding="utf-8",
    )
    assert _evaluate(mission)["verdict"] == "CONTINUE"


# ── Progress reporting is honest by construction ───────────────────────────


def test_an_unreconciled_format_reports_zero_resolved_not_unknown(
    mission: dict[str, Path],
) -> None:
    """A format never reconciled must not read as quietly complete."""
    result = _evaluate(mission)
    alpha = next(f for f in result["formats"] if f["format_id"] == "alpha")
    assert alpha["reconciliation"] == "NOT_RUN"
    assert alpha["obligations_resolved"] == 0
    assert "reconciler" in alpha["next_step"]


# ── Exit codes let a shell driver loop without any agent involved ──────────


def test_exit_code_is_zero_while_work_remains(
    mission: dict[str, Path], monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    monkeypatch.setattr(gd, "GOAL_PATH", mission["goal"])
    monkeypatch.setattr(gd, "STATE_PATH", mission["state"])
    monkeypatch.setattr(gd, "DIRECTIVE_PATH", mission["directive"])
    assert gd.main(["check"]) == gd.EXIT_CONTINUE
    assert json.loads(capsys.readouterr().out)["verdict"] == "CONTINUE"


def test_exit_code_distinguishes_goal_achieved_from_continue(
    mission: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _set_promotion(mission, alpha="CERTIFIED", beta="CERTIFIED")
    monkeypatch.setattr(gd, "GOAL_PATH", mission["goal"])
    monkeypatch.setattr(gd, "STATE_PATH", mission["state"])
    monkeypatch.setattr(gd, "DIRECTIVE_PATH", mission["directive"])
    assert gd.main(["check"]) == gd.EXIT_GOAL_ACHIEVED


# ── Against the real mission ───────────────────────────────────────────────


def test_real_mission_is_not_finished_and_says_so() -> None:
    result = gd.evaluate()
    assert result["verdict"] == "CONTINUE"
    assert result["certified_count"] == 0
    assert result["required_count"] == 6


def test_real_resume_briefing_names_the_next_action() -> None:
    text = gd.render_resume(gd.evaluate())
    assert "0/6" in text
    assert "NEXT ACTION" in text
