from __future__ import annotations

import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.plan_control.cli import EXIT_BLOCKED, EXIT_OK, main
from tools.plan_control.coordination import CoordinationAdapter, CoordinationError
from tools.plan_control.engine import PlanControlEngine
from tools.plan_control.journal import EventJournal
from tools.plan_control.models import ExecutionState
from tools.plan_control.parser import parse_plan
from tools.plan_control.portfolio import read_source_items
from tools.plan_control.producer import ProducerStateError


def _plan(repo: Path, name: str, body: str) -> Path:
    root = repo / "plans" / ".claude"
    root.mkdir(parents=True, exist_ok=True)
    path = root / name
    path.write_text(body, encoding="utf-8")
    return path


def test_concurrent_journal_writers_preserve_every_event(tmp_path: Path) -> None:
    path = tmp_path / "events.jsonl"

    def append(index: int) -> bool:
        return EventJournal(path).append(
            "CONCURRENT_TEST", {"index": index}, event_id=f"writer-{index}"
        ).appended

    with ThreadPoolExecutor(max_workers=16) as pool:
        assert all(pool.map(append, range(32)))
    events = EventJournal(path).read()
    assert len(events) == 32
    assert {event["payload"]["index"] for event in events} == set(range(32))


def test_claim_excludes_pending_task_and_allows_start(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _plan(
        tmp_path,
        "claim.md",
        "# Claim\n### TC-CLAIM-001 — Claim me\n**Status:** PENDING\n",
    )
    control = tmp_path / "control"
    engine = PlanControlEngine(tmp_path, control_root=control)
    engine.discover()
    monkeypatch.setattr(
        "tools.plan_control.cli.CoordinationAdapter.claim",
        lambda self, resource, task: "lease-ok",
    )
    assert (
        main(
            [
                "--repo",
                str(tmp_path),
                "--control-root",
                str(control),
                "claim",
                "TC-CLAIM-001",
            ]
        )
        == EXIT_OK
    )
    engine = PlanControlEngine(tmp_path, control_root=control)
    assert engine.show("TC-CLAIM-001")["state"] == "CLAIMED"
    assert engine.queue() == []
    engine.transition_task(
        "TC-CLAIM-001", ExecutionState.IN_PROGRESS, reason="autonomous start"
    )
    assert engine.show("TC-CLAIM-001")["state"] == "IN_PROGRESS"


def test_blocked_and_verification_only_cli_returns_four(tmp_path: Path) -> None:
    _plan(
        tmp_path,
        "blocked.md",
        "# Blocked\n### TC-BLOCK-001 — Wait\n**Status:** BLOCKED\n",
    )
    control = tmp_path / "control"
    engine = PlanControlEngine(tmp_path, control_root=control)
    engine.discover()
    assert (
        main(["--repo", str(tmp_path), "--control-root", str(control), "next"])
        == EXIT_BLOCKED
    )
    assert (
        main(
            [
                "--repo",
                str(tmp_path),
                "--control-root",
                str(control),
                "explain",
                "TC-BLOCK-001",
            ]
        )
        == EXIT_BLOCKED
    )


def test_retry_backoff_quarantines_three_distinct_failures_and_continues(
    tmp_path: Path,
) -> None:
    _plan(
        tmp_path,
        "retry.md",
        """# Retry
### TC-RETRY-001 — Flaky
**Status:** READY
### TC-OTHER-001 — Continue
**Status:** READY
""",
    )
    engine = PlanControlEngine(tmp_path)
    engine.discover()
    first = engine.record_failure(
        "TC-RETRY-001",
        root_cause="network",
        failure_signature="timeout-a",
        observed_at=100.0,
    )
    assert first["state"] == "PENDING"
    assert first["retry_not_before"] == 105.0
    assert [item["external_id"] for item in engine.queue()] == ["TC-OTHER-001"]
    assert engine.explain("TC-RETRY-001")["runnable"] is False
    engine.release_due_retries(now=105.0)
    engine.record_failure(
        "TC-RETRY-001",
        root_cause="network",
        failure_signature="timeout-b",
        observed_at=200.0,
    )
    engine.release_due_retries(now=210.0)
    third = engine.record_failure(
        "TC-RETRY-001",
        root_cause="network",
        failure_signature="reset-c",
        observed_at=300.0,
    )
    assert third["state"] == "BLOCKED"
    assert [item["external_id"] for item in engine.queue()] == ["TC-OTHER-001"]


def test_age_is_part_of_deterministic_queue_order(tmp_path: Path) -> None:
    _plan(
        tmp_path,
        "new.md",
        "---\ngenerated_at: 2026-07-01\n---\n# New\n"
        "### TC-NEW-001 — New\n**Status:** READY\n",
    )
    _plan(
        tmp_path,
        "old.md",
        "---\ngenerated_at: 2025-01-01\n---\n# Old\n"
        "### TC-OLD-001 — Old\n**Status:** READY\n",
    )
    engine = PlanControlEngine(tmp_path)
    engine.discover()
    queue = engine.queue()
    assert [item["external_id"] for item in queue] == ["TC-OLD-001", "TC-NEW-001"]
    assert "age=" in queue[0]["reason"]


def test_alias_growth_preserves_persisted_plan_identity(tmp_path: Path) -> None:
    path = _plan(
        tmp_path,
        "identity.md",
        "---\nmission_id: MISSION-Z\n---\n# Identity\n",
    )
    engine = PlanControlEngine(tmp_path)
    engine.discover()
    original = engine.show("MISSION-Z")["plan_id"]
    path.write_text(
        "---\nartifact_id: ARTIFACT-A\nmission_id: MISSION-Z\n---\n# Identity\n",
        encoding="utf-8",
    )
    engine.discover()
    assert engine.show("ARTIFACT-A")["plan_id"] == original
    assert engine.show("MISSION-Z")["plan_id"] == original
    assert len(engine.list_records("plans")) == 1


def test_parser_expands_ranges_and_records_malformed_table_gap(
    tmp_path: Path,
) -> None:
    path = tmp_path / "ranges.md"
    path.write_text(
        """# Ranges
### TC-R-001..TC-R-003 — Range
**Status:** READY

| Task ID | Status |
| malformed divider |
| TC-BAD-001 | COMPLETE |
""",
        encoding="utf-8",
    )
    parsed = parse_plan(path)
    assert [task.external_id for task in parsed.tasks] == [
        "TC-R-001",
        "TC-R-002",
        "TC-R-003",
    ]
    assert any("MALFORMED_STATUS_TABLE" in warning for warning in parsed.warnings)
    repo = tmp_path / "repo"
    target = _plan(repo, "ranges.md", path.read_text(encoding="utf-8"))
    assert target.exists()
    engine = PlanControlEngine(repo)
    engine.discover()
    assert any(gap["kind"] == "PLAN_PARSE" for gap in engine.state()["gaps"].values())
    assert engine.queue() == []


def test_clean_external_worktree_never_dispatches_and_head_history_reconciles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    canonical = tmp_path / "canonical"
    external = tmp_path / "external"
    (canonical / "plans").mkdir(parents=True)
    _plan(
        external,
        "external.md",
        "---\nmission_id: EXTERNAL-MISSION\n---\n# External\n"
        "### TC-E-001 — External\n**Status:** READY\n",
    )
    canonical_obs = SimpleNamespace(
        path=str(canonical),
        branch="main",
        commit="main-a",
        dirty=False,
        canonical=True,
        to_dict=lambda: {},
    )
    external_a = SimpleNamespace(
        path=str(external),
        branch="feature",
        commit="head-a",
        dirty=False,
        canonical=False,
        abandoned=False,
        to_dict=lambda: {},
    )
    external_b = SimpleNamespace(
        path=str(external),
        branch="feature",
        commit="head-b",
        dirty=False,
        canonical=False,
        abandoned=False,
        to_dict=lambda: {},
    )
    observations = iter(
        [[canonical_obs, external_a], [canonical_obs, external_b], [canonical_obs]]
    )
    monkeypatch.setattr(
        "tools.plan_control.engine.observe_worktrees", lambda _: next(observations)
    )
    engine = PlanControlEngine(canonical)
    engine.observe_external_worktrees("")
    assert engine.queue() == []
    assert engine.show("EXTERNAL-MISSION")["external_claimed"] is True
    engine.observe_external_worktrees("")
    engine.observe_external_worktrees("")
    occurrences = engine.show("EXTERNAL-MISSION")["occurrences"]
    assert {item["commit"] for item in occurrences} == {"head-a", "head-b"}
    assert all(item["active"] is False for item in occurrences)


def test_abandoned_worktree_branch_is_quarantined_and_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    canonical = tmp_path / "canonical"
    external = tmp_path / "external"
    (canonical / "plans").mkdir(parents=True)
    _plan(
        external,
        "abandoned.md",
        "---\nmission_id: ABANDONED-MISSION\n---\n# Abandoned\n"
        "### TC-ABANDONED-001 — Never dispatch\n**Status:** READY\n",
    )
    observations = [
        SimpleNamespace(
            path=str(canonical),
            branch="main",
            commit="main",
            dirty=False,
            canonical=True,
            abandoned=False,
            to_dict=lambda: {},
        ),
        SimpleNamespace(
            path=str(external),
            branch="deleted-branch",
            commit="orphan",
            dirty=False,
            canonical=False,
            abandoned=True,
            to_dict=lambda: {},
        ),
    ]
    monkeypatch.setattr(
        "tools.plan_control.engine.observe_worktrees", lambda _: observations
    )
    engine = PlanControlEngine(canonical)
    engine.observe_external_worktrees("")
    plan = engine.show("ABANDONED-MISSION")
    assert plan["external_claimed"] is True
    assert plan["coordination_owner"].startswith("abandoned-worktree:")
    assert engine.queue() == []
    assert any(
        gap["kind"] == "ABANDONED_WORKTREE_BRANCH"
        for gap in engine.state()["gaps"].values()
    )


def test_verification_cancellation_and_portfolio_closure_require_authority(
    tmp_path: Path,
) -> None:
    _plan(
        tmp_path,
        "closure.md",
        "# Closure\n### TC-CLOSE-001 — Close\n**Status:** AWAITING_VERIFICATION\n",
    )
    engine = PlanControlEngine(tmp_path)
    engine.discover()
    with pytest.raises(ValueError, match="verification requires"):
        engine.transition_task(
            "TC-CLOSE-001", ExecutionState.VERIFIED, reason="thin"
        )
    register = tmp_path / "register.json"
    register.write_text(
        json.dumps(
            {
                "plans": [
                    {
                        "source_plan": "source.md",
                        "taskcards": [
                            {
                                "taskcard_id": "TC-FALSE-001",
                                "disposition": "COMPLETE",
                                "evidence_digest": "not-a-digest",
                            },
                            {
                                "taskcard_id": "TC-FALSE-002",
                                "disposition": "CANCELLED",
                                "cancellation_authority": "x",
                            },
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    items = read_source_items(register)
    assert {item["disposition"] for item in items} == {"STILL_OPEN"}
    assert all(item["contradiction"] for item in items)


def test_producer_verification_is_digest_and_verifier_bound(tmp_path: Path) -> None:
    _plan(
        tmp_path,
        "producer.md",
        "---\nmission_id: PRODUCER-PLAN\n---\n# Producer\n"
        "### TC-PRODUCER-001 — Verify\n**Status:** AWAITING_VERIFICATION\n",
    )
    state_dir = tmp_path / "producer-state"
    state_dir.mkdir()
    state_path = state_dir / "state.json"
    state_path.write_text(
        json.dumps(
            {
                "schema": "format-factory/production-program-state@1",
                "evidence_digest": "z" * 64,
            }
        ),
        encoding="utf-8",
    )
    engine = PlanControlEngine(tmp_path)
    engine.discover()
    with pytest.raises(ProducerStateError):
        engine.ingest_producer(
            state_dir=state_dir,
            producer="production-program",
            plan_id="PRODUCER-PLAN",
            task_id="TC-PRODUCER-001",
            source_commit="abc123",
            evidence_path=None,
            declared_verifier="expected-verifier",
        )
    state_path.write_text(
        json.dumps(
            {
                "schema": "format-factory/production-program-state@1",
                "evidence_digest": "a" * 64,
            }
        ),
        encoding="utf-8",
    )
    engine.ingest_producer(
        state_dir=state_dir,
        producer="production-program",
        plan_id="PRODUCER-PLAN",
        task_id="TC-PRODUCER-001",
        source_commit="abc123",
        evidence_path=None,
        declared_verifier="expected-verifier",
    )
    with pytest.raises(ValueError, match="declared verifier"):
        engine.transition_task(
            "TC-PRODUCER-001",
            ExecutionState.VERIFIED,
            reason="wrong verifier",
            evidence={"reference": "a" * 64, "verifier": "other-verifier"},
        )
    engine.transition_task(
        "TC-PRODUCER-001",
        ExecutionState.VERIFIED,
        reason="declared verifier pass",
        evidence={"reference": "sha256:" + "a" * 64, "verifier": "expected-verifier"},
    )
    checkpoint = engine.state()["domain_checkpoints"][0]
    assert checkpoint["verified"] is True
    assert checkpoint["verification"]["result"] == "PASS"


def test_external_publication_blocker_does_not_stop_unrelated_queue(
    tmp_path: Path,
) -> None:
    _plan(
        tmp_path,
        "publication.md",
        """# Publication
### TC-PUBLISH-001 — Publish
**Status:** READY
### TC-LOCAL-001 — Local
**Status:** READY
""",
    )
    engine = PlanControlEngine(tmp_path)
    engine.discover()
    engine.transition_task(
        "TC-PUBLISH-001",
        ExecutionState.BLOCKED,
        reason="publication credential required",
        external_blocker=True,
    )
    assert [item["external_id"] for item in engine.queue()] == ["TC-LOCAL-001"]
    assert engine.explain("TC-PUBLISH-001")["reason"].endswith(
        "quarantined external blocker"
    )


def test_coordination_conflict_maps_to_six_and_takeover_is_explicit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        if "claim" in command:
            return subprocess.CompletedProcess(command, 2, "", "conflict")
        return subprocess.CompletedProcess(command, 0, "taken", "")

    monkeypatch.setattr("tools.plan_control.coordination.subprocess.run", fake_run)
    adapter = CoordinationAdapter(tmp_path)
    with pytest.raises(CoordinationError) as error:
        adapter.claim("logical:test", "TC-X")
    assert error.value.exit_code == 6
    assert adapter.takeover("lease-stale", "verified stale owner") == "taken"
    assert calls[-1][-4:] == [
        "--lease",
        "lease-stale",
        "--reason",
        "verified stale owner",
    ]
