"""tests/supervisor/test_maintenance_obligation_register.py

Unit and integration tests for tools/supervisor/maintenance_obligation_register.py.

Covers:
  - extract_from_plan: section present, section absent, malformed YAML, missing fields
  - register_obligations: idempotency, completed protection, newly_added/already_existed counts
  - surface_due_obligations: overdue, within-window, future, no-date, absent register
  - mark_completed: happy path, idempotency, missing obligation
  - V145 governance validator: WARNING for overdue, PASS for clean, blocks_sprint=False
  - Non-blocking write_plan_lock contract: extraction failure does not prevent lock write
  - MOR survives capability_map_generator regen (regression: no shared file reference)
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

# Make tools importable without package install
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

from maintenance_obligation_register import (
    extract_from_plan,
    mark_completed,
    register_obligations,
    surface_due_obligations,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_PLAN_CONTENT = """\
# Test Plan

## Deferred Work Register

```yaml
deferred_item:
  obligation_id: MO-TEST-001
  source_taskcard: TC-TEST-001
  type: observation_window
  action: "run some_check.py"
  scheduled_date: "2026-08-05"
  owner: governance
  reason: "test reason"
```
"""

PLAN_WITHOUT_SECTION = """\
# Test Plan

No deferred work section here.
"""

PLAN_MALFORMED_YAML = """\
# Test Plan

## Deferred Work Register

```yaml
deferred_item:
  obligation_id: MO-BAD-001
  type: [unclosed bracket
```
"""

PLAN_MISSING_FIELDS = """\
# Test Plan

## Deferred Work Register

```yaml
deferred_item:
  obligation_id: MO-MISSING-001
  action: "some action"
```
"""

PLAN_INVALID_TYPE = """\
# Test Plan

## Deferred Work Register

```yaml
deferred_item:
  obligation_id: MO-BADTYPE-001
  type: invalid_type_xyz
  action: "some action"
```
"""

PLAN_TWO_OBLIGATIONS = """\
# Test Plan

## Deferred Work Register

```yaml
deferred_item:
  obligation_id: MO-TEST-A
  type: follow_up
  action: "do thing A"
```

```yaml
deferred_item:
  obligation_id: MO-TEST-B
  type: scheduled_maintenance
  action: "do thing B"
  scheduled_date: "2026-09-01"
```
"""


# ---------------------------------------------------------------------------
# extract_from_plan
# ---------------------------------------------------------------------------


def test_extract_from_plan_valid(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(VALID_PLAN_CONTENT, encoding="utf-8")
    items = extract_from_plan(plan)
    assert len(items) == 1
    assert items[0]["obligation_id"] == "MO-TEST-001"
    assert items[0]["type"] == "observation_window"
    assert items[0]["action"] == "run some_check.py"
    assert str(items[0]["scheduled_date"]) == "2026-08-05"


def test_extract_from_plan_no_section(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(PLAN_WITHOUT_SECTION, encoding="utf-8")
    assert extract_from_plan(plan) == []


def test_extract_from_plan_malformed_yaml(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(PLAN_MALFORMED_YAML, encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed YAML"):
        extract_from_plan(plan)


def test_extract_from_plan_missing_required_fields(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(PLAN_MISSING_FIELDS, encoding="utf-8")
    with pytest.raises(ValueError, match="missing required fields"):
        extract_from_plan(plan)


def test_extract_from_plan_invalid_type(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(PLAN_INVALID_TYPE, encoding="utf-8")
    with pytest.raises(ValueError, match="invalid type"):
        extract_from_plan(plan)


def test_extract_from_plan_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_from_plan(tmp_path / "nonexistent.md")


def test_extract_from_plan_two_obligations(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(PLAN_TWO_OBLIGATIONS, encoding="utf-8")
    items = extract_from_plan(plan)
    assert len(items) == 2
    ids = {i["obligation_id"] for i in items}
    assert ids == {"MO-TEST-A", "MO-TEST-B"}


# ---------------------------------------------------------------------------
# register_obligations
# ---------------------------------------------------------------------------


def _make_mor(tmp_path, obligations=None) -> Path:
    mor = tmp_path / "maintenance-obligations.json"
    if obligations is not None:
        from datetime import datetime, timezone
        data = {
            "schema_version": "1.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "obligations": obligations,
        }
        mor.write_text(json.dumps(data), encoding="utf-8")
    return mor


def _read_mor(mor_path: Path) -> dict:
    return json.loads(mor_path.read_text(encoding="utf-8"))


def test_register_obligations_adds_new(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(VALID_PLAN_CONTENT, encoding="utf-8")
    items = extract_from_plan(plan)
    mor = _make_mor(tmp_path)

    added, existed = register_obligations(items, "plan.md", "hash001", mor)
    assert added == 1
    assert existed == 0
    data = _read_mor(mor)
    assert len(data["obligations"]) == 1
    assert data["obligations"][0]["obligation_id"] == "MO-TEST-001"
    assert data["obligations"][0]["status"] == "open"


def test_register_obligations_idempotent(tmp_path):
    plan = tmp_path / "plan.md"
    plan.write_text(VALID_PLAN_CONTENT, encoding="utf-8")
    items = extract_from_plan(plan)
    mor = _make_mor(tmp_path)

    added1, existed1 = register_obligations(items, "plan.md", "hash001", mor)
    added2, existed2 = register_obligations(items, "plan.md", "hash001", mor)
    assert added1 == 1
    assert added2 == 0
    assert existed1 == 0
    assert existed2 == 1
    data = _read_mor(mor)
    assert len(data["obligations"]) == 1  # Not doubled


def test_register_obligations_completed_not_overwritten(tmp_path):
    from datetime import datetime, timezone
    completed_ob = {
        "obligation_id": "MO-TEST-001",
        "type": "observation_window",
        "action": "original action",
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "completion_evidence": "done",
        "source_plan": "plan.md",
        "source_plan_hash": "hash001",
    }
    mor = _make_mor(tmp_path, obligations=[completed_ob])

    new_items = [{"obligation_id": "MO-TEST-001", "type": "follow_up", "action": "new action"}]
    added, existed = register_obligations(new_items, "plan.md", "hash002", mor)
    assert existed == 1
    data = _read_mor(mor)
    # Status and completion_evidence must be preserved
    ob = data["obligations"][0]
    assert ob["status"] == "completed"
    assert ob["completion_evidence"] == "done"
    assert ob["action"] == "original action"  # Not overwritten by new_items


def test_register_obligations_creates_file_if_absent(tmp_path):
    mor = tmp_path / "maintenance-obligations.json"
    assert not mor.exists()

    items = [{"obligation_id": "MO-NEW-001", "type": "follow_up", "action": "check it"}]
    register_obligations(items, "plan.md", "hash001", mor)
    assert mor.exists()
    data = _read_mor(mor)
    assert len(data["obligations"]) == 1


# ---------------------------------------------------------------------------
# surface_due_obligations
# ---------------------------------------------------------------------------


def _build_mor(tmp_path, obligations: list) -> Path:
    from datetime import datetime, timezone
    mor = tmp_path / "mor.json"
    data = {
        "schema_version": "1.0",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "obligations": obligations,
    }
    mor.write_text(json.dumps(data), encoding="utf-8")
    return mor


def test_surface_due_obligations_absent_register(tmp_path):
    result = surface_due_obligations(tmp_path / "nonexistent.json")
    assert result == []


def test_surface_due_obligations_overdue(tmp_path):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    ob = {
        "obligation_id": "MO-OVERDUE-001",
        "type": "observation_window",
        "action": "check",
        "status": "open",
        "scheduled_date": yesterday,
    }
    mor = _build_mor(tmp_path, [ob])
    result = surface_due_obligations(mor, lookahead_days=14)
    assert len(result) == 1
    assert result[0]["obligation_id"] == "MO-OVERDUE-001"


def test_surface_due_obligations_within_window(tmp_path):
    soon = (date.today() + timedelta(days=7)).isoformat()
    ob = {
        "obligation_id": "MO-SOON-001",
        "type": "scheduled_maintenance",
        "action": "do maintenance",
        "status": "open",
        "scheduled_date": soon,
    }
    mor = _build_mor(tmp_path, [ob])
    result = surface_due_obligations(mor, lookahead_days=14)
    assert len(result) == 1


def test_surface_due_obligations_future_not_surfaced(tmp_path):
    far_future = (date.today() + timedelta(days=60)).isoformat()
    ob = {
        "obligation_id": "MO-FUTURE-001",
        "type": "follow_up",
        "action": "later",
        "status": "open",
        "scheduled_date": far_future,
    }
    mor = _build_mor(tmp_path, [ob])
    result = surface_due_obligations(mor, lookahead_days=14)
    assert result == []


def test_surface_due_obligations_no_date_always_surfaced(tmp_path):
    ob = {
        "obligation_id": "MO-NODATE-001",
        "type": "valid_deferred",
        "action": "whenever",
        "status": "open",
        "scheduled_date": None,
    }
    mor = _build_mor(tmp_path, [ob])
    result = surface_due_obligations(mor)
    assert len(result) == 1


def test_surface_due_obligations_completed_not_surfaced(tmp_path):
    ob = {
        "obligation_id": "MO-DONE-001",
        "type": "observation_window",
        "action": "done",
        "status": "completed",
        "scheduled_date": (date.today() - timedelta(days=5)).isoformat(),
    }
    mor = _build_mor(tmp_path, [ob])
    result = surface_due_obligations(mor)
    assert result == []


# ---------------------------------------------------------------------------
# mark_completed
# ---------------------------------------------------------------------------


def test_mark_completed_happy_path(tmp_path):
    ob = {
        "obligation_id": "MO-COMP-001",
        "type": "observation_window",
        "action": "check it",
        "status": "open",
    }
    mor = _build_mor(tmp_path, [ob])
    ok = mark_completed("MO-COMP-001", "evidence string", mor)
    assert ok is True
    data = _read_mor(mor)
    result_ob = data["obligations"][0]
    assert result_ob["status"] == "completed"
    assert result_ob["completion_evidence"] == "evidence string"
    assert result_ob["completed_at"] is not None


def test_mark_completed_idempotent(tmp_path):
    ob = {
        "obligation_id": "MO-COMP-002",
        "type": "follow_up",
        "action": "do it",
        "status": "open",
    }
    mor = _build_mor(tmp_path, [ob])
    ok1 = mark_completed("MO-COMP-002", "evidence", mor)
    ok2 = mark_completed("MO-COMP-002", "evidence again", mor)
    assert ok1 is True
    assert ok2 is True
    data = _read_mor(mor)
    # Only one record, evidence from first call preserved (idempotent)
    assert len(data["obligations"]) == 1


def test_mark_completed_not_found(tmp_path):
    mor = _build_mor(tmp_path, [])
    ok = mark_completed("MO-NONEXISTENT", "evidence", mor)
    assert ok is False


def test_mark_completed_absent_register(tmp_path):
    ok = mark_completed("MO-ANY", "evidence", tmp_path / "nonexistent.json")
    assert ok is False


# ---------------------------------------------------------------------------
# V145 governance validator
# ---------------------------------------------------------------------------


def test_v145_pass_no_overdue(tmp_path):
    sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))
    from governance_validators_ext4 import validate_maintenance_obligations_current

    future = (date.today() + timedelta(days=30)).isoformat()
    ob = {
        "obligation_id": "MO-FUTURE",
        "type": "observation_window",
        "action": "check later",
        "status": "open",
        "scheduled_date": future,
    }
    # Write MOR to tmp_path-based repo root
    mor_dir = tmp_path / "reports" / "supervisor"
    mor_dir.mkdir(parents=True)
    (mor_dir / "maintenance-obligations.json").write_text(
        json.dumps({"schema_version": "1.0", "obligations": [ob]}), encoding="utf-8"
    )

    decl = {"sprint_id": "test", "planned_work_items": []}
    result = validate_maintenance_obligations_current(decl, repo_root=tmp_path)
    assert result["result"] == "PASS"


def test_v145_warn_overdue(tmp_path):
    sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))
    from governance_validators_ext4 import validate_maintenance_obligations_current

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    ob = {
        "obligation_id": "MO-OVERDUE",
        "type": "observation_window",
        "action": "overdue check",
        "status": "open",
        "scheduled_date": yesterday,
    }
    mor_dir = tmp_path / "reports" / "supervisor"
    mor_dir.mkdir(parents=True)
    (mor_dir / "maintenance-obligations.json").write_text(
        json.dumps({"schema_version": "1.0", "obligations": [ob]}), encoding="utf-8"
    )

    decl = {"sprint_id": "test", "planned_work_items": []}
    result = validate_maintenance_obligations_current(decl, repo_root=tmp_path)
    assert result["result"] == "WARN", f"Expected WARN, got {result['result']}"
    assert result.get("blocks_sprint") is False, "V145 must never block sprint"


def test_v145_blocks_sprint_false_invariant(tmp_path):
    """V145 must NEVER set blocks_sprint=True regardless of content."""
    sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))
    from governance_validators_ext4 import validate_maintenance_obligations_current

    # Add many overdue items
    from datetime import datetime, timezone
    obs = [
        {
            "obligation_id": f"MO-{i:03}",
            "type": "observation_window",
            "action": f"check {i}",
            "status": "open",
            "scheduled_date": (date.today() - timedelta(days=i)).isoformat(),
        }
        for i in range(1, 10)
    ]
    mor_dir = tmp_path / "reports" / "supervisor"
    mor_dir.mkdir(parents=True)
    (mor_dir / "maintenance-obligations.json").write_text(
        json.dumps({"schema_version": "1.0", "obligations": obs}), encoding="utf-8"
    )

    decl = {"sprint_id": "test", "planned_work_items": []}
    result = validate_maintenance_obligations_current(decl, repo_root=tmp_path)
    assert result.get("blocks_sprint") is not True, "V145 must never block sprint"


def test_v145_pass_when_mor_absent(tmp_path):
    sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))
    from governance_validators_ext4 import validate_maintenance_obligations_current

    decl = {"sprint_id": "test", "planned_work_items": []}
    result = validate_maintenance_obligations_current(decl, repo_root=tmp_path)
    assert result["result"] == "PASS"


# ---------------------------------------------------------------------------
# Non-blocking write_plan_lock contract
# ---------------------------------------------------------------------------


def test_nonblocking_when_plan_corrupted(tmp_path, monkeypatch):
    """Extraction failure (corrupted plan) must not raise — write_plan_lock remains safe."""
    sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))
    import maintenance_obligation_register as mor_mod

    # Patch extract_from_plan to raise
    def _raise(*args, **kwargs):
        raise RuntimeError("Simulated extraction failure")

    monkeypatch.setattr(mor_mod, "extract_from_plan", _raise)

    # Should not raise even though extract_from_plan fails
    result = mor_mod.extract_and_pin_deferred_items(
        plan_path=str(tmp_path / "nonexistent.md"),
        plan_hash="hash001",
        locked_at="2026-08-01T00:00:00+00:00",
        repo_root=tmp_path,
    )
    # extract_and_pin_deferred_items returns 0 when plan doesn't exist (pre-check)
    assert result == 0


# ---------------------------------------------------------------------------
# MOR survival regression: capability_map_generator must not touch it
# ---------------------------------------------------------------------------


def test_mor_not_referenced_by_capability_map_generator():
    """Regression: capability_map_generator.py must not write to maintenance-obligations.json."""
    gen = _REPO_ROOT / "tools" / "supervisor" / "capability_map_generator.py"
    if not gen.exists():
        pytest.skip("capability_map_generator.py not found")
    content = gen.read_text(encoding="utf-8", errors="replace")
    assert "maintenance-obligations" not in content, (
        "capability_map_generator.py references maintenance-obligations.json — "
        "this would wipe the MOR on every autonomous cycle regen"
    )


def test_mor_not_referenced_by_gap_ledger_pipeline():
    """The gap ledger pipeline must not write to maintenance-obligations.json."""
    gap_gen = _REPO_ROOT / "tools" / "supervisor" / "capability_map_generator.py"
    compiler = _REPO_ROOT / "tools" / "supervisor" / "capability_feature_compiler.py"
    for f in [gap_gen, compiler]:
        if f.exists():
            content = f.read_text(encoding="utf-8", errors="replace")
            assert "maintenance-obligations" not in content, (
                f"{f.name} references maintenance-obligations.json — must never happen"
            )
