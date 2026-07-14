"""Tests for TC-MA2-PIPE-001: sprint prompt sourced from next-work-items.json.

Verifies:
  - Task titles in generated packet come from NWI item_ids
  - No fixture path appears in task descriptions
  - Empty NWI surfaces "NO GOVERNED PRODUCT WORK" sentinel
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))


def _make_repo(tmp_path: Path, nwi_items: list[dict] | None = None) -> Path:
    """Build a minimal fake repo tree with the files generate_supervisor_packet needs."""
    repo = tmp_path / "repo"
    repo.mkdir()

    # Required directories
    for d in [
        ".local/supervisor",
        ".supervisor",
        "reports/supervisor",
        "reports/r90",
    ]:
        (repo / d).mkdir(parents=True, exist_ok=True)

    # next-work-items.json
    nwi_path = repo / ".local/supervisor/next-work-items.json"
    if nwi_items is not None:
        nwi_path.write_text(json.dumps({"items": nwi_items}), encoding="utf-8")
    # else: leave absent → empty case

    # Minimal continuation-signal.json (needed by generate_supervisor_packet)
    sig = {
        "autonomous_continue": True,
        "iteration": 1,
        "max_iterations": 12,
        "rework_items": [],
        "stop_reason": None,
        "safe_lanes_available": True,
        "continuation_state": "YES",
        "continuation_reason_codes": [],
    }
    (repo / ".local/supervisor/continuation-signal.json").write_text(
        json.dumps(sig), encoding="utf-8"
    )

    # Minimal approval-gates.md
    (repo / "reports/supervisor/approval-gates.md").write_text(
        "## Approval Gates\nAUTONOMOUS_CONTINUE: YES\n", encoding="utf-8"
    )

    # Minimal product-code-change-ledger.json
    (repo / "reports/r90/product-code-change-ledger.json").write_text(
        json.dumps({"status": "ok", "items": []}), encoding="utf-8"
    )

    # Minimal skill-registry.yaml stub
    (repo / ".supervisor/skill-registry.yaml").write_text(
        "registry_id: test\nskills: []\nversion: '1.0'\nsprint: test\n",
        encoding="utf-8",
    )

    return repo


def _call_build_tasks(repo: Path) -> list[dict]:
    """Import and call synthesize_sprint_tasks with a minimal review dict."""
    import importlib
    import generate_supervisor_packet as gsp

    importlib.reload(gsp)

    review = {
        "autonomous_continue": True,
        "rework_items": [],
        "hard_stops_detected": [],
        "sprint_id": "TEST-SPRINT-001",
    }
    contradictions: dict = {}
    tasks = gsp.synthesize_sprint_tasks(review, contradictions, repo)
    return tasks


# ---------------------------------------------------------------------------
# TC-MA2-PIPE-001-01 / -05: Tasks sourced from NWI
# ---------------------------------------------------------------------------


def test_tasks_sourced_from_nwi(tmp_path: Path) -> None:
    """TC-MA2-PIPE-001: Tasks in packet come from next-work-items.json item_ids."""
    items = [
        {
            "item_id": "WI-GAP-TEST-001",
            "title": "Implement foo for TEST",
            "lane": "product",
            "priority": 1,
            "description": "Do foo for TEST format.",
            "acceptance_criteria": "pytest tests/ -q",
        },
        {
            "item_id": "WI-GAP-TEST-002",
            "title": "Implement bar for TEST",
            "lane": "product",
            "priority": 2,
            "description": "Do bar for TEST format.",
            "acceptance_criteria": "pytest tests/ -q",
        },
    ]
    repo = _make_repo(tmp_path, nwi_items=items)
    tasks = _call_build_tasks(repo)

    product_tasks = [t for t in tasks if t.get("supervisor_task_ref", "").startswith("WI-GAP")]
    assert len(product_tasks) == 2

    item_ids_in_tasks = {t["supervisor_task_ref"] for t in product_tasks}
    assert "WI-GAP-TEST-001" in item_ids_in_tasks
    assert "WI-GAP-TEST-002" in item_ids_in_tasks


def test_no_fixture_path_in_task_descriptions(tmp_path: Path) -> None:
    """TC-MA2-PIPE-001: No fixture path appears in task descriptions."""
    items = [
        {
            "item_id": "WI-GAP-FIXTURE-CHECK-001",
            "title": "Check no fixture",
            "lane": "product",
            "priority": 1,
            "description": "Some governed task.",
            "acceptance_criteria": "pytest tests/ -q",
        }
    ]
    repo = _make_repo(tmp_path, nwi_items=items)
    tasks = _call_build_tasks(repo)

    for task in tasks:
        desc = task.get("description", "") + task.get("ff_doc_ref", "")
        assert "fixtures" not in desc.lower(), (
            f"fixture path found in task {task.get('task_id')}: {desc[:200]}"
        )


def test_empty_nwi_surfaces_sentinel(tmp_path: Path) -> None:
    """TC-MA2-PIPE-001 REQ-PIPE-003: Empty NWI produces 'NO GOVERNED PRODUCT WORK'."""
    repo = _make_repo(tmp_path, nwi_items=[])
    tasks = _call_build_tasks(repo)

    sentinel_tasks = [t for t in tasks if "NO GOVERNED PRODUCT WORK" in t.get("title", "")]
    assert sentinel_tasks, "expected 'NO GOVERNED PRODUCT WORK' sentinel task when NWI is empty"
    assert sentinel_tasks[0]["status"] == "blocked"


def test_absent_nwi_surfaces_sentinel(tmp_path: Path) -> None:
    """TC-MA2-PIPE-001: Absent next-work-items.json produces the sentinel task."""
    repo = _make_repo(tmp_path, nwi_items=None)
    # Don't create the NWI file
    tasks = _call_build_tasks(repo)

    sentinel_tasks = [t for t in tasks if "NO GOVERNED PRODUCT WORK" in t.get("title", "")]
    assert sentinel_tasks, "expected sentinel task when next-work-items.json absent"
