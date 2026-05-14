"""
test_acquisition_planning_runtime.py -- R11 Lane E Tests
FORMAT-FACTORY-R11-ACQUISITION-PLANNING-INTEGRATION-SWARM-001

Integration tests for the unified acquisition planning runtime.
Ensures no fake integration, enforces governance invariants, and
validates cross-tool connectivity.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from acquisition_planning_runtime import (
    _GOVERNANCE_FLAGS,
    _TIER_MAP,
    _governance_copy,
    _stable_hash,
    run_acquisition_planning,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def default_bundle():
    """Return a default TIER_A planning bundle."""
    return run_acquisition_planning(tier="TIER_A", top_n=5, dry_run=True)


# ---------------------------------------------------------------------------
# Import integration tests (runtime imports all R10 tools)
# ---------------------------------------------------------------------------

class TestR10ToolImports:
    def test_runtime_imports_lifecycle_simulator(self):
        from acquisition_planning_runtime import (
            KNOWN_FORMAT_PROFILES,
            simulate_format_acquisition,
        )
        assert KNOWN_FORMAT_PROFILES is not None
        assert callable(simulate_format_acquisition)

    def test_runtime_imports_candidate_backlog(self):
        from acquisition_planning_runtime import (
            TIER_A_NEAR_TERM,
            get_candidates_by_tier,
        )
        assert TIER_A_NEAR_TERM == "TIER_A_NEAR_TERM"
        assert callable(get_candidates_by_tier)

    def test_runtime_imports_readiness_scorer(self):
        from acquisition_planning_runtime import (
            STANDARD_CANDIDATE_SPECS,
            score_multiple_formats,
        )
        assert isinstance(STANDARD_CANDIDATE_SPECS, list)
        assert callable(score_multiple_formats)

    def test_runtime_imports_planner(self):
        from acquisition_planning_runtime import plan_all_groups
        assert callable(plan_all_groups)

    def test_runtime_imports_simulation_v2(self):
        from acquisition_planning_runtime import simulate_v2
        assert callable(simulate_v2)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

class TestInputValidation:
    def test_invalid_tier_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown tier"):
            run_acquisition_planning(tier="TIER_NONEXISTENT")

    def test_tier_z_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown tier"):
            run_acquisition_planning(tier="Z")

    def test_empty_tier_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown tier"):
            run_acquisition_planning(tier="")

    def test_dry_run_false_raises_value_error(self):
        with pytest.raises(ValueError, match="dry_run must be True"):
            run_acquisition_planning(dry_run=False)

    def test_valid_tier_a_does_not_raise(self):
        result = run_acquisition_planning(tier="TIER_A")
        assert result is not None

    def test_valid_tier_b_does_not_raise(self):
        result = run_acquisition_planning(tier="TIER_B")
        assert result is not None

    def test_valid_tier_c_does_not_raise(self):
        result = run_acquisition_planning(tier="TIER_C")
        assert result is not None

    def test_valid_tier_active_does_not_raise(self):
        result = run_acquisition_planning(tier="TIER_ACTIVE")
        assert result is not None

    def test_all_valid_tiers_in_tier_map(self):
        assert "TIER_A" in _TIER_MAP
        assert "TIER_B" in _TIER_MAP
        assert "TIER_C" in _TIER_MAP
        assert "TIER_ACTIVE" in _TIER_MAP


# ---------------------------------------------------------------------------
# Output structure
# ---------------------------------------------------------------------------

class TestOutputStructure:
    def test_bundle_has_required_keys(self):
        result = default_bundle()
        required_keys = [
            "bundle_id", "tier", "top_n", "dry_run_only", "simulation_only",
            "candidate_ranking", "selected_first_candidate",
            "first_candidate_readiness_score", "first_candidate_rationale",
            "first_candidate_blockers", "first_candidate_required_evidence",
            "first_candidate_proposed_acquisition_lanes", "first_candidate_risks",
            "first_candidate_non_goals", "lifecycle_simulation",
            "simulation_graph_summary", "multi_format_plan", "governance",
            "next_recommended_sprint",
        ]
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"

    def test_bundle_id_is_string(self):
        result = default_bundle()
        assert isinstance(result["bundle_id"], str)
        assert len(result["bundle_id"]) == 16  # SHA-256 first 16 hex chars

    def test_tier_echoed_in_bundle(self):
        result = run_acquisition_planning(tier="TIER_A")
        assert result["tier"] == "TIER_A"

    def test_top_n_echoed_in_bundle(self):
        result = run_acquisition_planning(top_n=3)
        assert result["top_n"] == 3

    def test_candidate_ranking_is_list(self):
        result = default_bundle()
        assert isinstance(result["candidate_ranking"], list)

    def test_candidate_ranking_respects_top_n(self):
        result = run_acquisition_planning(top_n=3)
        assert len(result["candidate_ranking"]) <= 3

    def test_candidate_ranking_has_required_fields(self):
        result = default_bundle()
        for entry in result["candidate_ranking"]:
            assert "format_id" in entry
            assert "score" in entry
            assert "tier" in entry

    def test_candidate_ranking_is_sorted_descending(self):
        result = default_bundle()
        scores = [r["score"] for r in result["candidate_ranking"]]
        assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# First candidate
# ---------------------------------------------------------------------------

class TestFirstCandidate:
    def test_selected_first_candidate_is_string(self):
        result = default_bundle()
        assert isinstance(result["selected_first_candidate"], str)
        assert len(result["selected_first_candidate"]) > 0

    def test_selected_first_candidate_is_top_ranked(self):
        result = default_bundle()
        first_candidate = result["selected_first_candidate"]
        top_ranked = result["candidate_ranking"][0]["format_id"]
        assert first_candidate == top_ranked

    def test_first_candidate_readiness_score_is_numeric(self):
        result = default_bundle()
        score = result["first_candidate_readiness_score"]
        assert isinstance(score, (int, float))
        assert 0.0 <= score <= 10.0

    def test_first_candidate_rationale_is_nonempty_string(self):
        result = default_bundle()
        rationale = result["first_candidate_rationale"]
        assert isinstance(rationale, str)
        assert len(rationale) > 10

    def test_first_candidate_blockers_is_list(self):
        result = default_bundle()
        assert isinstance(result["first_candidate_blockers"], list)

    def test_first_candidate_required_evidence_is_list(self):
        result = default_bundle()
        assert isinstance(result["first_candidate_required_evidence"], list)

    def test_first_candidate_proposed_lanes_is_list(self):
        result = default_bundle()
        lanes = result["first_candidate_proposed_acquisition_lanes"]
        assert isinstance(lanes, list)
        assert len(lanes) > 0

    def test_first_candidate_risks_is_list(self):
        result = default_bundle()
        assert isinstance(result["first_candidate_risks"], list)

    def test_first_candidate_non_goals_is_list(self):
        result = default_bundle()
        assert isinstance(result["first_candidate_non_goals"], list)

    def test_first_candidate_non_goals_not_empty(self):
        result = default_bundle()
        assert len(result["first_candidate_non_goals"]) > 0

    def test_first_candidate_non_goals_include_gate11(self):
        result = default_bundle()
        combined = " ".join(result["first_candidate_non_goals"])
        assert "Gate 11" in combined or "gate_11" in combined.lower()

    def test_first_candidate_non_goals_include_product_ready(self):
        result = default_bundle()
        combined = " ".join(result["first_candidate_non_goals"])
        assert "commercial_product_ready" in combined


# ---------------------------------------------------------------------------
# Lifecycle simulation
# ---------------------------------------------------------------------------

class TestLifecycleSimulation:
    def test_lifecycle_simulation_is_dict(self):
        result = default_bundle()
        assert isinstance(result["lifecycle_simulation"], dict)

    def test_lifecycle_simulation_is_nonempty(self):
        result = default_bundle()
        assert len(result["lifecycle_simulation"]) > 0

    def test_lifecycle_simulation_has_format_id(self):
        result = default_bundle()
        sim = result["lifecycle_simulation"]
        first = result["selected_first_candidate"]
        assert sim.get("format_id") == first

    def test_lifecycle_simulation_has_current_state(self):
        result = default_bundle()
        assert "current_state" in result["lifecycle_simulation"]

    def test_lifecycle_simulation_has_dry_run_only_true(self):
        result = default_bundle()
        assert result["lifecycle_simulation"].get("dry_run_only") is True

    def test_lifecycle_simulation_has_governance(self):
        result = default_bundle()
        assert "governance" in result["lifecycle_simulation"]


# ---------------------------------------------------------------------------
# Simulation graph summary
# ---------------------------------------------------------------------------

class TestSimulationGraphSummary:
    def test_graph_summary_is_dict(self):
        result = default_bundle()
        assert isinstance(result["simulation_graph_summary"], dict)

    def test_graph_summary_is_nonempty(self):
        result = default_bundle()
        assert len(result["simulation_graph_summary"]) > 0

    def test_graph_summary_has_per_graph(self):
        result = default_bundle()
        assert "per_graph" in result["simulation_graph_summary"]

    def test_graph_summary_has_all_6_graph_types(self):
        result = default_bundle()
        per_graph = result["simulation_graph_summary"]["per_graph"]
        expected = {
            "dependency_graph", "taskcard_graph", "evidence_graph",
            "replay_lineage_graph", "stale_state_graph", "authority_graph",
        }
        assert set(per_graph.keys()) == expected

    def test_graph_summary_node_counts_positive(self):
        result = default_bundle()
        per_graph = result["simulation_graph_summary"]["per_graph"]
        for gtype, gdata in per_graph.items():
            assert gdata["node_count"] > 0, f"Zero nodes in {gtype}"

    def test_graph_summary_gate_11_approved_false(self):
        result = default_bundle()
        assert result["simulation_graph_summary"].get("gate_11_approved") is False


# ---------------------------------------------------------------------------
# Multi-format plan
# ---------------------------------------------------------------------------

class TestMultiFormatPlan:
    def test_multi_format_plan_is_dict(self):
        result = default_bundle()
        assert isinstance(result["multi_format_plan"], dict)

    def test_multi_format_plan_has_per_group(self):
        result = default_bundle()
        assert "per_group" in result["multi_format_plan"]

    def test_multi_format_plan_has_5_groups(self):
        result = default_bundle()
        per_group = result["multi_format_plan"]["per_group"]
        assert len(per_group) == 5

    def test_multi_format_plan_dry_run_only(self):
        result = default_bundle()
        assert result["multi_format_plan"].get("dry_run_only") is True

    def test_multi_format_plan_governance_commercial_product_ready_false(self):
        result = default_bundle()
        gov = result["multi_format_plan"].get("governance", {})
        assert gov.get("commercial_product_ready") is False


# ---------------------------------------------------------------------------
# Governance invariants
# ---------------------------------------------------------------------------

class TestGovernanceInvariants:
    def test_dry_run_only_is_true(self):
        result = default_bundle()
        assert result["dry_run_only"] is True

    def test_simulation_only_is_true(self):
        result = default_bundle()
        assert result["simulation_only"] is True

    def test_governance_commercial_product_ready_false(self):
        result = default_bundle()
        assert result["governance"]["commercial_product_ready"] is False

    def test_governance_autonomous_execution_allowed_false(self):
        result = default_bundle()
        assert result["governance"]["autonomous_execution_allowed"] is False

    def test_governance_gate_self_approval_allowed_false(self):
        result = default_bundle()
        assert result["governance"]["gate_self_approval_allowed"] is False

    def test_governance_no_source_mutation(self):
        result = default_bundle()
        assert result["governance"]["no_source_mutation"] is True

    def test_governance_no_internet_access(self):
        result = default_bundle()
        assert result["governance"]["no_internet_access"] is True

    def test_governance_dry_run_only_in_flags(self):
        result = default_bundle()
        assert result["governance"]["dry_run_only"] is True

    def test_governance_simulation_only_in_flags(self):
        result = default_bundle()
        assert result["governance"]["simulation_only"] is True

    def test_governance_scores_are_estimates(self):
        result = default_bundle()
        assert result["governance"]["scores_are_estimates_not_decisions"] is True

    def test_governance_plans_are_estimates(self):
        result = default_bundle()
        assert result["governance"]["plans_are_estimates_not_commitments"] is True

    def test_governance_flags_are_shallow_copy(self):
        """Mutating governance output does not affect _GOVERNANCE_FLAGS."""
        result = default_bundle()
        result["governance"]["commercial_product_ready"] = True
        assert _GOVERNANCE_FLAGS["commercial_product_ready"] is False

    def test_governance_copy_returns_new_dict(self):
        a = _governance_copy()
        b = _governance_copy()
        a["commercial_product_ready"] = "mutated"
        assert b["commercial_product_ready"] is False
        assert _GOVERNANCE_FLAGS["commercial_product_ready"] is False


# ---------------------------------------------------------------------------
# Source mutation check
# ---------------------------------------------------------------------------

class TestNoSourceMutation:
    def test_runtime_does_not_write_to_src_net(self):
        """Running the runtime should not create files under src/net/."""
        import os
        src_net = REPO_ROOT / "src" / "net"
        before = set()
        if src_net.exists():
            before = set(p for p in src_net.rglob("*") if p.is_file())

        run_acquisition_planning()

        after = set()
        if src_net.exists():
            after = set(p for p in src_net.rglob("*") if p.is_file())

        assert after == before, f"Runtime created files under src/net/: {after - before}"

    def test_runtime_does_not_write_to_src_python(self):
        """Running the runtime should not create files under src/python/."""
        src_python = REPO_ROOT / "src" / "python"
        before = set()
        if src_python.exists():
            before = set(p for p in src_python.rglob("*") if p.is_file())

        run_acquisition_planning()

        after = set()
        if src_python.exists():
            after = set(p for p in src_python.rglob("*") if p.is_file())

        assert after == before, f"Runtime created files under src/python/: {after - before}"


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_bundle_id_is_stable_across_calls(self):
        r1 = run_acquisition_planning(tier="TIER_A", top_n=5)
        r2 = run_acquisition_planning(tier="TIER_A", top_n=5)
        assert r1["bundle_id"] == r2["bundle_id"]

    def test_candidate_ranking_is_stable_across_calls(self):
        r1 = run_acquisition_planning(tier="TIER_A", top_n=5)
        r2 = run_acquisition_planning(tier="TIER_A", top_n=5)
        assert r1["candidate_ranking"] == r2["candidate_ranking"]

    def test_first_candidate_is_stable_across_calls(self):
        r1 = run_acquisition_planning(tier="TIER_A")
        r2 = run_acquisition_planning(tier="TIER_A")
        assert r1["selected_first_candidate"] == r2["selected_first_candidate"]

    def test_stable_hash_is_deterministic(self):
        assert _stable_hash({"a": 1}) == _stable_hash({"a": 1})

    def test_stable_hash_differs_for_different_data(self):
        assert _stable_hash({"a": 1}) != _stable_hash({"a": 2})


# ---------------------------------------------------------------------------
# Tier-specific behavior
# ---------------------------------------------------------------------------

class TestTierBehavior:
    def test_tier_active_returns_active_formats(self):
        result = run_acquisition_planning(tier="TIER_ACTIVE")
        ranking_ids = {r["format_id"] for r in result["candidate_ranking"]}
        # Active formats are fods and fodt
        assert "fods" in ranking_ids or "fodt" in ranking_ids

    def test_tier_a_does_not_return_tier_b_formats(self):
        result = run_acquisition_planning(tier="TIER_A")
        tier_b_formats = {"idml", "indd", "qxp", "sla", "wpd", "wk1"}
        ranking_ids = {r["format_id"] for r in result["candidate_ranking"]}
        assert not (ranking_ids & tier_b_formats), \
            f"TIER_B formats found in TIER_A ranking: {ranking_ids & tier_b_formats}"

    def test_tier_b_does_not_return_tier_a_formats(self):
        result = run_acquisition_planning(tier="TIER_B")
        tier_a_formats = {"hwpx", "hwp", "hwt", "alz", "egg", "gnumeric", "abw"}
        ranking_ids = {r["format_id"] for r in result["candidate_ranking"]}
        assert not (ranking_ids & tier_a_formats), \
            f"TIER_A formats found in TIER_B ranking: {ranking_ids & tier_a_formats}"

    def test_different_tiers_different_bundle_ids(self):
        ra = run_acquisition_planning(tier="TIER_A")
        rb = run_acquisition_planning(tier="TIER_B")
        assert ra["bundle_id"] != rb["bundle_id"]

    def test_different_top_n_different_bundle_ids(self):
        r3 = run_acquisition_planning(top_n=3)
        r5 = run_acquisition_planning(top_n=5)
        assert r3["bundle_id"] != r5["bundle_id"]


# ---------------------------------------------------------------------------
# Candidate blockers
# ---------------------------------------------------------------------------

class TestCandidateBlockers:
    def test_tier_a_first_candidate_blockers_included(self):
        result = default_bundle()
        # The result should have a blockers field (may be empty for high-scoring candidates)
        assert "first_candidate_blockers" in result
        assert isinstance(result["first_candidate_blockers"], list)

    def test_candidate_with_needs_audit_has_blocker_info(self):
        """Lifecycle simulation should flag audit requirements as blockers or next actions."""
        result = default_bundle()
        sim = result["lifecycle_simulation"]
        # zst is not in KNOWN_FORMAT_PROFILES, so it gets empty profile → CANDIDATE state
        # CANDIDATE state with support_matrix_audited=False should flag audit requirement
        # in next_actions
        next_actions = sim.get("next_actions", [])
        assert len(next_actions) > 0 or sim.get("current_state") == "CANDIDATE"


# ---------------------------------------------------------------------------
# Next recommended sprint
# ---------------------------------------------------------------------------

class TestNextRecommendedSprint:
    def test_next_recommended_sprint_is_string(self):
        result = default_bundle()
        assert isinstance(result["next_recommended_sprint"], str)
        assert len(result["next_recommended_sprint"]) > 0

    def test_next_recommended_sprint_not_r11(self):
        """R11 is current sprint — next sprint should not be R11."""
        result = default_bundle()
        assert "R11" not in result["next_recommended_sprint"]
