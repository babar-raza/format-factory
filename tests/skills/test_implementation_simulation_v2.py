"""
test_implementation_simulation_v2.py -- Lane F Tests (FORMAT-FACTORY-R10)

Tests for implementation_simulation_v2.py.

COVERAGE:
  - build_dependency_graph: structure, cross-format edges
  - build_taskcard_graph: task cards per gate, completed status
  - build_evidence_graph: evidence artifacts, requires chain
  - build_replay_lineage_graph: hash chain, determinism
  - build_stale_state_graph: domain nodes, propagation edges
  - build_authority_graph: authority chain, gate_11_approved=False
  - simulate_v2: all 6 graphs, governance invariants
  - simulate_v2_standard_formats: smoke test

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from implementation_simulation_v2 import (
    build_dependency_graph,
    build_taskcard_graph,
    build_evidence_graph,
    build_replay_lineage_graph,
    build_stale_state_graph,
    build_authority_graph,
    simulate_v2,
    simulate_v2_standard_formats,
    GATE_SEQUENCE,
    NODE_TYPE_FORMAT,
    NODE_TYPE_GATE,
    NODE_TYPE_TASK,
    NODE_TYPE_EVIDENCE,
    NODE_TYPE_AUTHORITY,
    NODE_TYPE_STALE_DOMAIN,
    NODE_TYPE_FINGERPRINT,
    EDGE_TYPE_PRODUCES,
    EDGE_TYPE_REQUIRES,
    EDGE_TYPE_PROPAGATES_TO,
    EDGE_TYPE_AUTHORIZES,
    EDGE_TYPE_CHAINS_TO,
    _GOVERNANCE_FLAGS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _node_ids(graph: dict) -> set:
    return {n["id"] for n in graph["nodes"]}


def _edge_types(graph: dict) -> set:
    return {e["type"] for e in graph["edges"]}


# ---------------------------------------------------------------------------
# GATE_SEQUENCE
# ---------------------------------------------------------------------------

class TestGateSequence:
    def test_gate_sequence_non_empty(self):
        assert len(GATE_SEQUENCE) >= 10

    def test_support_matrix_audit_is_first(self):
        assert GATE_SEQUENCE[0] == "SUPPORT_MATRIX_AUDIT"

    def test_gate_11_is_last(self):
        assert GATE_SEQUENCE[-1] == "GATE_11"

    def test_evidence_ready_before_gate_11(self):
        idx_er = GATE_SEQUENCE.index("EVIDENCE_READY")
        idx_g11 = GATE_SEQUENCE.index("GATE_11")
        assert idx_er < idx_g11


# ---------------------------------------------------------------------------
# build_dependency_graph
# ---------------------------------------------------------------------------

class TestBuildDependencyGraph:
    def test_required_keys_present(self):
        r = build_dependency_graph("hwpx")
        for key in ["graph_id", "graph_type", "format", "nodes", "edges",
                    "node_count", "edge_count", "governance", "dry_run_only", "graph_note"]:
            assert key in r, f"Missing: {key}"

    def test_graph_type_correct(self):
        assert build_dependency_graph("hwpx")["graph_type"] == "dependency_graph"

    def test_format_in_result(self):
        r = build_dependency_graph("hwpx")
        assert r["format"] == "hwpx"

    def test_node_count_matches_nodes(self):
        r = build_dependency_graph("hwpx")
        assert r["node_count"] == len(r["nodes"])

    def test_edge_count_matches_edges(self):
        r = build_dependency_graph("hwpx")
        assert r["edge_count"] == len(r["edges"])

    def test_has_format_nodes(self):
        r = build_dependency_graph("hwpx", ["hwpx", "hwp"])
        types = {n["type"] for n in r["nodes"]}
        assert NODE_TYPE_FORMAT in types

    def test_has_gate_nodes(self):
        r = build_dependency_graph("hwpx")
        types = {n["type"] for n in r["nodes"]}
        assert NODE_TYPE_GATE in types

    def test_graph_id_is_hex(self):
        r = build_dependency_graph("hwpx")
        int(r["graph_id"], 16)

    def test_determinism(self):
        r1 = build_dependency_graph("hwpx", ["hwpx", "hwp"])
        r2 = build_dependency_graph("hwpx", ["hwpx", "hwp"])
        assert r1["graph_id"] == r2["graph_id"]

    def test_cross_format_hwp_depends_on_hwpx(self):
        r = build_dependency_graph("hwp", ["hwpx", "hwp"])
        # Should have edge from fmt:hwpx to gate:hwp:SUPPORT_MATRIX_AUDIT
        edge_froms = {e["from"] for e in r["edges"]}
        assert "fmt:hwpx" in edge_froms

    def test_cross_format_egg_depends_on_alz(self):
        r = build_dependency_graph("egg", ["alz", "egg"])
        edge_froms = {e["from"] for e in r["edges"]}
        assert "fmt:alz" in edge_froms

    def test_dry_run_only_true(self):
        assert build_dependency_graph("fods")["dry_run_only"] is True

    def test_governance_commercial_product_ready_false(self):
        r = build_dependency_graph("fods")
        assert r["governance"]["commercial_product_ready"] is False

    def test_json_serializable(self):
        json.dumps(build_dependency_graph("hwpx", ["hwpx", "hwp", "hwt"]))


# ---------------------------------------------------------------------------
# build_taskcard_graph
# ---------------------------------------------------------------------------

class TestBuildTaskcardGraph:
    def test_required_keys_present(self):
        r = build_taskcard_graph("fods")
        for key in ["graph_id", "graph_type", "format", "nodes", "edges",
                    "node_count", "edge_count", "gates_completed", "total_gates",
                    "governance", "dry_run_only", "graph_note"]:
            assert key in r, f"Missing: {key}"

    def test_graph_type_correct(self):
        assert build_taskcard_graph("fods")["graph_type"] == "taskcard_graph"

    def test_has_task_nodes(self):
        r = build_taskcard_graph("fods")
        types = {n["type"] for n in r["nodes"]}
        assert NODE_TYPE_TASK in types

    def test_has_gate_nodes(self):
        r = build_taskcard_graph("fods")
        types = {n["type"] for n in r["nodes"]}
        assert NODE_TYPE_GATE in types

    def test_all_tasks_sim_prefixed(self):
        r = build_taskcard_graph("fods")
        for n in r["nodes"]:
            if n["type"] == NODE_TYPE_TASK:
                assert n["label"].startswith("[SIM]"), f"Non-SIM task: {n['label']}"

    def test_total_gates_correct(self):
        r = build_taskcard_graph("fods")
        assert r["total_gates"] == len(GATE_SEQUENCE)

    def test_completed_gates_in_result(self):
        completed = ["SUPPORT_MATRIX_AUDIT", "SPEC_DISCOVERY"]
        r = build_taskcard_graph("hwpx", completed)
        assert set(completed) == set(r["gates_completed"])

    def test_node_count_matches(self):
        r = build_taskcard_graph("hwpx")
        assert r["node_count"] == len(r["nodes"])

    def test_graph_id_is_hex(self):
        int(build_taskcard_graph("fods")["graph_id"], 16)

    def test_determinism(self):
        r1 = build_taskcard_graph("fods", ["SUPPORT_MATRIX_AUDIT"])
        r2 = build_taskcard_graph("fods", ["SUPPORT_MATRIX_AUDIT"])
        assert r1["graph_id"] == r2["graph_id"]

    def test_different_completed_different_graph_id(self):
        r1 = build_taskcard_graph("fods", [])
        r2 = build_taskcard_graph("fods", ["SUPPORT_MATRIX_AUDIT"])
        assert r1["graph_id"] != r2["graph_id"]

    def test_governance_flags_correct(self):
        r = build_taskcard_graph("fods")
        assert r["governance"]["commercial_product_ready"] is False
        assert r["governance"]["autonomous_execution_allowed"] is False

    def test_json_serializable(self):
        json.dumps(build_taskcard_graph("hwpx"))


# ---------------------------------------------------------------------------
# build_evidence_graph
# ---------------------------------------------------------------------------

class TestBuildEvidenceGraph:
    def test_required_keys_present(self):
        r = build_evidence_graph("fods")
        for key in ["graph_id", "graph_type", "format", "nodes", "edges",
                    "node_count", "edge_count", "evidence_artifacts",
                    "governance", "dry_run_only", "graph_note"]:
            assert key in r, f"Missing: {key}"

    def test_graph_type_correct(self):
        assert build_evidence_graph("fods")["graph_type"] == "evidence_graph"

    def test_has_evidence_nodes(self):
        r = build_evidence_graph("fods")
        types = {n["type"] for n in r["nodes"]}
        assert NODE_TYPE_EVIDENCE in types

    def test_has_gate_nodes(self):
        r = build_evidence_graph("fods")
        types = {n["type"] for n in r["nodes"]}
        assert NODE_TYPE_GATE in types

    def test_produces_edges_present(self):
        r = build_evidence_graph("fods")
        assert EDGE_TYPE_PRODUCES in _edge_types(r)

    def test_requires_edges_present(self):
        r = build_evidence_graph("fods")
        assert EDGE_TYPE_REQUIRES in _edge_types(r)

    def test_evidence_artifacts_non_empty(self):
        r = build_evidence_graph("fods")
        assert len(r["evidence_artifacts"]) > 0

    def test_evidence_artifacts_include_gate_11_approval(self):
        r = build_evidence_graph("fods")
        assert "gate_11_human_approval_record" in r["evidence_artifacts"]

    def test_graph_id_is_hex(self):
        int(build_evidence_graph("fods")["graph_id"], 16)

    def test_determinism(self):
        r1 = build_evidence_graph("fods")
        r2 = build_evidence_graph("fods")
        assert r1["graph_id"] == r2["graph_id"]

    def test_cross_format_different_graph_ids(self):
        r_fods = build_evidence_graph("fods")
        r_hwpx = build_evidence_graph("hwpx")
        assert r_fods["graph_id"] != r_hwpx["graph_id"]

    def test_evidence_nodes_have_visibility_internal(self):
        r = build_evidence_graph("fods")
        for n in r["nodes"]:
            if n["type"] == NODE_TYPE_EVIDENCE:
                assert n["metadata"].get("visibility") == "internal"

    def test_json_serializable(self):
        json.dumps(build_evidence_graph("hwpx"))


# ---------------------------------------------------------------------------
# build_replay_lineage_graph
# ---------------------------------------------------------------------------

class TestBuildReplayLineageGraph:
    def test_required_keys_present(self):
        r = build_replay_lineage_graph("fods")
        for key in ["graph_id", "graph_type", "format", "nodes", "edges",
                    "node_count", "edge_count", "sprint_count",
                    "genesis_sprint", "latest_sprint", "governance",
                    "dry_run_only", "graph_note"]:
            assert key in r, f"Missing: {key}"

    def test_graph_type_correct(self):
        assert build_replay_lineage_graph("fods")["graph_type"] == "replay_lineage_graph"

    def test_has_fingerprint_nodes(self):
        r = build_replay_lineage_graph("fods")
        types = {n["type"] for n in r["nodes"]}
        assert NODE_TYPE_FINGERPRINT in types

    def test_chains_to_edges_present(self):
        r = build_replay_lineage_graph("fods")
        assert EDGE_TYPE_CHAINS_TO in _edge_types(r)

    def test_sprint_count_matches_sprints(self):
        sprints = ["R1", "R2", "R3"]
        r = build_replay_lineage_graph("fods", sprints)
        assert r["sprint_count"] == 3
        assert r["node_count"] == 3
        assert r["edge_count"] == 2  # N nodes → N-1 edges

    def test_genesis_sprint_is_first(self):
        r = build_replay_lineage_graph("fods", ["R1", "R2"])
        assert r["genesis_sprint"] == "R1"

    def test_latest_sprint_is_last(self):
        r = build_replay_lineage_graph("fods", ["R1", "R2", "R3"])
        assert r["latest_sprint"] == "R3"

    def test_first_node_is_genesis(self):
        r = build_replay_lineage_graph("fods", ["R1", "R2"])
        first = next(n for n in r["nodes"] if n["id"].endswith(":R1"))
        assert first["metadata"]["is_genesis"] is True

    def test_non_first_node_not_genesis(self):
        r = build_replay_lineage_graph("fods", ["R1", "R2"])
        second = next(n for n in r["nodes"] if n["id"].endswith(":R2"))
        assert second["metadata"]["is_genesis"] is False

    def test_all_nodes_have_lineage_hash(self):
        r = build_replay_lineage_graph("fods")
        for n in r["nodes"]:
            assert "lineage_hash" in n["metadata"]
            int(n["metadata"]["lineage_hash"], 16)

    def test_determinism(self):
        r1 = build_replay_lineage_graph("fods", ["R1", "R2"])
        r2 = build_replay_lineage_graph("fods", ["R1", "R2"])
        assert r1["graph_id"] == r2["graph_id"]
        assert [n["metadata"]["lineage_hash"] for n in r1["nodes"]] == \
               [n["metadata"]["lineage_hash"] for n in r2["nodes"]]

    def test_cross_format_different_hashes(self):
        r_fods = build_replay_lineage_graph("fods", ["R1"])
        r_hwpx = build_replay_lineage_graph("hwpx", ["R1"])
        fods_fp = r_fods["nodes"][0]["metadata"]["fingerprint"]
        hwpx_fp = r_hwpx["nodes"][0]["metadata"]["fingerprint"]
        assert fods_fp != hwpx_fp

    def test_json_serializable(self):
        json.dumps(build_replay_lineage_graph("hwpx"))


# ---------------------------------------------------------------------------
# build_stale_state_graph
# ---------------------------------------------------------------------------

class TestBuildStaleStateGraph:
    def test_required_keys_present(self):
        r = build_stale_state_graph("fods")
        for key in ["graph_id", "graph_type", "format", "nodes", "edges",
                    "node_count", "edge_count", "stale_domains",
                    "governance", "dry_run_only", "graph_note"]:
            assert key in r, f"Missing: {key}"

    def test_graph_type_correct(self):
        assert build_stale_state_graph("fods")["graph_type"] == "stale_state_graph"

    def test_has_stale_domain_nodes(self):
        r = build_stale_state_graph("fods")
        types = {n["type"] for n in r["nodes"]}
        assert NODE_TYPE_STALE_DOMAIN in types

    def test_propagates_to_edges_present(self):
        r = build_stale_state_graph("fods")
        assert EDGE_TYPE_PROPAGATES_TO in _edge_types(r)

    def test_stale_domains_non_empty(self):
        r = build_stale_state_graph("fods")
        assert len(r["stale_domains"]) >= 5

    def test_spec_cache_first_domain(self):
        r = build_stale_state_graph("fods")
        assert r["stale_domains"][0] == "spec_cache"

    def test_evidence_bundle_last_domain(self):
        r = build_stale_state_graph("fods")
        assert r["stale_domains"][-1] == "evidence_bundle"

    def test_node_count_equals_domain_count(self):
        r = build_stale_state_graph("fods")
        assert r["node_count"] == len(r["stale_domains"])

    def test_edge_count_is_domains_minus_one(self):
        r = build_stale_state_graph("fods")
        assert r["edge_count"] == r["node_count"] - 1

    def test_graph_id_is_hex(self):
        int(build_stale_state_graph("fods")["graph_id"], 16)

    def test_determinism(self):
        r1 = build_stale_state_graph("fods")
        r2 = build_stale_state_graph("fods")
        assert r1["graph_id"] == r2["graph_id"]

    def test_cross_format_different_graph_ids(self):
        r_fods = build_stale_state_graph("fods")
        r_hwpx = build_stale_state_graph("hwpx")
        assert r_fods["graph_id"] != r_hwpx["graph_id"]

    def test_json_serializable(self):
        json.dumps(build_stale_state_graph("hwpx"))


# ---------------------------------------------------------------------------
# build_authority_graph
# ---------------------------------------------------------------------------

class TestBuildAuthorityGraph:
    def test_required_keys_present(self):
        r = build_authority_graph("fods")
        for key in ["graph_id", "graph_type", "format", "nodes", "edges",
                    "node_count", "edge_count", "gate_11_approved",
                    "governance", "dry_run_only", "graph_note"]:
            assert key in r, f"Missing: {key}"

    def test_graph_type_correct(self):
        assert build_authority_graph("fods")["graph_type"] == "authority_graph"

    def test_gate_11_approved_false(self):
        assert build_authority_graph("fods")["gate_11_approved"] is False

    def test_has_authority_nodes(self):
        r = build_authority_graph("fods")
        types = {n["type"] for n in r["nodes"]}
        assert NODE_TYPE_AUTHORITY in types

    def test_authorizes_edges_present(self):
        r = build_authority_graph("fods")
        assert EDGE_TYPE_AUTHORIZES in _edge_types(r)

    def test_gate_11_node_approved_false(self):
        r = build_authority_graph("fods")
        gate11_node = next(
            (n for n in r["nodes"] if "gate_11" in n["id"].lower() or "Gate 11" in n["label"]),
            None,
        )
        assert gate11_node is not None
        assert gate11_node["metadata"]["approved"] is False

    def test_no_node_has_gate_self_approval_true(self):
        r = build_authority_graph("fods")
        for n in r["nodes"]:
            assert n["metadata"].get("gate_self_approval_allowed") is not True

    def test_graph_note_mentions_not_approved(self):
        r = build_authority_graph("fods")
        assert "NOT APPROVED" in r["graph_note"]

    def test_graph_id_is_hex(self):
        int(build_authority_graph("fods")["graph_id"], 16)

    def test_determinism(self):
        r1 = build_authority_graph("fods")
        r2 = build_authority_graph("fods")
        assert r1["graph_id"] == r2["graph_id"]

    def test_governance_commercial_product_ready_false(self):
        r = build_authority_graph("fods")
        assert r["governance"]["commercial_product_ready"] is False

    def test_json_serializable(self):
        json.dumps(build_authority_graph("hwpx"))


# ---------------------------------------------------------------------------
# simulate_v2
# ---------------------------------------------------------------------------

class TestSimulateV2:
    def _run(self, fmt="fods", **kwargs):
        return simulate_v2(fmt, **kwargs)

    def test_required_keys_present(self):
        r = self._run()
        for key in ["simulation_id", "format", "graphs", "graph_types",
                    "total_nodes", "total_edges", "gate_11_approved",
                    "governance", "dry_run_only", "autonomous_execution_allowed",
                    "simulation_note"]:
            assert key in r, f"Missing: {key}"

    def test_six_graphs_present(self):
        r = self._run()
        assert len(r["graphs"]) == 6

    def test_all_graph_types_present(self):
        r = self._run()
        expected = {"dependency_graph", "taskcard_graph", "evidence_graph",
                    "replay_lineage_graph", "stale_state_graph", "authority_graph"}
        assert set(r["graph_types"]) == expected

    def test_graph_types_sorted(self):
        r = self._run()
        assert r["graph_types"] == sorted(r["graph_types"])

    def test_gate_11_approved_false(self):
        r = self._run()
        assert r["gate_11_approved"] is False

    def test_dry_run_only_true(self):
        r = self._run()
        assert r["dry_run_only"] is True

    def test_autonomous_execution_allowed_false(self):
        r = self._run()
        assert r["autonomous_execution_allowed"] is False

    def test_total_nodes_positive(self):
        r = self._run()
        assert r["total_nodes"] > 0

    def test_total_edges_positive(self):
        r = self._run()
        assert r["total_edges"] > 0

    def test_simulation_id_is_hex(self):
        int(self._run()["simulation_id"], 16)

    def test_determinism(self):
        r1 = self._run()
        r2 = self._run()
        assert r1["simulation_id"] == r2["simulation_id"]
        assert r1["total_nodes"] == r2["total_nodes"]

    def test_cross_format_different_simulation_ids(self):
        r_fods = simulate_v2("fods")
        r_hwpx = simulate_v2("hwpx")
        assert r_fods["simulation_id"] != r_hwpx["simulation_id"]

    def test_governance_commercial_product_ready_false(self):
        r = self._run()
        assert r["governance"]["commercial_product_ready"] is False
        for graph in r["graphs"].values():
            assert graph["governance"]["commercial_product_ready"] is False

    def test_simulation_note_mentions_not_approved(self):
        r = self._run()
        assert "NOT APPROVED" in r["simulation_note"]

    def test_json_serializable(self):
        json.dumps(self._run())

    def test_format_in_result(self):
        r = simulate_v2("hwpx")
        assert r["format"] == "hwpx"


# ---------------------------------------------------------------------------
# simulate_v2_standard_formats
# ---------------------------------------------------------------------------

class TestSimulateV2StandardFormats:
    def test_returns_dict(self):
        r = simulate_v2_standard_formats()
        assert isinstance(r, dict)

    def test_required_keys_present(self):
        r = simulate_v2_standard_formats()
        for key in ["aggregate_simulation_id", "formats_simulated", "per_format",
                    "format_count", "gate_11_approved", "governance",
                    "dry_run_only", "autonomous_execution_allowed"]:
            assert key in r, f"Missing: {key}"

    def test_contains_standard_formats(self):
        r = simulate_v2_standard_formats()
        for fmt in ["fods", "fodt", "hwpx", "hwp", "alz", "egg"]:
            assert fmt in r["per_format"]

    def test_formats_simulated_sorted(self):
        r = simulate_v2_standard_formats()
        assert r["formats_simulated"] == sorted(r["formats_simulated"])

    def test_format_count_matches(self):
        r = simulate_v2_standard_formats()
        assert r["format_count"] == len(r["formats_simulated"])

    def test_gate_11_approved_false(self):
        r = simulate_v2_standard_formats()
        assert r["gate_11_approved"] is False

    def test_governance_flags_correct(self):
        r = simulate_v2_standard_formats()
        assert r["governance"]["commercial_product_ready"] is False
        assert r["autonomous_execution_allowed"] is False

    def test_each_format_has_six_graphs(self):
        r = simulate_v2_standard_formats()
        for fmt in r["formats_simulated"]:
            assert len(r["per_format"][fmt]["graphs"]) == 6

    def test_governance_flags_immutable(self):
        r = simulate_v2_standard_formats()
        r["governance"]["commercial_product_ready"] = True
        assert _GOVERNANCE_FLAGS["commercial_product_ready"] is False

    def test_json_serializable(self):
        json.dumps(simulate_v2_standard_formats())
