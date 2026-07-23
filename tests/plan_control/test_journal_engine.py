import json
from pathlib import Path

import pytest

from tools.plan_control.engine import PlanControlEngine
from tools.plan_control.journal import EventJournal, JournalError, canonical_json
from tools.plan_control.models import ExecutionState
from tools.plan_control.projections import projection_documents, projection_digest, reduce_events


def _repo(tmp_path: Path) -> Path:
    (tmp_path / "plans" / ".claude").mkdir(parents=True)
    (tmp_path / "plans" / "master-plan.md").write_text(
        "---\nartifact_id: MASTER\nstatus: IN_PROGRESS\n---\n# Master\n",
        encoding="utf-8",
    )
    (tmp_path / "plans" / ".claude" / "child.md").write_text(
        """---
mission_id: CHILD-1
status: IN_PROGRESS
---
# Child
### TC-ONE-001 — First
**Status:** READY
### TC-TWO-001 — Second
**Status:** BLOCKED
""",
        encoding="utf-8",
    )
    return tmp_path


def test_hash_chain_idempotency_and_corruption_detection(tmp_path: Path) -> None:
    journal = EventJournal(tmp_path / "events.jsonl")
    first = journal.append("TEST", {"value": 1}, event_id="same")
    second = journal.append("TEST", {"value": 1}, event_id="same")
    assert first.appended is True
    assert second.appended is False
    assert journal.head == first.event["event_hash"]
    line = json.loads((tmp_path / "events.jsonl").read_text(encoding="utf-8"))
    line["payload"]["value"] = 2
    (tmp_path / "events.jsonl").write_text(json.dumps(line) + "\n", encoding="utf-8")
    with pytest.raises(JournalError, match="event hash mismatch"):
        journal.read()


def test_reconcile_is_idempotent_and_projection_replay_is_deterministic(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    engine = PlanControlEngine(repo)
    first = engine.reconcile(include_worktrees=False)
    event_count = len(engine.journal.read())
    second = engine.reconcile(include_worktrees=False)
    assert len(engine.journal.read()) == event_count
    assert second["discover"]["events_appended"] == 0
    state_a = reduce_events(engine.journal.read())
    state_b = reduce_events(engine.journal.read())
    assert projection_digest(projection_documents(state_a)) == projection_digest(
        projection_documents(state_b)
    )
    assert first["projection"]["runnable_count"] == 1


def test_reducer_never_mutates_cached_nested_event_payloads(tmp_path: Path) -> None:
    engine = PlanControlEngine(_repo(tmp_path))
    engine.reconcile(include_worktrees=False)
    engine.transition_task("TC-ONE-001", ExecutionState.IN_PROGRESS, reason="start")
    engine.transition_task(
        "TC-ONE-001",
        ExecutionState.AWAITING_VERIFICATION,
        reason="done",
        evidence={"reference": "sha256:abc", "verifier": "pilot"},
    )
    engine.transition_task(
        "TC-ONE-001",
        ExecutionState.VERIFIED,
        reason="verified",
        evidence={"reference": "sha256:abc", "verifier": "pilot"},
    )

    cached_events = engine.journal.read()
    journal_before = canonical_json(cached_events)
    first = projection_documents(reduce_events(cached_events))
    second = projection_documents(reduce_events(cached_events))

    assert projection_digest(first) == projection_digest(second)
    assert canonical_json(engine.journal.read()) == journal_before
    engine.project()
    assert engine.doctor()["ok"] is True


def test_crash_after_event_before_projection_recovers_by_replay(tmp_path: Path) -> None:
    engine = PlanControlEngine(_repo(tmp_path))
    engine.discover()
    assert not engine.paths.projection_root.exists()
    recovered = engine.project()
    assert recovered["task_count"] == 2
    assert (engine.paths.projection_root / "registry.json").exists()


def test_task_requires_verification_before_complete(tmp_path: Path) -> None:
    engine = PlanControlEngine(_repo(tmp_path))
    engine.reconcile(include_worktrees=False)
    engine.transition_task("TC-ONE-001", ExecutionState.IN_PROGRESS, reason="start")
    engine.transition_task(
        "TC-ONE-001", ExecutionState.AWAITING_VERIFICATION, reason="implementation done"
    )
    engine.transition_task(
        "TC-ONE-001",
        ExecutionState.VERIFIED,
        reason="independent verification",
        evidence={"reference": "sha256:abc", "verifier": "independent-agent"},
    )
    result = engine.transition_task("TC-ONE-001", ExecutionState.COMPLETE, reason="close")
    assert result["state"] == "COMPLETE"


def test_route_violations_are_reported_not_adopted(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "plans" / "oracle").mkdir()
    (repo / "plans" / "root-plan.md").write_text("# Wrong root\n", encoding="utf-8")
    engine = PlanControlEngine(repo)
    result = engine.discover()
    assert "UNAPPROVED_PLAN_ROOT:plans/oracle" in result["route_violations"]
    assert "UNROUTED_PLAN_FILE:plans/root-plan.md" in result["route_violations"]


def test_terminal_plan_closure_rejects_open_task_and_missing_evidence(tmp_path: Path) -> None:
    engine = PlanControlEngine(_repo(tmp_path))
    engine.reconcile(include_worktrees=False)
    with pytest.raises(ValueError, match="open tasks"):
        engine.transition_plan(
            "CHILD-1", ExecutionState.TERMINAL_CLOSED, reason="premature"
        )
    for external_id in ("TC-ONE-001", "TC-TWO-001"):
        task_id = engine.resolve_id(external_id)[1]
        engine.journal.append(
            "TASK_STATE_CHANGED",
            {
                "task_id": task_id,
                "current_state": engine.state()["tasks"][task_id]["state"],
                "target_state": "COMPLETE",
                "reason": "fixture",
                "evidence": None,
            },
            event_id=f"fixture-close:{task_id}",
        )
    with pytest.raises(ValueError, match="missing evidence"):
        engine.transition_plan(
            "CHILD-1", ExecutionState.TERMINAL_CLOSED, reason="still premature"
        )
