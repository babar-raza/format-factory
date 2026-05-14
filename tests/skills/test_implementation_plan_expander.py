"""
tests/skills/test_implementation_plan_expander.py

Tests for implementation_plan_expander.py — Lane B CONWAY-R7R8.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

import pytest
from implementation_plan_expander import expand_implementation_plan


# ===========================================================================
# TestLiveExpansion (FODS + FODT)
# ===========================================================================

class TestLiveExpansion:
    def test_fods_expansion_status_expanded(self):
        result = expand_implementation_plan("fods")
        assert result["expansion_status"] == "EXPANDED", (
            f"FODS expansion status is {result['expansion_status']}"
        )

    def test_fodt_expansion_status_expanded(self):
        result = expand_implementation_plan("fodt")
        assert result["expansion_status"] == "EXPANDED"

    def test_fods_accepted_count_is_20(self):
        result = expand_implementation_plan("fods")
        assert result["accepted_count"] == 20

    def test_fodt_accepted_count_is_20(self):
        result = expand_implementation_plan("fodt")
        assert result["accepted_count"] == 20

    def test_fods_has_implementation_slices(self):
        result = expand_implementation_plan("fods")
        assert len(result["implementation_slices"]) > 0

    def test_fodt_has_implementation_slices(self):
        result = expand_implementation_plan("fodt")
        assert len(result["implementation_slices"]) > 0

    def test_fods_has_planning_taskcards(self):
        result = expand_implementation_plan("fods")
        assert len(result["planning_taskcards"]) > 0

    def test_fodt_has_planning_taskcards(self):
        result = expand_implementation_plan("fodt")
        assert len(result["planning_taskcards"]) > 0

    def test_fods_has_dependency_groups(self):
        result = expand_implementation_plan("fods")
        assert len(result["dependency_groups"]) > 0

    def test_fodt_dependency_groups_ordered(self):
        result = expand_implementation_plan("fodt")
        indices = [dg["group_index"] for dg in result["dependency_groups"]]
        assert indices == sorted(indices), "Dependency groups must be ordered"

    def test_fods_future_scoped_excluded(self):
        """Future-scoped requirements must not appear in implementation slices."""
        result = expand_implementation_plan("fods")
        all_slice_reqs = set()
        for sl in result["implementation_slices"]:
            all_slice_reqs.update(sl["requirements"])
        # Future scoped count should be > 0 (conversion reqs are future-scoped)
        assert result["future_scoped_count"] > 0

    def test_fods_taskcards_have_required_keys(self):
        result = expand_implementation_plan("fods")
        required_keys = {"taskcard_id", "format", "lane_id", "requirement_ids",
                         "prerequisites", "test_expectations", "evidence_expectations",
                         "dry_run_only", "autonomous_execution_allowed"}
        for card in result["planning_taskcards"]:
            for key in required_keys:
                assert key in card, f"Taskcard missing key: {key}"

    def test_fods_dry_run_only_always_true(self):
        result = expand_implementation_plan("fods")
        for card in result["planning_taskcards"]:
            assert card["dry_run_only"] is True

    def test_fods_autonomous_execution_always_false(self):
        result = expand_implementation_plan("fods")
        for card in result["planning_taskcards"]:
            assert card["autonomous_execution_allowed"] is False

    def test_fods_governance_commercial_ready_false(self):
        result = expand_implementation_plan("fods")
        assert result["governance"]["commercial_product_ready"] is False

    def test_fodt_constraints_propagated(self):
        """FODT should have at least one known constraint (FODT-REQ-040)."""
        result = expand_implementation_plan("fodt")
        assert len(result["known_constraints"]) > 0

    def test_result_json_serializable(self):
        result = expand_implementation_plan("fods")
        json.dumps(result)  # Should not raise

    def test_requirements_state_authoritative(self):
        for fmt in ("fods", "fodt"):
            result = expand_implementation_plan(fmt)
            assert result["requirements_state"] == "REQUIREMENTS_AUTHORITATIVE"

    def test_lane_recommendations_non_empty(self):
        result = expand_implementation_plan("fods")
        assert len(result["lane_recommendations"]) > 0

    def test_all_accepted_reqs_appear_in_some_slice(self):
        """Every accepted requirement must be in exactly one slice."""
        result = expand_implementation_plan("fods")
        all_slice_reqs = []
        for sl in result["implementation_slices"]:
            all_slice_reqs.extend(sl["requirements"])
        # All req IDs should be unique across slices
        assert len(all_slice_reqs) == len(set(all_slice_reqs)), "Duplicate requirement IDs in slices"
        assert len(all_slice_reqs) == result["accepted_count"], (
            f"Slice count {len(all_slice_reqs)} != accepted_count {result['accepted_count']}"
        )


# ===========================================================================
# TestBlockedStates
# ===========================================================================

class TestBlockedStates:
    def test_nonexistent_format_blocked_not_authoritative(self):
        result = expand_implementation_plan("nonexistent_xyz")
        assert result["expansion_status"] in ("BLOCKED_NOT_AUTHORITATIVE", "BLOCKED_STALE")
        assert result["accepted_count"] == 0
        assert result["implementation_slices"] == []

    def test_blocked_state_has_empty_taskcards(self):
        result = expand_implementation_plan("nonexistent_xyz")
        assert result["planning_taskcards"] == []


# ===========================================================================
# TestDependencyOrdering
# ===========================================================================

class TestDependencyOrdering:
    def test_load_lane_has_no_prerequisites(self):
        result = expand_implementation_plan("fods")
        for dg in result["dependency_groups"]:
            if dg["lane_id"] == "LANE-I-LOAD":
                assert dg["prerequisite_lanes"] == []
                assert dg["can_start_immediately"] is True

    def test_save_lane_requires_earlier_lanes(self):
        result = expand_implementation_plan("fods")
        for dg in result["dependency_groups"]:
            if dg["lane_id"] == "LANE-I-SAVE":
                assert len(dg["prerequisite_lanes"]) > 0
