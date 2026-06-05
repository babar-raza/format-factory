"""Tests for choose_skill_or_handoff.py v2/v3/v4 — skill registry, new decisions, work-type, UNSAFE_SCOPE, source_track."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from choose_skill_or_handoff import (
    choose_skill_or_handoff,
    classify_work_type,
    classify_source_track,
    _match_skill_registry,
    UNSAFE_SCOPE_PATTERNS,
)


def test_external_gate_escalation():
    gap = {"capability_path": "blockers.1", "description": "Gate 11 G11-G: requires approval", "current_status": "BLOCKED"}
    result = choose_skill_or_handoff(gap)
    assert result["decision"] == "EXTERNAL_GATE_ESCALATION"
    assert result["external_gate"] is True


def test_dogfood_skill():
    gap = {"capability_path": "dogfood_status.fods_to_csv", "description": "export using dogfood", "current_status": "GAP_DOGFOOD_EXTERNAL"}
    result = choose_skill_or_handoff(gap)
    assert result["decision"] == "GOVERNED_SKILL_REQUIRED"
    assert result["governed_skill"] == "governed-dogfood-export"


def test_installed_workflow_read_only():
    gap = {"capability_path": "python_status.installed_workflow", "description": "verify installed workflow", "current_status": "PARTIAL"}
    result = choose_skill_or_handoff(gap)
    # Should match installed-workflow rule, not read-only
    assert result["decision"] == "GOVERNED_SKILL_REQUIRED"
    assert result["governed_skill"] == "governed-installed-workflow-verification"


def test_plan_hardening_for_new_file():
    gap = {"capability_path": "dogfood_status.fods_to_html", "description": "create new export file using dogfood", "current_status": "GAP_DOGFOOD_EXTERNAL"}
    result = choose_skill_or_handoff(gap)
    assert result["decision"] == "NEED_PLAN_HARDENING"
    assert result["governed_skill"] is not None


def test_read_only_verify():
    gap = {"capability_path": "status.check_config", "description": "verify configuration", "current_status": "NOT_YET"}
    result = choose_skill_or_handoff(gap)
    assert result["decision"] == "READ_ONLY_VERIFY"


def test_fallback_handoff():
    gap = {"capability_path": "unknown.something", "description": "something unusual", "current_status": "NOT_IMPLEMENTED"}
    result = choose_skill_or_handoff(gap)
    assert result["decision"] == "GOVERNED_HANDOFF_REQUIRED"
    assert result["handoff_required"] is True


def test_skill_registry_match():
    registry = {
        "skills": [
            {
                "skill_id": "add-dotnet-api",
                "status": "active",
                "purpose": "Add or extend one bounded commercial .NET product API with focused tests and evidence.",
                "product_track": "commercial_dotnet",
            }
        ]
    }
    gap = {"capability_path": "dotnet_status.some_api", "description": "Add one bounded commercial .NET product API", "current_status": "NOT_IMPLEMENTED"}
    result = choose_skill_or_handoff(gap, skill_registry=registry)
    assert result["decision"] == "GOVERNED_SKILL_REQUIRED"
    assert result["governed_skill"] == "add-dotnet-api"


def test_match_skill_registry_no_match():
    registry = {
        "skills": [
            {"skill_id": "add-dotnet-api", "status": "active", "purpose": "specific dotnet work"}
        ]
    }
    result = _match_skill_registry("completely unrelated text", registry)
    assert result is None


def test_match_skill_registry_inactive_skill():
    registry = {
        "skills": [
            {"skill_id": "disabled-skill", "status": "inactive", "purpose": "matching words text here"}
        ]
    }
    result = _match_skill_registry("matching words text here", registry)
    assert result is None


def test_backward_compatibility_no_registry():
    gap = {"capability_path": "dogfood_status.x", "description": "dogfood export", "current_status": "GAP_DOGFOOD_EXTERNAL"}
    result = choose_skill_or_handoff(gap)
    assert result["decision"] == "GOVERNED_SKILL_REQUIRED"
    assert result["governed_skill"] == "governed-dogfood-export"


# --- v3 (R100): work-type classification tests ---


def test_work_type_product_source_change():
    gap = {"capability_path": "api.save_document", "description": "write document to disk", "current_status": "NOT_IMPLEMENTED"}
    assert classify_work_type(gap) == "product_source_change"


def test_work_type_test_only_change():
    gap = {"capability_path": "tests.roundtrip", "description": "roundtrip regression hardening", "current_status": "NOT_STARTED"}
    assert classify_work_type(gap) == "test_only_change"


def test_work_type_docs_examples():
    gap = {"capability_path": "docs.readme", "description": "usage documentation example needed", "current_status": "NOT_YET"}
    assert classify_work_type(gap) == "docs_examples"


def test_work_type_package_proof():
    gap = {"capability_path": "packaging", "description": "build wheel and pip install", "current_status": "NOT_STARTED"}
    assert classify_work_type(gap) == "package_proof"


def test_work_type_dogfood_export():
    gap = {"capability_path": "dogfood.csv", "description": "dogfood export to CSV", "current_status": "GAP_DOGFOOD_EXTERNAL"}
    assert classify_work_type(gap) == "dogfood_export"


def test_work_type_supervisor_tooling():
    gap = {"capability_path": "tools.supervisor", "description": "acceleration tooling", "current_status": "NOT_STARTED"}
    assert classify_work_type(gap) == "supervisor_tooling"


def test_work_type_external_gate():
    gap = {"capability_path": "blockers.1", "description": "Gate 11 approval required", "current_status": "BLOCKED"}
    assert classify_work_type(gap) == "external_gate"


def test_work_type_dry_run_proof():
    gap = {"capability_path": "proof.dry_run", "description": "dry-run simulation", "current_status": "NOT_STARTED"}
    assert classify_work_type(gap) == "dry_run_proof"


def test_work_type_unknown():
    gap = {"capability_path": "misc.xyz", "description": "something completely different", "current_status": "PARTIAL"}
    assert classify_work_type(gap) == "unknown"


def test_work_type_in_decision_output():
    gap = {"capability_path": "api.save", "description": "save feature", "current_status": "NOT_IMPLEMENTED"}
    result = choose_skill_or_handoff(gap)
    assert "work_type" in result
    assert result["work_type"] == "product_source_change"


# --- v4 (R101): UNSAFE_SCOPE tests ---


def test_unsafe_scope_all_formats():
    """Positive: 'all formats' triggers UNSAFE_SCOPE."""
    gap = {"capability_path": "api.refactor", "description": "refactor all formats at once", "current_status": "NOT_IMPLEMENTED"}
    result = choose_skill_or_handoff(gap)
    assert result["decision"] == "UNSAFE_SCOPE"
    assert result["handoff_required"] is True


def test_unsafe_scope_global_refactor():
    """Positive: 'global refactor' triggers UNSAFE_SCOPE."""
    gap = {"capability_path": "api.change", "description": "global refactor of parsers", "current_status": "NOT_IMPLEMENTED"}
    result = choose_skill_or_handoff(gap)
    assert result["decision"] == "UNSAFE_SCOPE"


def test_unsafe_scope_bulk_rename():
    """Positive: 'bulk rename' triggers UNSAFE_SCOPE."""
    gap = {"capability_path": "api.rename", "description": "bulk rename all methods", "current_status": "NOT_IMPLEMENTED"}
    result = choose_skill_or_handoff(gap)
    assert result["decision"] == "UNSAFE_SCOPE"


def test_unsafe_scope_not_triggered():
    """Negative: normal gap does NOT trigger UNSAFE_SCOPE."""
    gap = {"capability_path": "api.save", "description": "save FODS to disk", "current_status": "NOT_IMPLEMENTED"}
    result = choose_skill_or_handoff(gap)
    assert result["decision"] != "UNSAFE_SCOPE"


def test_unsafe_scope_takes_priority_over_gate():
    """Positive: UNSAFE_SCOPE fires before EXTERNAL_GATE even when both match."""
    gap = {"capability_path": "blockers.1", "description": "all formats need approval", "current_status": "BLOCKED"}
    result = choose_skill_or_handoff(gap)
    assert result["decision"] == "UNSAFE_SCOPE"


# --- v4 (R101): source_track classification tests ---


def test_source_track_commercial_dotnet():
    gap = {"product_track": "commercial_net"}
    assert classify_source_track(gap) == "commercial_dotnet"


def test_source_track_foss_python():
    gap = {"product_track": "foss_reduced"}
    assert classify_source_track(gap) == "foss_python"


def test_source_track_unknown():
    gap = {"product_track": "something_else"}
    assert classify_source_track(gap) == "unknown"


def test_source_track_empty():
    gap = {}
    assert classify_source_track(gap) == "unknown"


def test_source_track_in_decision_output():
    """All decision outputs must include source_track."""
    gap = {"capability_path": "api.save", "description": "save", "current_status": "NOT_IMPLEMENTED",
           "product_track": "commercial_net"}
    result = choose_skill_or_handoff(gap)
    assert "source_track" in result
    assert result["source_track"] == "commercial_dotnet"


def test_source_track_in_unsafe_scope():
    gap = {"capability_path": "x", "description": "all formats refactor", "current_status": "NOT_IMPLEMENTED",
           "product_track": "foss_reduced"}
    result = choose_skill_or_handoff(gap)
    assert result["decision"] == "UNSAFE_SCOPE"
    assert result["source_track"] == "foss_python"


def test_source_track_in_external_gate():
    gap = {"capability_path": "blockers.1", "description": "Gate 11 approval", "current_status": "BLOCKED",
           "product_track": "commercial_net"}
    result = choose_skill_or_handoff(gap)
    assert result["source_track"] == "commercial_dotnet"


def test_source_track_in_handoff():
    gap = {"capability_path": "unknown.x", "description": "something unusual", "current_status": "NOT_IMPLEMENTED",
           "product_track": "foss_reduced"}
    result = choose_skill_or_handoff(gap)
    assert result["decision"] == "GOVERNED_HANDOFF_REQUIRED"
    assert result["source_track"] == "foss_python"
