"""
test_multi_format_acquisition_planner.py -- Lane E Tests (FORMAT-FACTORY-R10)

Tests for multi_format_acquisition_planner.py.

COVERAGE:
  - plan_format_group: structure, determinism, required keys, governance
  - plan_all_groups: all groups present, aggregate structure
  - plan_active_and_candidate_groups: smoke test
  - get_group_definition: lookup + not found
  - Sequencing recommendations
  - Blocker detection
  - Governance invariants

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from multi_format_acquisition_planner import (
    plan_format_group,
    plan_all_groups,
    plan_active_and_candidate_groups,
    get_group_definition,
    FORMAT_GROUPS,
    ALL_GROUP_NAMES,
    GROUP_ACTIVE_FORMATS,
    GROUP_KOREAN_WORD_PROCESSING,
    GROUP_ARCHIVE,
    GROUP_DOCUMENT,
    GROUP_IMAGE,
    _GOVERNANCE_FLAGS,
    _stable_hash,
)


# ---------------------------------------------------------------------------
# Constants / structure
# ---------------------------------------------------------------------------

class TestConstants:
    def test_all_group_names_non_empty(self):
        assert len(ALL_GROUP_NAMES) >= 5

    def test_all_group_names_in_format_groups(self):
        for name in ALL_GROUP_NAMES:
            assert name in FORMAT_GROUPS

    def test_format_groups_have_required_keys(self):
        required = {"description", "formats", "lifecycle_state", "audit_state",
                    "spec_type", "priority", "parallelizable"}
        for name, grp in FORMAT_GROUPS.items():
            missing = required - set(grp.keys())
            assert not missing, f"{name} missing: {missing}"

    def test_active_formats_group_has_fods_fodt(self):
        assert "fods" in FORMAT_GROUPS[GROUP_ACTIVE_FORMATS]["formats"]
        assert "fodt" in FORMAT_GROUPS[GROUP_ACTIVE_FORMATS]["formats"]

    def test_korean_group_has_hwp_hwpx_hwt(self):
        grp = FORMAT_GROUPS[GROUP_KOREAN_WORD_PROCESSING]["formats"]
        assert "hwp" in grp
        assert "hwpx" in grp
        assert "hwt" in grp

    def test_archive_group_has_alz_egg(self):
        grp = FORMAT_GROUPS[GROUP_ARCHIVE]["formats"]
        assert "alz" in grp
        assert "egg" in grp

    def test_document_group_has_gnumeric_abw(self):
        grp = FORMAT_GROUPS[GROUP_DOCUMENT]["formats"]
        assert "gnumeric" in grp
        assert "abw" in grp

    def test_image_group_has_wmf_emf(self):
        grp = FORMAT_GROUPS[GROUP_IMAGE]["formats"]
        assert "wmf" in grp
        assert "emf" in grp

    def test_active_formats_is_evidence_ready(self):
        assert FORMAT_GROUPS[GROUP_ACTIVE_FORMATS]["lifecycle_state"] == "EVIDENCE_READY"

    def test_candidate_groups_are_candidate_state(self):
        for name in [GROUP_KOREAN_WORD_PROCESSING, GROUP_ARCHIVE, GROUP_DOCUMENT, GROUP_IMAGE]:
            assert FORMAT_GROUPS[name]["lifecycle_state"] == "CANDIDATE"


# ---------------------------------------------------------------------------
# _stable_hash
# ---------------------------------------------------------------------------

class TestStableHash:
    def test_deterministic(self):
        assert _stable_hash({"a": 1}) == _stable_hash({"a": 1})

    def test_length_16(self):
        h = _stable_hash("test")
        assert len(h) == 16
        int(h, 16)  # must be valid hex

    def test_different_inputs_different_hash(self):
        assert _stable_hash({"a": 1}) != _stable_hash({"a": 2})


# ---------------------------------------------------------------------------
# plan_format_group
# ---------------------------------------------------------------------------

class TestPlanFormatGroup:
    def _active_plan(self):
        return plan_format_group(GROUP_ACTIVE_FORMATS)

    def _korean_plan(self):
        return plan_format_group(GROUP_KOREAN_WORD_PROCESSING)

    def _archive_plan(self):
        return plan_format_group(GROUP_ARCHIVE)

    def test_required_keys_present(self):
        r = self._active_plan()
        for key in ["plan_id", "group_name", "formats", "format_count",
                    "lifecycle_state", "spec_type", "parallelizable",
                    "sequencing_recommendation", "estimated_sprint_count",
                    "gates_remaining", "blockers", "recommendations",
                    "notes", "governance", "dry_run_only", "plan_note"]:
            assert key in r, f"Missing: {key}"

    def test_group_name_in_result(self):
        r = self._active_plan()
        assert r["group_name"] == GROUP_ACTIVE_FORMATS

    def test_formats_list_non_empty(self):
        r = self._active_plan()
        assert len(r["formats"]) >= 2

    def test_format_count_matches_formats(self):
        r = self._active_plan()
        assert r["format_count"] == len(r["formats"])

    def test_plan_id_is_hex(self):
        r = self._active_plan()
        int(r["plan_id"], 16)

    def test_determinism(self):
        r1 = self._active_plan()
        r2 = self._active_plan()
        assert r1["plan_id"] == r2["plan_id"]
        assert r1["estimated_sprint_count"] == r2["estimated_sprint_count"]

    def test_cross_group_different_plan_ids(self):
        r_active = self._active_plan()
        r_korean = self._korean_plan()
        assert r_active["plan_id"] != r_korean["plan_id"]

    def test_dry_run_only_true(self):
        assert self._active_plan()["dry_run_only"] is True

    def test_plan_note_mentions_simulation(self):
        r = self._active_plan()
        note = r["plan_note"].upper()
        assert "SIMULATION" in note or "ESTIMATE" in note

    def test_governance_commercial_product_ready_false(self):
        r = self._active_plan()
        assert r["governance"]["commercial_product_ready"] is False

    def test_governance_autonomous_execution_false(self):
        r = self._active_plan()
        assert r["governance"]["autonomous_execution_allowed"] is False

    def test_governance_dry_run_only_true(self):
        r = self._active_plan()
        assert r["governance"]["dry_run_only"] is True

    def test_governance_simulation_only_true(self):
        r = self._active_plan()
        assert r["governance"]["simulation_only"] is True

    def test_active_formats_has_fods_fodt(self):
        r = self._active_plan()
        assert "fods" in r["formats"]
        assert "fodt" in r["formats"]

    def test_active_formats_is_evidence_ready(self):
        r = self._active_plan()
        assert r["lifecycle_state"] == "EVIDENCE_READY"

    def test_active_formats_gates_remaining_is_one(self):
        r = self._active_plan()
        assert r["gates_remaining"] == 1

    def test_active_formats_no_blockers(self):
        r = self._active_plan()
        assert r["blockers"] == []

    def test_korean_group_candidate_state(self):
        r = self._korean_plan()
        assert r["lifecycle_state"] == "CANDIDATE"

    def test_korean_group_not_parallelizable(self):
        r = self._korean_plan()
        assert r["parallelizable"] is False

    def test_archive_group_parallelizable(self):
        r = self._archive_plan()
        assert r["parallelizable"] is True

    def test_reverse_engineering_has_legal_review_blocker(self):
        r = self._archive_plan()
        assert "reverse_engineering_requires_legal_review" in r["blockers"]

    def test_sequencing_recommendation_non_empty(self):
        r = self._korean_plan()
        assert len(r["sequencing_recommendation"]) > 0

    def test_sequencing_has_format_and_rationale(self):
        r = self._korean_plan()
        for item in r["sequencing_recommendation"]:
            assert "format" in item
            assert "rationale" in item

    def test_hwpx_first_in_korean_sequencing(self):
        r = self._korean_plan()
        seq = r["sequencing_recommendation"]
        assert seq[0]["format"] == "hwpx"

    def test_estimated_sprint_count_positive_for_candidate(self):
        r = self._korean_plan()
        assert r["estimated_sprint_count"] > 0

    def test_active_formats_fewer_sprints_than_candidate(self):
        r_active = self._active_plan()
        r_korean = self._korean_plan()
        assert r_active["estimated_sprint_count"] <= r_korean["estimated_sprint_count"]

    def test_recommendations_are_plan_rec_prefixed(self):
        r = self._archive_plan()
        for rec in r["recommendations"]:
            assert rec.startswith("[PLAN-REC]"), f"Non-PLAN-REC: {rec}"

    def test_json_serializable(self):
        r = self._active_plan()
        json.dumps(r)

    def test_custom_formats_override(self):
        r = plan_format_group(
            "custom_test_group",
            formats=["fmt_a", "fmt_b"],
            lifecycle_state="CANDIDATE",
            spec_type="full_public",
            parallelizable=True,
        )
        assert r["group_name"] == "custom_test_group"
        assert "fmt_a" in r["formats"]
        assert "fmt_b" in r["formats"]

    def test_no_spec_adds_blocker(self):
        r = plan_format_group(
            "no_spec_test",
            formats=["fmt_x"],
            lifecycle_state="CANDIDATE",
            spec_type="none",
        )
        assert "no_spec_available" in r["blockers"]

    def test_blocked_state_adds_blocker(self):
        r = plan_format_group(
            "blocked_test",
            formats=["fmt_y"],
            lifecycle_state="BLOCKED",
            spec_type="full_public",
        )
        assert "group_in_blocked_state" in r["blockers"]

    def test_deferred_state_adds_blocker(self):
        r = plan_format_group(
            "deferred_test",
            formats=["fmt_z"],
            lifecycle_state="DEFERRED",
            spec_type="full_public",
        )
        assert "group_in_deferred_state" in r["blockers"]


# ---------------------------------------------------------------------------
# plan_all_groups
# ---------------------------------------------------------------------------

class TestPlanAllGroups:
    def _run(self):
        return plan_all_groups()

    def test_required_keys_present(self):
        r = self._run()
        for key in ["aggregate_plan_id", "groups_planned", "per_group",
                    "total_formats_covered", "total_format_count",
                    "groups_with_blockers", "groups_near_ready",
                    "all_groups_ready", "governance", "dry_run_only", "plan_note"]:
            assert key in r, f"Missing: {key}"

    def test_all_group_names_present(self):
        r = self._run()
        for name in ALL_GROUP_NAMES:
            assert name in r["per_group"]

    def test_groups_planned_is_sorted(self):
        r = self._run()
        assert r["groups_planned"] == sorted(r["groups_planned"])

    def test_total_formats_covered_non_empty(self):
        r = self._run()
        assert len(r["total_formats_covered"]) > 0

    def test_total_format_count_matches(self):
        r = self._run()
        assert r["total_format_count"] == len(r["total_formats_covered"])

    def test_fods_fodt_in_total_formats(self):
        r = self._run()
        assert "fods" in r["total_formats_covered"]
        assert "fodt" in r["total_formats_covered"]

    def test_hwp_hwpx_in_total_formats(self):
        r = self._run()
        assert "hwp" in r["total_formats_covered"]
        assert "hwpx" in r["total_formats_covered"]

    def test_alz_egg_in_total_formats(self):
        r = self._run()
        assert "alz" in r["total_formats_covered"]
        assert "egg" in r["total_formats_covered"]

    def test_aggregate_plan_id_is_hex(self):
        r = self._run()
        int(r["aggregate_plan_id"], 16)

    def test_determinism(self):
        r1 = self._run()
        r2 = self._run()
        assert r1["aggregate_plan_id"] == r2["aggregate_plan_id"]

    def test_governance_commercial_product_ready_false(self):
        r = self._run()
        assert r["governance"]["commercial_product_ready"] is False

    def test_dry_run_only_true(self):
        r = self._run()
        assert r["dry_run_only"] is True

    def test_per_group_each_has_plan_id(self):
        r = self._run()
        for name in ALL_GROUP_NAMES:
            assert "plan_id" in r["per_group"][name]

    def test_groups_with_blockers_are_valid_group_names(self):
        r = self._run()
        for name in r["groups_with_blockers"]:
            assert name in ALL_GROUP_NAMES

    def test_active_formats_not_in_groups_with_blockers(self):
        r = self._run()
        # active formats are EVIDENCE_READY, should not have blockers
        assert GROUP_ACTIVE_FORMATS not in r["groups_with_blockers"]

    def test_all_groups_ready_is_bool(self):
        r = self._run()
        assert isinstance(r["all_groups_ready"], bool)

    def test_json_serializable(self):
        r = self._run()
        json.dumps(r)

    def test_plan_note_mentions_estimate(self):
        r = self._run()
        note = r["plan_note"].upper()
        assert "ESTIMATE" in note or "SIMULATION" in note


# ---------------------------------------------------------------------------
# plan_active_and_candidate_groups
# ---------------------------------------------------------------------------

class TestPlanActiveAndCandidateGroups:
    def test_returns_dict(self):
        r = plan_active_and_candidate_groups()
        assert isinstance(r, dict)

    def test_same_structure_as_plan_all_groups(self):
        r = plan_active_and_candidate_groups()
        assert "per_group" in r
        assert "aggregate_plan_id" in r

    def test_contains_all_groups(self):
        r = plan_active_and_candidate_groups()
        for name in ALL_GROUP_NAMES:
            assert name in r["per_group"]

    def test_governance_preserved(self):
        r = plan_active_and_candidate_groups()
        assert r["governance"]["no_internet_access"] is True


# ---------------------------------------------------------------------------
# get_group_definition
# ---------------------------------------------------------------------------

class TestGetGroupDefinition:
    def test_returns_dict_for_known_group(self):
        result = get_group_definition(GROUP_ACTIVE_FORMATS)
        assert isinstance(result, dict)
        assert "formats" in result

    def test_returns_none_for_unknown_group(self):
        result = get_group_definition("nonexistent_xyz_99999")
        assert result is None

    def test_returns_copy_not_reference(self):
        r1 = get_group_definition(GROUP_ARCHIVE)
        r1["formats"] = ["TAMPERED"]
        r2 = get_group_definition(GROUP_ARCHIVE)
        assert "TAMPERED" not in r2["formats"]


# ---------------------------------------------------------------------------
# Governance invariants
# ---------------------------------------------------------------------------

class TestGovernanceInvariants:
    def test_governance_flags_immutable(self):
        r = plan_format_group(GROUP_ACTIVE_FORMATS)
        r["governance"]["commercial_product_ready"] = True
        assert _GOVERNANCE_FLAGS["commercial_product_ready"] is False

    def test_all_plans_commercial_product_ready_false(self):
        r = plan_all_groups()
        assert r["governance"]["commercial_product_ready"] is False
        for name in ALL_GROUP_NAMES:
            assert r["per_group"][name]["governance"]["commercial_product_ready"] is False

    def test_no_plan_approves_gate_11(self):
        r = plan_all_groups()
        for name in ALL_GROUP_NAMES:
            gov = r["per_group"][name]["governance"]
            assert gov.get("gate_self_approval_allowed") is False

    def test_all_plans_dry_run_only_true(self):
        r = plan_all_groups()
        assert r["dry_run_only"] is True
        for name in ALL_GROUP_NAMES:
            assert r["per_group"][name]["dry_run_only"] is True
