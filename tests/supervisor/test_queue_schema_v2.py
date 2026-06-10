"""Tests for queue item schema v2 validation.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-1-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

from action_queue import validate_item_schema_v2


def _make_valid_v2(**overrides):
    base = {
        "action_id": "q-abc12345",
        "action_type": "GENERATE_TASK_CANDIDATES",
        "stream": "autonomy",
        "priority": 3,
        "status": "pending",
        "objective": "Generate product task candidates from capability gaps",
        "allowed_paths": ["tools/supervisor/"],
        "forbidden_paths": ["src/net/"],
        "human_approval_required": False,
        "evidence_required": True,
    }
    base.update(overrides)
    return base


def _make_source_changing(**overrides):
    base = _make_valid_v2(
        action_type="IMPLEMENT_SMALL_PRODUCT_FEATURE",
        rollback_strategy="git checkout src/python/fodg/fodg_codec.py",
        expected_tests=["tests/python/fodg/test_r130_fodg_csv.py"],
        gate_classification="LOCAL_AUTONOMOUS",
    )
    base.update(overrides)
    return base


class TestValidItemPasses:
    def test_minimal_valid_item(self):
        item = _make_valid_v2()
        errors = validate_item_schema_v2(item)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_source_changing_item_passes(self):
        item = _make_source_changing()
        errors = validate_item_schema_v2(item)
        assert errors == [], f"Expected no errors, got: {errors}"

    def test_extra_fields_allowed(self):
        item = _make_valid_v2(sprint_id="SPR-001", target_path="src/python/fodg/")
        errors = validate_item_schema_v2(item)
        assert errors == []


class TestMissingRequiredFields:
    def test_missing_action_id(self):
        item = _make_valid_v2()
        del item["action_id"]
        errors = validate_item_schema_v2(item)
        assert any("missing required fields" in e for e in errors)

    def test_missing_allowed_paths(self):
        item = _make_valid_v2()
        del item["allowed_paths"]
        errors = validate_item_schema_v2(item)
        assert any("missing required fields" in e for e in errors)

    def test_missing_forbidden_paths(self):
        item = _make_valid_v2()
        del item["forbidden_paths"]
        errors = validate_item_schema_v2(item)
        assert any("missing required fields" in e for e in errors)

    def test_missing_human_approval_required(self):
        item = _make_valid_v2()
        del item["human_approval_required"]
        errors = validate_item_schema_v2(item)
        assert any("missing required fields" in e for e in errors)

    def test_missing_evidence_required(self):
        item = _make_valid_v2()
        del item["evidence_required"]
        errors = validate_item_schema_v2(item)
        assert any("missing required fields" in e for e in errors)

    def test_missing_objective(self):
        item = _make_valid_v2()
        del item["objective"]
        errors = validate_item_schema_v2(item)
        assert any("missing required fields" in e or "objective" in e for e in errors)


class TestTypeValidation:
    def test_priority_must_be_int(self):
        item = _make_valid_v2(priority="high")
        errors = validate_item_schema_v2(item)
        assert any("priority" in e for e in errors)

    def test_allowed_paths_must_be_list(self):
        item = _make_valid_v2(allowed_paths="src/python/")
        errors = validate_item_schema_v2(item)
        assert any("allowed_paths" in e for e in errors)

    def test_human_approval_required_must_be_bool(self):
        item = _make_valid_v2(human_approval_required="false")
        errors = validate_item_schema_v2(item)
        assert any("human_approval_required" in e for e in errors)

    def test_short_objective_rejected(self):
        item = _make_valid_v2(objective="do it")
        errors = validate_item_schema_v2(item)
        assert any("objective" in e for e in errors)


class TestStatusValidation:
    def test_invalid_status_rejected(self):
        item = _make_valid_v2(status="in-progress")
        errors = validate_item_schema_v2(item)
        assert any("status" in e for e in errors)

    def test_valid_statuses_accepted(self):
        for status in ("pending", "running", "done", "failed", "blocked"):
            item = _make_valid_v2(status=status)
            errors = validate_item_schema_v2(item)
            assert not any("status" in e for e in errors), \
                f"Status {status!r} should be valid, got errors: {errors}"


class TestSourceChangingSafety:
    def test_source_changing_requires_rollback(self):
        item = _make_source_changing()
        del item["rollback_strategy"]
        errors = validate_item_schema_v2(item)
        assert any("rollback_strategy" in e for e in errors)

    def test_source_changing_requires_expected_tests(self):
        item = _make_source_changing()
        del item["expected_tests"]
        errors = validate_item_schema_v2(item)
        assert any("expected_tests" in e for e in errors)

    def test_local_autonomous_must_not_require_approval(self):
        item = _make_source_changing(
            gate_classification="LOCAL_AUTONOMOUS",
            human_approval_required=True,
        )
        errors = validate_item_schema_v2(item)
        assert any("human_approval_required" in e for e in errors)

    def test_local_autonomous_no_approval_passes(self):
        item = _make_source_changing(
            gate_classification="LOCAL_AUTONOMOUS",
            human_approval_required=False,
        )
        errors = validate_item_schema_v2(item)
        assert errors == []
