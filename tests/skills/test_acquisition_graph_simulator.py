"""
test_acquisition_graph_simulator.py

R12 Lane E — Tests for acquisition_graph_simulator.py

Validates:
- All 6 graph types build correctly
- Determinism across runs
- Multi-format isolation
- Governance flag enforcement
- State machine correctness
- Stale propagation correctness
- Evidence dependency completeness

Sprint: FORMAT-FACTORY-R12-ACQUISITION-ENGINE-IV-AND-ZST-GOVERNED-READINESS-SWARM-001
Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))


from acquisition_graph_simulator import (
    simulate_acquisition_graphs,
    build_acquisition_dependency_graph,
    build_onboarding_transition_graph,
    build_stale_propagation_graph,
    build_evidence_dependency_graph,
    build_replay_lineage_graph,
    build_verification_dependency_graph,
    simulate_multi_format_isolation,
    ACQUISITION_STATES,
    STATE_CANDIDATE,
    STATE_SUPPORT_MATRIX_AUDIT,
    STATE_SPEC_NORMALIZATION,
    STATE_EVIDENCE_READY,
    _GOVERNANCE_FLAGS,
    _governance_copy,
)


# ---------------------------------------------------------------------------
# Section 1: Module Import and Constants
# ---------------------------------------------------------------------------

class TestModuleImport:

    def test_module_imports_successfully(self):
        import acquisition_graph_simulator
        assert acquisition_graph_simulator is not None

    def test_acquisition_states_count(self):
        """Exactly 10 acquisition states (CANDIDATE through EVIDENCE_READY)."""
        assert len(ACQUISITION_STATES) == 10

    def test_acquisition_states_starts_with_candidate(self):
        assert ACQUISITION_STATES[0] == STATE_CANDIDATE

    def test_acquisition_states_ends_with_evidence_ready(self):
        assert ACQUISITION_STATES[-1] == STATE_EVIDENCE_READY

    def test_governance_flags_present(self):
        assert "commercial_product_ready" in _GOVERNANCE_FLAGS
        assert "dry_run_only" in _GOVERNANCE_FLAGS
        assert "simulation_only" in _GOVERNANCE_FLAGS
        assert "acquisition_not_authorized" in _GOVERNANCE_FLAGS

    def test_governance_immutable(self):
        copy = _governance_copy()
        copy["commercial_product_ready"] = True
        assert _GOVERNANCE_FLAGS["commercial_product_ready"] is False


# ---------------------------------------------------------------------------
# Section 2: simulate_acquisition_graphs (main entrypoint)
# ---------------------------------------------------------------------------

class TestSimulateAcquisitionGraphs:

    def test_zst_bundle_has_correct_format(self):
        result = simulate_acquisition_graphs("zst")
        assert result["format"] == "zst"

    def test_bundle_has_6_graphs(self):
        result = simulate_acquisition_graphs("zst")
        assert result["graph_count"] == 6

    def test_bundle_has_all_graph_types(self):
        result = simulate_acquisition_graphs("zst")
        expected_keys = {
            "acquisition_dependency_graph",
            "onboarding_transition_graph",
            "stale_propagation_graph",
            "evidence_dependency_graph",
            "replay_lineage_graph",
            "verification_dependency_graph",
        }
        assert set(result["graphs"].keys()) == expected_keys

    def test_bundle_total_nodes_positive(self):
        result = simulate_acquisition_graphs("zst")
        assert result["total_nodes"] > 0

    def test_bundle_total_edges_positive(self):
        result = simulate_acquisition_graphs("zst")
        assert result["total_edges"] > 0

    def test_bundle_simulation_id_present(self):
        result = simulate_acquisition_graphs("zst")
        assert "simulation_id" in result
        assert len(result["simulation_id"]) == 16

    def test_bundle_governance_present(self):
        result = simulate_acquisition_graphs("zst")
        gov = result["governance"]
        assert gov["commercial_product_ready"] is False
        assert gov["dry_run_only"] is True
        assert gov["simulation_only"] is True
        assert gov["acquisition_not_authorized"] is True

    def test_bundle_simulation_note_present(self):
        result = simulate_acquisition_graphs("zst")
        assert "simulation_note" in result
        assert "SIMULATION" in result["simulation_note"]

    def test_different_formats_produce_different_simulation_ids(self):
        zst = simulate_acquisition_graphs("zst")
        hwp = simulate_acquisition_graphs("hwp")
        assert zst["simulation_id"] != hwp["simulation_id"]


# ---------------------------------------------------------------------------
# Section 3: Acquisition Dependency Graph
# ---------------------------------------------------------------------------

class TestAcquisitionDependencyGraph:

    def test_graph_type_correct(self):
        g = build_acquisition_dependency_graph("zst")
        assert g["graph_type"] == "acquisition_dependency_graph"

    def test_node_count_includes_terminal_states(self):
        g = build_acquisition_dependency_graph("zst")
        # 10 lifecycle states + 2 terminal (BLOCKED, DEFERRED) = 12 nodes
        assert g["node_count"] == 12

    def test_edge_count_is_9(self):
        g = build_acquisition_dependency_graph("zst")
        # 9 sequential edges (10 states - 1)
        assert g["edge_count"] == 9

    def test_all_nodes_have_correct_format(self):
        g = build_acquisition_dependency_graph("zst")
        for node in g["nodes"]:
            if node["type"] != "terminal_state":
                assert node.get("format") == "zst"

    def test_graph_id_is_stable(self):
        g1 = build_acquisition_dependency_graph("zst")
        g2 = build_acquisition_dependency_graph("zst")
        assert g1["graph_id"] == g2["graph_id"]

    def test_different_formats_different_graph_ids(self):
        g1 = build_acquisition_dependency_graph("zst")
        g2 = build_acquisition_dependency_graph("hwp")
        assert g1["graph_id"] != g2["graph_id"]


# ---------------------------------------------------------------------------
# Section 4: Onboarding Transition Graph
# ---------------------------------------------------------------------------

class TestOnboardingTransitionGraph:

    def test_default_current_state_is_candidate(self):
        g = build_onboarding_transition_graph("zst")
        assert g["current_state"] == STATE_CANDIDATE

    def test_next_state_from_candidate_is_support_matrix_audit(self):
        g = build_onboarding_transition_graph("zst", STATE_CANDIDATE)
        assert g["next_state"] == STATE_SUPPORT_MATRIX_AUDIT

    def test_next_state_is_none_at_evidence_ready(self):
        g = build_onboarding_transition_graph("zst", STATE_EVIDENCE_READY)
        assert g["next_state"] is None

    def test_nodes_have_correct_status_flags(self):
        g = build_onboarding_transition_graph("zst", STATE_SPEC_NORMALIZATION)
        status_map = {n["label"]: n.get("status") for n in g["nodes"]
                      if n["type"] == "onboarding_state"}
        assert status_map[STATE_CANDIDATE] == "PAST"
        assert status_map[STATE_SUPPORT_MATRIX_AUDIT] == "PAST"
        assert status_map[STATE_SPEC_NORMALIZATION] == "CURRENT"
        assert status_map[STATE_EVIDENCE_READY] == "FUTURE"

    def test_graph_id_depends_on_current_state(self):
        g1 = build_onboarding_transition_graph("zst", STATE_CANDIDATE)
        g2 = build_onboarding_transition_graph("zst", STATE_SPEC_NORMALIZATION)
        assert g1["graph_id"] != g2["graph_id"]


# ---------------------------------------------------------------------------
# Section 5: Stale Propagation Graph
# ---------------------------------------------------------------------------

class TestStalePropagationGraph:

    def test_stale_origin_node_is_stale(self):
        g = build_stale_propagation_graph("zst", STATE_SPEC_NORMALIZATION)
        origin_node = next(
            n for n in g["nodes"]
            if n["label"] == STATE_SPEC_NORMALIZATION
        )
        assert origin_node["stale_status"] == "STALE_ORIGIN"

    def test_states_before_origin_are_unaffected(self):
        g = build_stale_propagation_graph("zst", STATE_SPEC_NORMALIZATION)
        for node in g["nodes"]:
            if node["label"] in (STATE_CANDIDATE, STATE_SUPPORT_MATRIX_AUDIT):
                assert node["stale_status"] == "UNAFFECTED"

    def test_states_after_origin_are_propagated(self):
        g = build_stale_propagation_graph("zst", STATE_SPEC_NORMALIZATION)
        norm_order = ACQUISITION_STATES.index(STATE_SPEC_NORMALIZATION)
        for node in g["nodes"]:
            if node["label"] in ACQUISITION_STATES:
                node_order = ACQUISITION_STATES.index(node["label"])
                if node_order > norm_order:
                    assert node["stale_status"] == "STALE_PROPAGATED", \
                        f"{node['label']} should be STALE_PROPAGATED"

    def test_stale_affected_states_list_correct(self):
        g = build_stale_propagation_graph("zst", STATE_SPEC_NORMALIZATION)
        affected = g["stale_affected_states"]
        norm_order = ACQUISITION_STATES.index(STATE_SPEC_NORMALIZATION)
        expected = ACQUISITION_STATES[norm_order:]
        assert affected == expected

    def test_stale_edges_go_forward(self):
        g = build_stale_propagation_graph("zst", STATE_SPEC_NORMALIZATION)
        for edge in g["edges"]:
            assert edge["type"] == "stale_propagates_to"


# ---------------------------------------------------------------------------
# Section 6: Evidence Dependency Graph
# ---------------------------------------------------------------------------

class TestEvidenceDependencyGraph:

    def test_total_evidence_artifacts_positive(self):
        g = build_evidence_dependency_graph("zst")
        assert g["total_evidence_artifacts"] > 0

    def test_evidence_edges_are_required_for_advance(self):
        g = build_evidence_dependency_graph("zst")
        for edge in g["edges"]:
            assert edge["type"] == "required_for_advance"

    def test_spec_normalization_has_evidence(self):
        from acquisition_graph_simulator import STATE_EVIDENCE_REQUIREMENTS
        ev = STATE_EVIDENCE_REQUIREMENTS.get(STATE_SPEC_NORMALIZATION, [])
        assert len(ev) > 0
        assert "spec_cached_locally" in ev

    def test_candidate_state_has_evidence(self):
        from acquisition_graph_simulator import STATE_EVIDENCE_REQUIREMENTS
        ev = STATE_EVIDENCE_REQUIREMENTS.get(STATE_CANDIDATE, [])
        assert len(ev) > 0

    def test_all_states_have_evidence_requirements(self):
        from acquisition_graph_simulator import STATE_EVIDENCE_REQUIREMENTS
        for state in ACQUISITION_STATES:
            assert state in STATE_EVIDENCE_REQUIREMENTS, \
                f"{state} has no evidence requirements defined"
            assert len(STATE_EVIDENCE_REQUIREMENTS[state]) > 0, \
                f"{state} has empty evidence requirements"


# ---------------------------------------------------------------------------
# Section 7: Replay Lineage Graph
# ---------------------------------------------------------------------------

class TestReplayLineageGraph:

    def test_default_sprints_count(self):
        g = build_replay_lineage_graph("zst")
        assert g["sprint_count"] == 4  # Default R10/R10-closure/R11/R12

    def test_custom_sprints(self):
        g = build_replay_lineage_graph("zst", sprints=["S1", "S2", "S3"])
        assert g["sprint_count"] == 3

    def test_replay_edges_chain_sequentially(self):
        g = build_replay_lineage_graph("zst")
        for edge in g["edges"]:
            assert edge["type"] == "replay_chains_to"

    def test_node_count_equals_sprint_count(self):
        g = build_replay_lineage_graph("zst", sprints=["S1", "S2", "S3"])
        assert g["node_count"] == 3

    def test_edge_count_is_sprint_count_minus_1(self):
        g = build_replay_lineage_graph("zst", sprints=["S1", "S2", "S3"])
        assert g["edge_count"] == 2


# ---------------------------------------------------------------------------
# Section 8: Verification Dependency Graph
# ---------------------------------------------------------------------------

class TestVerificationDependencyGraph:

    def test_iv_stages_count(self):
        g = build_verification_dependency_graph("zst")
        assert len(g["iv_stages"]) == 3

    def test_iv_stages_include_dec034(self):
        g = build_verification_dependency_graph("zst")
        assert "DEC034_IV" in g["iv_stages"]

    def test_iv_edges_require_iv(self):
        g = build_verification_dependency_graph("zst")
        for edge in g["edges"]:
            assert edge["type"] == "requires_iv"

    def test_governance_in_iv_graph(self):
        g = build_verification_dependency_graph("zst")
        assert g["governance"]["commercial_product_ready"] is False


# ---------------------------------------------------------------------------
# Section 9: Multi-Format Isolation
# ---------------------------------------------------------------------------

class TestMultiFormatIsolation:

    def test_zst_and_hwp_fully_isolated(self):
        result = simulate_multi_format_isolation(["zst", "hwp"])
        assert result["isolation_valid"] is True
        assert len(result["violations"]) == 0

    def test_all_tier_a_formats_isolated(self):
        tier_a = [
            "hwpx", "hwp", "hwt", "alz", "egg", "numbers", "key", "pages",
            "gnumeric", "abw", "xar", "lha", "lzh", "arj", "zpaq", "zst",
            "qoi", "ora", "xcf",
        ]
        result = simulate_multi_format_isolation(tier_a)
        assert result["isolation_valid"] is True, \
            f"Isolation violations: {result['violations']}"

    def test_isolation_total_nodes_accumulates(self):
        result = simulate_multi_format_isolation(["zst", "hwp"])
        # Each format produces 12 dependency graph nodes; 2 formats = 24 unique nodes
        assert result["total_nodes"] == 24

    def test_empty_format_list(self):
        result = simulate_multi_format_isolation([])
        assert result["isolation_valid"] is True
        assert result["total_nodes"] == 0


# ---------------------------------------------------------------------------
# Section 10: Determinism
# ---------------------------------------------------------------------------

class TestGraphDeterminism:

    def test_simulation_id_stable(self):
        r1 = simulate_acquisition_graphs("zst")
        r2 = simulate_acquisition_graphs("zst")
        assert r1["simulation_id"] == r2["simulation_id"]

    def test_all_graph_ids_stable(self):
        r1 = simulate_acquisition_graphs("zst")
        r2 = simulate_acquisition_graphs("zst")
        for graph_type in r1["graphs"]:
            assert r1["graphs"][graph_type]["graph_id"] == r2["graphs"][graph_type]["graph_id"], \
                f"{graph_type}: graph_id not stable"

    def test_node_counts_stable(self):
        r1 = simulate_acquisition_graphs("zst")
        r2 = simulate_acquisition_graphs("zst")
        assert r1["total_nodes"] == r2["total_nodes"]
        assert r1["total_edges"] == r2["total_edges"]
