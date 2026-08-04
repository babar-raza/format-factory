"""Tests for the FF6 native controller event writer (GAP-007 mechanism).

These cover three things the hand-editing this module replaces could not give
us: that the real journal's chain is actually intact, that the writer refuses
every way of producing a broken chain, and that the second independent copy of
the hash algorithm has not drifted from this one.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from tools.ff6 import controller_events as ce

REPO_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------


def _body(**overrides: object) -> dict[str, object]:
    """A minimal valid event body (chain fields deliberately absent)."""
    body: dict[str, object] = {
        "schema": ce.EVENT_SCHEMA,
        "goal_id": ce.GOAL_ID,
        "state_before": "CONTRACT",
        "state_after": "CONTRACT",
        "task_id": "TC-FF6-TEST-001",
        "transition": "TEST_TRANSITION",
        "agent": "pytest",
    }
    body.update(overrides)
    return body


@pytest.fixture
def journal(tmp_path: Path) -> Path:
    """A two-event journal with a valid chain, isolated from the real one."""
    path = tmp_path / "events.jsonl"
    first = _body(task_id="TC-FF6-TEST-000", transition="GENESIS")
    first |= {"sequence": 1, "event_id": "FF6-EVENT-000001", "previous_event_hash": None}
    first["event_hash"] = ce.event_hash(first)

    second = _body()
    second |= {
        "sequence": 2,
        "event_id": "FF6-EVENT-000002",
        "previous_event_hash": first["event_hash"],
    }
    second["event_hash"] = ce.event_hash(second)

    path.write_text(
        "".join(ce.serialize_event(e) + "\n" for e in (first, second)),
        encoding="utf-8",
    )
    return path


# --------------------------------------------------------------------------
# The real journal
# --------------------------------------------------------------------------


def test_real_journal_chain_is_intact() -> None:
    events = ce.load_journal()
    assert ce.validate_chain(events) == []
    assert len(events) >= 47


def test_real_journal_head_matches_projection_head() -> None:
    """controller-state.yaml must not drift from the journal it projects."""
    head = ce.load_journal()[-1]
    state = ce.STATE_PATH.read_bytes().decode("utf-8")
    assert f"transition_sequence: {head['sequence']}\n" in state
    assert f"event_id: {head['event_id']}\n" in state
    assert f"event_hash: {head['event_hash']}\n" in state


def test_hash_algorithm_has_not_drifted_from_the_handover_copy() -> None:
    """Drift guard for the second copy of the hash rule (GAP-003 lesson).

    ``plans/codex/handover/handover_projection.py`` is a portable handover
    artifact and keeps its own self-contained implementation. If the two ever
    disagree on any real event, one of them is wrong and this fails.
    """
    module_path = REPO_ROOT / "plans" / "codex" / "handover" / "handover_projection.py"
    spec = importlib.util.spec_from_file_location("_ff6_handover", module_path)
    assert spec is not None and spec.loader is not None
    handover = importlib.util.module_from_spec(spec)
    # Register before exec: the module defines dataclasses, and dataclass field
    # resolution looks the owning module up in sys.modules by name.
    sys.modules[spec.name] = handover
    try:
        spec.loader.exec_module(handover)
    finally:
        sys.modules.pop(spec.name, None)

    events = ce.load_journal()
    for event in events:
        assert ce.event_hash(event) == handover.event_hash(event), event["event_id"]


# --------------------------------------------------------------------------
# Chain validation catches every corruption shape
# --------------------------------------------------------------------------


def test_validate_chain_detects_tampered_payload(journal: Path) -> None:
    events = ce.load_journal(journal)
    events[1]["transition"] = "SOMETHING_ELSE"  # hash no longer matches
    errors = ce.validate_chain(events)
    assert any("event_hash" in e for e in errors)


def test_validate_chain_detects_sequence_gap(journal: Path) -> None:
    events = ce.load_journal(journal)
    events[1]["sequence"] = 3
    errors = ce.validate_chain(events)
    assert any("sequence is 3" in e for e in errors)


def test_validate_chain_detects_broken_predecessor_link(journal: Path) -> None:
    events = ce.load_journal(journal)
    events[1]["previous_event_hash"] = "0" * 64
    events[1]["event_hash"] = ce.event_hash(events[1])  # internally consistent
    errors = ce.validate_chain(events)
    assert any("predecessor hash" in e for e in errors)


def test_validate_chain_detects_missing_required_field(journal: Path) -> None:
    events = ce.load_journal(journal)
    del events[1]["transition"]
    errors = ce.validate_chain(events)
    assert any("missing required field" in e for e in errors)


# --------------------------------------------------------------------------
# The writer refuses bad input
# --------------------------------------------------------------------------


@pytest.mark.parametrize("field", sorted(ce.DERIVED_FIELDS))
def test_append_rejects_presupplied_chain_fields(journal: Path, field: str) -> None:
    with pytest.raises(ce.ControllerEventError, match="derived chain field"):
        ce.append_event(
            _body(**{field: "attacker-chosen"}),
            journal_path=journal,
            verify_commits=False,
        )


def test_append_rejects_wrong_schema(journal: Path) -> None:
    with pytest.raises(ce.ControllerEventError, match="schema must be"):
        ce.append_event(
            _body(schema="ff6/controller-event@99"),
            journal_path=journal,
            verify_commits=False,
        )


def test_append_rejects_wrong_goal(journal: Path) -> None:
    with pytest.raises(ce.ControllerEventError, match="goal_id must be"):
        ce.append_event(
            _body(goal_id="SOME-OTHER-MISSION"),
            journal_path=journal,
            verify_commits=False,
        )


def test_append_rejects_missing_required_field(journal: Path) -> None:
    body = _body()
    del body["transition"]
    with pytest.raises(ce.ControllerEventError, match="missing required field"):
        ce.append_event(body, journal_path=journal, verify_commits=False)


def test_append_rejects_nonexistent_semantic_commit(journal: Path) -> None:
    """An event may not claim a commit that does not exist."""
    with pytest.raises(ce.ControllerEventError, match="does not resolve to a commit"):
        ce.append_event(
            _body(semantic_commit="0" * 40),
            journal_path=journal,
            verify_commits=True,
        )


def test_append_accepts_a_real_commit(journal: Path) -> None:
    event = ce.append_event(
        _body(semantic_commit="028b6db4"),
        journal_path=journal,
        verify_commits=True,
    )
    assert event["sequence"] == 3


def test_append_refuses_onto_an_already_broken_chain(journal: Path) -> None:
    """Appending onto corruption would hide it under a valid-looking head."""
    events = ce.load_journal(journal)
    events[1]["transition"] = "TAMPERED"
    journal.write_text(
        "".join(ce.serialize_event(e) + "\n" for e in events), encoding="utf-8"
    )
    with pytest.raises(ce.ControllerEventError, match="existing chain is invalid"):
        ce.append_event(_body(), journal_path=journal, verify_commits=False)


# --------------------------------------------------------------------------
# The writer produces a valid chain
# --------------------------------------------------------------------------


def test_append_derives_all_chain_fields(journal: Path) -> None:
    before = ce.load_journal(journal)
    event = ce.append_event(_body(), journal_path=journal, verify_commits=False)

    assert event["sequence"] == 3
    assert event["event_id"] == "FF6-EVENT-000003"
    assert event["previous_event_hash"] == before[-1]["event_hash"]
    assert event["event_hash"] == ce.event_hash(event)
    assert ce.validate_chain(ce.load_journal(journal)) == []


def test_append_preserves_existing_bytes_exactly(journal: Path) -> None:
    """Append-only means append-only: prior lines are never rewritten."""
    original = journal.read_bytes()
    ce.append_event(_body(), journal_path=journal, verify_commits=False)
    assert journal.read_bytes().startswith(original)


def test_append_is_dry_runnable(journal: Path) -> None:
    original = journal.read_bytes()
    event = ce.append_event(
        _body(), journal_path=journal, verify_commits=False, dry_run=True
    )
    assert event["event_id"] == "FF6-EVENT-000003"
    assert journal.read_bytes() == original


def test_appended_line_is_canonical_json(journal: Path) -> None:
    event = ce.append_event(_body(), journal_path=journal, verify_commits=False)
    last = journal.read_text(encoding="utf-8").splitlines()[-1]
    assert last == ce.serialize_event(event)
    assert json.loads(last)["event_hash"] == event["event_hash"]


def test_successive_appends_chain_together(journal: Path) -> None:
    first = ce.append_event(_body(), journal_path=journal, verify_commits=False)
    second = ce.append_event(_body(), journal_path=journal, verify_commits=False)
    assert second["previous_event_hash"] == first["event_hash"]
    assert second["sequence"] == first["sequence"] + 1
    assert ce.validate_chain(ce.load_journal(journal)) == []


# --------------------------------------------------------------------------
# Projection sync
# --------------------------------------------------------------------------


def test_sync_projection_updates_only_the_head_scalars(
    tmp_path: Path, journal: Path
) -> None:
    state = tmp_path / "controller-state.yaml"
    state.write_text(
        "schema: ff6/controller-state@1\n"
        "transition_sequence: 1\n"
        "last_verified_event:\n"
        "  event_id: FF6-EVENT-000001\n"
        "  event_hash: deadbeef\n"
        "nrrd_checkpoint:\n"
        "  event_id: FF6-EVENT-000001  # must NOT be touched\n",
        encoding="utf-8",
    )
    result = ce.sync_projection_head(journal_path=journal, state_path=state)

    head = ce.load_journal(journal)[-1]
    text = state.read_text(encoding="utf-8")
    assert result["changed"] is True
    assert f"transition_sequence: {head['sequence']}\n" in text
    assert f"  event_id: {head['event_id']}\n" in text
    assert f"  event_hash: {head['event_hash']}\n" in text
    # The nested per-format checkpoint carries reviewed judgement, not a
    # mechanical restatement of the head -- it must survive untouched.
    assert "  event_id: FF6-EVENT-000001  # must NOT be touched\n" in text


def test_sync_projection_refuses_partial_write(tmp_path: Path, journal: Path) -> None:
    state = tmp_path / "controller-state.yaml"
    state.write_text("schema: ff6/controller-state@1\n", encoding="utf-8")
    with pytest.raises(ce.ControllerEventError, match="could not locate"):
        ce.sync_projection_head(journal_path=journal, state_path=state)
    assert state.read_text(encoding="utf-8") == "schema: ff6/controller-state@1\n"


def test_sync_projection_refuses_when_chain_is_broken(
    tmp_path: Path, journal: Path
) -> None:
    events = ce.load_journal(journal)
    events[1]["transition"] = "TAMPERED"
    journal.write_text(
        "".join(ce.serialize_event(e) + "\n" for e in events), encoding="utf-8"
    )
    state = tmp_path / "controller-state.yaml"
    state.write_text("transition_sequence: 1\n", encoding="utf-8")
    with pytest.raises(ce.ControllerEventError, match="chain is invalid"):
        ce.sync_projection_head(journal_path=journal, state_path=state)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def test_cli_verify_passes_on_the_real_journal(capsys: pytest.CaptureFixture) -> None:
    assert ce.main(["verify"]) == 0
    assert "PASS" in capsys.readouterr().out


def test_cli_verify_fails_on_a_broken_journal(
    journal: Path, capsys: pytest.CaptureFixture
) -> None:
    events = ce.load_journal(journal)
    events[1]["transition"] = "TAMPERED"
    journal.write_text(
        "".join(ce.serialize_event(e) + "\n" for e in events), encoding="utf-8"
    )
    assert ce.main(["verify", "--journal", str(journal)]) == 1
    assert "FAIL" in capsys.readouterr().err


def test_cli_append_writes_and_reports(journal: Path, tmp_path: Path) -> None:
    body_path = tmp_path / "body.json"
    body_path.write_text(json.dumps(_body()), encoding="utf-8")
    exit_code = ce.main(
        [
            "append",
            str(body_path),
            "--journal",
            str(journal),
            "--skip-commit-check",
        ]
    )
    assert exit_code == 0
    assert len(ce.load_journal(journal)) == 3
    assert ce.validate_chain(ce.load_journal(journal)) == []
