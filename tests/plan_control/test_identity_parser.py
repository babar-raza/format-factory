from pathlib import Path

from tools.plan_control.identity import stable_plan_id
from tools.plan_control.models import ExecutionState, parse_execution_state
from tools.plan_control.parser import parse_plan


def test_identity_survives_rename_and_status_change(tmp_path: Path) -> None:
    first = tmp_path / "first.md"
    second = tmp_path / "renamed.md"
    first.write_text(
        "---\nartifact_id: MISSION-1\nstatus: IN_PROGRESS\n---\n# Plan\n",
        encoding="utf-8",
    )
    second.write_text(
        "---\nartifact_id: MISSION-1\nstatus: COMPLETE\n---\n# Plan\n",
        encoding="utf-8",
    )
    assert parse_plan(first).plan_id == parse_plan(second).plan_id


def test_identity_without_alias_uses_title_and_task_ids() -> None:
    first = stable_plan_id(
        repository_id="repo",
        aliases=[],
        title="Alpha",
        task_ids=["TC-A-1"],
        content="**Status:** READY",
    )
    second = stable_plan_id(
        repository_id="repo",
        aliases=[],
        title="Alpha",
        task_ids=["TC-A-1"],
        content="**Status:** COMPLETE",
    )
    assert first == second


def test_parser_supports_heading_table_and_checklist(tmp_path: Path) -> None:
    plan = tmp_path / "plan.md"
    plan.write_text(
        """---
artifact_id: PARSER-1
status: IN_PROGRESS
---
# Parser Plan
### TC-HEAD-001 — Heading task
**Status:** READY

| Task ID | Title | Status |
|---|---|---|
| TC-TABLE-001 | Table task | BLOCKED |

- [ ] Free checklist task
- [x] TC-CHECK-001 checked task
""",
        encoding="utf-8",
    )
    parsed = parse_plan(plan)
    states = {task.external_id: task.state for task in parsed.tasks}
    assert states["TC-HEAD-001"] == ExecutionState.READY
    assert states["TC-TABLE-001"] == ExecutionState.BLOCKED
    assert states["TC-CHECK-001"] == ExecutionState.COMPLETE
    assert any(task_id.startswith("CHK-") for task_id in states)


def test_superseded_is_never_an_execution_state(tmp_path: Path) -> None:
    state, warning = parse_execution_state("SUPERSEDED")
    assert state == ExecutionState.BLOCKED
    assert warning == "SUPERSEDED_IS_AUTHORITY_NOT_EXECUTION_STATE"
    plan = tmp_path / "plan.md"
    plan.write_text(
        "# Plan\n### TC-X-001 — Invalid\n**Status:** SUPERSEDED\n",
        encoding="utf-8",
    )
    task = parse_plan(plan).tasks[0]
    assert task.state == ExecutionState.BLOCKED
    assert "SUPERSEDED_IS_AUTHORITY_NOT_EXECUTION_STATE" in task.warnings
