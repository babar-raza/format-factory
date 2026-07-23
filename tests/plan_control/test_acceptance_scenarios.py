import json
from pathlib import Path

from tools.plan_control.engine import PlanControlEngine
from tools.plan_control.models import AuthorityMode, ExecutionState


def _write(repo: Path, name: str, body: str) -> Path:
    root = repo / "plans" / ".claude"
    root.mkdir(parents=True, exist_ok=True)
    path = root / name
    path.write_text(body, encoding="utf-8")
    return path


def test_no_lock_plan_remains_in_backlog(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "no-lock.md",
        "# No Lock\n### TC-NL-001 — Open\n**Status:** READY\n",
    )
    engine = PlanControlEngine(tmp_path)
    engine.reconcile(include_worktrees=False)
    assert [item["external_id"] for item in engine.queue()] == ["TC-NL-001"]


def test_incomplete_superseded_plan_remains_queued(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "superseded.md",
        """---
artifact_id: OLD-PLAN
authority_mode: SUPERSEDED
status: COMPLETE
---
# Old
### TC-OLD-001 — Still open
**Status:** READY
""",
    )
    engine = PlanControlEngine(tmp_path)
    engine.reconcile(include_worktrees=False)
    plan = engine.show("OLD-PLAN")
    assert plan["authority_mode"] == AuthorityMode.SUPERSEDED.value
    assert plan["execution_state"] == ExecutionState.ITERATION_REQUIRED.value
    assert engine.queue()[0]["external_id"] == "TC-OLD-001"


def test_completed_unlocked_plan_is_completion_candidate(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "complete.md",
        "---\nartifact_id: COMPLETE-PLAN\nstatus: COMPLETE\n---\n# Complete\n",
    )
    engine = PlanControlEngine(tmp_path)
    engine.reconcile(include_worktrees=False)
    assert (
        engine.show("COMPLETE-PLAN")["execution_state"]
        == ExecutionState.COMPLETION_CANDIDATE.value
    )


def test_clean_candidate_can_terminal_close_with_evidence(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "complete.md",
        "---\nartifact_id: COMPLETE-PLAN\nstatus: COMPLETE\n---\n# Complete\n",
    )
    engine = PlanControlEngine(tmp_path)
    engine.reconcile(include_worktrees=False)
    result = engine.transition_plan(
        "COMPLETE-PLAN",
        ExecutionState.TERMINAL_CLOSED,
        reason="audit pass",
        evidence={"digest": "verified"},
    )
    assert result["state"] == ExecutionState.TERMINAL_CLOSED.value


def test_failed_candidate_audit_routes_to_iteration_required(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "complete.md",
        "---\nartifact_id: COMPLETE-PLAN\nstatus: COMPLETE\n---\n# Complete\n",
    )
    engine = PlanControlEngine(tmp_path)
    engine.reconcile(include_worktrees=False)
    result = engine.transition_plan(
        "COMPLETE-PLAN",
        ExecutionState.ITERATION_REQUIRED,
        reason="audit failure",
    )
    assert result["state"] == ExecutionState.ITERATION_REQUIRED.value


def test_child_plan_stays_visible_under_canonical_master(tmp_path: Path) -> None:
    (tmp_path / "plans").mkdir()
    (tmp_path / "plans" / "master-plan.md").write_text(
        "---\nartifact_id: MASTER\n---\n# Master\n", encoding="utf-8"
    )
    _write(tmp_path, "child.md", "---\nartifact_id: CHILD\n---\n# Child\n")
    engine = PlanControlEngine(tmp_path)
    engine.reconcile(include_worktrees=False)
    aliases = {alias for plan in engine.list_records("plans") for alias in plan["aliases"]}
    assert aliases == {"MASTER", "CHILD"}


def test_direct_projection_edit_is_detected(tmp_path: Path) -> None:
    _write(tmp_path, "plan.md", "# Plan\n")
    engine = PlanControlEngine(tmp_path)
    engine.reconcile(include_worktrees=False)
    status = engine.paths.projection_root / "status.json"
    document = json.loads(status.read_text(encoding="utf-8"))
    document["plan_count"] = 999
    status.write_text(json.dumps(document), encoding="utf-8")
    assert "STALE_PROJECTION:status.json" in engine.doctor()["findings"]


def test_every_approved_file_has_exactly_one_occurrence(tmp_path: Path) -> None:
    files = [
        _write(tmp_path, f"plan-{index}.md", f"# Plan {index}\n")
        for index in range(5)
    ]
    engine = PlanControlEngine(tmp_path)
    result = engine.reconcile(include_worktrees=False)
    assert result["discover"]["canonical_plan_count"] == len(files)
    plans = engine.list_records("plans")
    assert len(plans) == len(files)
    assert all(len(plan["occurrences"]) == 1 for plan in plans)
