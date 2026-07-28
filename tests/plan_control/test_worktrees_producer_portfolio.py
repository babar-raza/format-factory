import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.plan_control.engine import PlanControlEngine
from tools.plan_control.portfolio import read_source_items
from tools.plan_control.producer import ProducerStateError, read_checkpoint
from tools.plan_control.worktrees import parse_active_tasks


def test_active_task_parser() -> None:
    status = (
        "agent-codex-1  [ACTIVE]  provider=codex "
        "task=FF-SIX-PYTHON-PRODUCTION-AUTONOMOUS hb=now\n"
    )
    assert parse_active_tasks(status) == {
        "ff-six-python-production-autonomous": "agent-codex-1"
    }


def test_external_active_plan_is_not_dispatched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    canonical = tmp_path / "canonical"
    external = tmp_path / "external"
    (canonical / "plans").mkdir(parents=True)
    (canonical / "plans" / "master-plan.md").write_text("# Master\n", encoding="utf-8")
    (external / "plans" / ".claude").mkdir(parents=True)
    (external / "plans" / ".claude" / "six.md").write_text(
        """---
mission_id: FF-SIX-PYTHON-PRODUCTION-AUTONOMOUS
status: IN_PROGRESS
---
# Six
### TC-FF6-IPYNB-SAFE-001 — Harden
**Status:** READY
""",
        encoding="utf-8",
    )
    observations = [
        SimpleNamespace(
            path=str(canonical), branch="main", commit="a", dirty=False, canonical=True,
            to_dict=lambda: {"path": str(canonical), "canonical": True},
        ),
        SimpleNamespace(
            path=str(external), branch="codex/six", commit="dabcc732", dirty=True,
            canonical=False,
            to_dict=lambda: {"path": str(external), "canonical": False},
        ),
    ]
    monkeypatch.setattr("tools.plan_control.engine.observe_worktrees", lambda _: observations)
    engine = PlanControlEngine(canonical)
    engine.discover()
    engine.observe_external_worktrees(
        "agent-six [ACTIVE] provider=codex task=FF-SIX-PYTHON-PRODUCTION-AUTONOMOUS"
    )
    plan = next(
        item
        for item in engine.state()["plans"].values()
        if "FF-SIX-PYTHON-PRODUCTION-AUTONOMOUS" in item.get("aliases", [])
    )
    assert plan["external_claimed"] is True
    assert all(item["external_id"] != "TC-FF6-IPYNB-SAFE-001" for item in engine.queue())


def test_dirty_external_complete_is_downgraded_to_verification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    canonical = tmp_path / "canonical"
    external = tmp_path / "external"
    (canonical / "plans").mkdir(parents=True)
    (external / "plans" / ".claude").mkdir(parents=True)
    (external / "plans" / ".claude" / "plan.md").write_text(
        "# Plan\n### TC-X-001 — X\n**Status:** COMPLETE\n", encoding="utf-8"
    )
    observations = [
        SimpleNamespace(
            path=str(canonical), canonical=True, branch="main", commit="a", dirty=False,
            to_dict=lambda: {},
        ),
        SimpleNamespace(
            path=str(external), canonical=False, branch="feature", commit="b", dirty=True,
            to_dict=lambda: {},
        ),
    ]
    monkeypatch.setattr("tools.plan_control.engine.observe_worktrees", lambda _: observations)
    engine = PlanControlEngine(canonical)
    engine.observe_external_worktrees("")
    task = next(iter(engine.state()["tasks"].values()))
    assert task["state"] == "AWAITING_VERIFICATION"
    plan = next(iter(engine.state()["plans"].values()))
    assert plan["external_claimed"] is True
    assert engine.queue() == []


def test_producer_checkpoint_is_digest_bound_and_non_promoting(tmp_path: Path) -> None:
    state_dir = tmp_path / "producer"
    state_dir.mkdir()
    (state_dir / "state.json").write_text(
        json.dumps(
            {
                "schema": "format-factory/production-program-state@1",
                "formats": {},
                "evidence_digest": "a" * 64,
            }
        ),
        encoding="utf-8",
    )
    checkpoint = read_checkpoint(
        state_dir=state_dir,
        producer="production-program",
        plan_id="plan-1",
        task_id="task-1",
        source_commit="dabcc732",
        declared_verifier="production-program-verifier",
    )
    assert checkpoint["producer_state_digest"]
    assert checkpoint["evidence_digest"] == "a" * 64
    assert checkpoint["declared_verifier"] == "production-program-verifier"
    assert checkpoint["verified"] is False
    with pytest.raises(ProducerStateError):
        read_checkpoint(
            state_dir=tmp_path / "missing",
            producer="production-program",
            plan_id="plan-1",
            task_id=None,
            source_commit="x",
            declared_verifier="production-program-verifier",
        )


def test_portfolio_accounts_for_all_2326_items_as_open(tmp_path: Path) -> None:
    path = tmp_path / "register.json"
    path.write_text(
        json.dumps(
            {
                "plans": [
                    {
                        "source_plan": "source.md",
                        "taskcards": [
                            {
                                "taskcard_id": f"TC-{index}",
                                "master_state": "UNRECONCILED",
                                "disposition": None,
                                "occurrences": [],
                            }
                            for index in range(2326)
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    items = read_source_items(path)
    assert len(items) == 2326
    assert {item["disposition"] for item in items} == {"STILL_OPEN"}
    assert len({item["source_item_id"] for item in items}) == 2326


def test_declared_migration_checkpoint_is_verified_and_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan_root = tmp_path / "plans" / ".claude"
    control = tmp_path / "plans" / ".control"
    plan_root.mkdir(parents=True)
    control.mkdir(parents=True)
    (plan_root / "six.md").write_text(
        "---\nmission_id: FF-SIX\n---\n# Six\n", encoding="utf-8"
    )
    (control / "config.json").write_text(
        json.dumps(
            {
                "migration_checkpoints": [
                    {
                        "plan_alias": "FF-SIX",
                        "source_commit": "checkpoint",
                        "branch": "feature",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "tools.plan_control.engine.verify_commit_occurrence",
        lambda repo, ref, branch: {
            "source_commit": "a" * 40,
            "commit_object_digest": "b" * 64,
        },
    )
    engine = PlanControlEngine(tmp_path)
    engine.discover()
    assert engine.reconcile_migration_checkpoints() == {
        "configured": 1,
        "recorded": 1,
    }
    assert engine.reconcile_migration_checkpoints() == {
        "configured": 1,
        "recorded": 0,
    }
    checkpoint = engine.state()["verified_plan_checkpoints"][0]
    assert checkpoint["plan_alias"] == "FF-SIX"
    assert checkpoint["verified"] is True
