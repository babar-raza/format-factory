"""
acquisition_graph_simulator.py -- R12 Lane E Deliverable

Acquisition Dependency and Transition Graph Simulator.

PURPOSE:
  Simulate acquisition planning dependencies, onboarding transitions, stale-state
  transitions, evidence transitions, and replay lineage for format candidates.
  Complements implementation_simulation_v2.py by focusing on the acquisition-layer
  (pre-implementation) graph structure.

GRAPH TYPES:
  acquisition_dependency_graph  -- Prerequisites between acquisition lifecycle states
  onboarding_transition_graph   -- Format-specific state machine transitions
  stale_propagation_graph       -- How stale state propagates through lifecycle
  evidence_dependency_graph     -- Which evidence artifacts each state requires
  replay_lineage_graph          -- Sprint lineage for replay verification
  verification_dependency_graph -- DEC-034 IV dependencies

SIMULATION ONLY:
  No source mutation, no gate approval, no internet fetches, no real acquisition.
  All outputs are deterministic descriptions of what WOULD happen.

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
Sprint: FORMAT-FACTORY-R12-ACQUISITION-ENGINE-IV-AND-ZST-GOVERNED-READINESS-SWARM-001
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

# ---------------------------------------------------------------------------
# Governance
# ---------------------------------------------------------------------------

_GOVERNANCE_FLAGS: dict[str, Any] = {
    "commercial_product_ready": False,
    "autonomous_execution_allowed": False,
    "gate_self_approval_allowed": False,
    "dry_run_only": True,
    "simulation_only": True,
    "no_internet_access": True,
    "no_source_mutation": True,
    "graphs_are_simulation_outputs_not_authorizations": True,
    "acquisition_not_authorized": True,
}

# ---------------------------------------------------------------------------
# Lifecycle State Constants (mirrors acquisition_lifecycle_simulator)
# ---------------------------------------------------------------------------

STATE_CANDIDATE = "CANDIDATE"
STATE_SUPPORT_MATRIX_AUDIT = "SUPPORT_MATRIX_AUDIT"
STATE_SPEC_DISCOVERY = "SPEC_DISCOVERY"
STATE_SPEC_NORMALIZATION = "SPEC_NORMALIZATION"
STATE_REQUIREMENTS_GENERATION = "REQUIREMENTS_GENERATION"
STATE_VERIFIER_REVIEW = "VERIFIER_REVIEW"
STATE_DEC034_IV = "DEC034_IV"
STATE_PLANNING_READY = "PLANNING_READY"
STATE_IMPLEMENTATION_SIMULATION = "IMPLEMENTATION_SIMULATION"
STATE_EVIDENCE_READY = "EVIDENCE_READY"
STATE_BLOCKED = "BLOCKED"
STATE_DEFERRED = "DEFERRED"

ACQUISITION_STATES = [
    STATE_CANDIDATE,
    STATE_SUPPORT_MATRIX_AUDIT,
    STATE_SPEC_DISCOVERY,
    STATE_SPEC_NORMALIZATION,
    STATE_REQUIREMENTS_GENERATION,
    STATE_VERIFIER_REVIEW,
    STATE_DEC034_IV,
    STATE_PLANNING_READY,
    STATE_IMPLEMENTATION_SIMULATION,
    STATE_EVIDENCE_READY,
]

TERMINAL_STATES = {STATE_BLOCKED, STATE_DEFERRED}

# Evidence required to advance from each state
STATE_EVIDENCE_REQUIREMENTS: dict[str, list[str]] = {
    STATE_CANDIDATE: [
        "format_id_confirmed",
        "backlog_entry_created",
    ],
    STATE_SUPPORT_MATRIX_AUDIT: [
        "support_matrix_audit_report",
        "aspose_coverage_determined",
    ],
    STATE_SPEC_DISCOVERY: [
        "spec_location_documented",
        "spec_access_confirmed_legal",
    ],
    STATE_SPEC_NORMALIZATION: [
        "spec_cached_locally",
        "spec_hash_recorded",
        "spec_normalization_report",
    ],
    STATE_REQUIREMENTS_GENERATION: [
        "ai_generated_requirements",
        "schema_validation_pass",
        "requirements_evidence_bundle",
    ],
    STATE_VERIFIER_REVIEW: [
        "verifier_review_report",
        "lane_r5_pass",
    ],
    STATE_DEC034_IV: [
        "dec034_iv_sprint_complete",
        "iv_bundle_validated",
        "separate_session_confirmed",
    ],
    STATE_PLANNING_READY: [
        "requirements_authoritative_declared",
        "human_review_completed",
    ],
    STATE_IMPLEMENTATION_SIMULATION: [
        "vertical_slice_plan",
        "oracle_approach_confirmed",
        "implementation_simulation_report",
    ],
    STATE_EVIDENCE_READY: [
        "evidence_bundle_built",
        "bundle_validation_pass",
        "gate_11_sub_gates_complete",
    ],
}

# Stale triggers for each state
STATE_STALE_TRIGGERS: dict[str, list[str]] = {
    STATE_SPEC_NORMALIZATION: ["spec_version_changed", "spec_url_changed"],
    STATE_REQUIREMENTS_GENERATION: ["spec_normalization_changed", "schema_version_changed"],
    STATE_VERIFIER_REVIEW: ["requirements_changed"],
    STATE_DEC034_IV: ["requirements_changed", "verifier_review_changed"],
    STATE_PLANNING_READY: ["dec034_iv_changed"],
    STATE_EVIDENCE_READY: ["implementation_changed"],
}


# ---------------------------------------------------------------------------
# Graph node/edge helpers
# ---------------------------------------------------------------------------

def _node(node_id: str, node_type: str, label: str, **attrs) -> dict:
    return {"id": node_id, "type": node_type, "label": label, **attrs}


def _edge(from_id: str, to_id: str, edge_type: str, label: str = "") -> dict:
    return {"from": from_id, "to": to_id, "type": edge_type, "label": label}


def _stable_hash(data: Any) -> str:
    normalized = json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def _governance_copy() -> dict[str, Any]:
    return dict(_GOVERNANCE_FLAGS)


# ---------------------------------------------------------------------------
# Graph 1: Acquisition Dependency Graph
# ---------------------------------------------------------------------------

def build_acquisition_dependency_graph(format_id: str) -> dict:
    """
    Build the acquisition dependency graph for a format.
    Shows prerequisite relationships between lifecycle states.
    """
    nodes = []
    edges = []

    # Create nodes for each state
    for i, state in enumerate(ACQUISITION_STATES):
        nodes.append(_node(
            f"{format_id}:{state}",
            "lifecycle_state",
            state,
            format=format_id,
            order=i,
            evidence_count=len(STATE_EVIDENCE_REQUIREMENTS.get(state, [])),
        ))

    # Create sequential dependency edges
    for i in range(len(ACQUISITION_STATES) - 1):
        from_state = ACQUISITION_STATES[i]
        to_state = ACQUISITION_STATES[i + 1]
        edges.append(_edge(
            f"{format_id}:{from_state}",
            f"{format_id}:{to_state}",
            "prerequisite",
            f"advance_to_{to_state}",
        ))

    # Add BLOCKED/DEFERRED as possible transitions from any state
    nodes.append(_node(f"{format_id}:BLOCKED", "terminal_state", "BLOCKED", format=format_id))
    nodes.append(_node(f"{format_id}:DEFERRED", "terminal_state", "DEFERRED", format=format_id))

    graph_id = _stable_hash({"format": format_id, "graph": "acquisition_dependency"})
    return {
        "graph_type": "acquisition_dependency_graph",
        "graph_id": graph_id,
        "format": format_id,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "simulation_note": f"SIMULATION — acquisition dependency graph for {format_id.upper()}",
        "governance": _governance_copy(),
    }


# ---------------------------------------------------------------------------
# Graph 2: Onboarding Transition Graph
# ---------------------------------------------------------------------------

def build_onboarding_transition_graph(format_id: str, current_state: str = STATE_CANDIDATE) -> dict:
    """
    Build the onboarding state machine transition graph for a format,
    starting from the current state.
    """
    nodes = []
    edges = []

    current_order = ACQUISITION_STATES.index(current_state) if current_state in ACQUISITION_STATES else 0

    for i, state in enumerate(ACQUISITION_STATES):
        is_past = i < current_order
        is_current = i == current_order
        is_future = i > current_order

        status = "PAST" if is_past else ("CURRENT" if is_current else "FUTURE")
        nodes.append(_node(
            f"{format_id}:{state}",
            "onboarding_state",
            state,
            format=format_id,
            status=status,
            order=i,
        ))

    # Transitions from current state forward
    for i in range(current_order, len(ACQUISITION_STATES) - 1):
        from_state = ACQUISITION_STATES[i]
        to_state = ACQUISITION_STATES[i + 1]
        edge_type = "active_transition" if i == current_order else "future_transition"
        edges.append(_edge(
            f"{format_id}:{from_state}",
            f"{format_id}:{to_state}",
            edge_type,
        ))

    graph_id = _stable_hash({
        "format": format_id,
        "current_state": current_state,
        "graph": "onboarding_transition",
    })
    return {
        "graph_type": "onboarding_transition_graph",
        "graph_id": graph_id,
        "format": format_id,
        "current_state": current_state,
        "next_state": ACQUISITION_STATES[current_order + 1] if current_order < len(ACQUISITION_STATES) - 1 else None,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "simulation_note": f"SIMULATION — onboarding transitions for {format_id.upper()} from {current_state}",
        "governance": _governance_copy(),
    }


# ---------------------------------------------------------------------------
# Graph 3: Stale Propagation Graph
# ---------------------------------------------------------------------------

def build_stale_propagation_graph(format_id: str, stale_origin: str = STATE_SPEC_NORMALIZATION) -> dict:
    """
    Build the stale-state propagation graph showing how stale state
    propagates downstream through the lifecycle.
    """
    nodes = []
    edges = []

    origin_order = ACQUISITION_STATES.index(stale_origin) if stale_origin in ACQUISITION_STATES else 0

    for i, state in enumerate(ACQUISITION_STATES):
        if i < origin_order:
            stale_status = "UNAFFECTED"
        elif i == origin_order:
            stale_status = "STALE_ORIGIN"
        else:
            stale_status = "STALE_PROPAGATED"

        nodes.append(_node(
            f"{format_id}:{state}",
            "stale_state_node",
            state,
            format=format_id,
            stale_status=stale_status,
            stale_triggers=STATE_STALE_TRIGGERS.get(state, []),
        ))

    # Stale propagation edges
    for i in range(origin_order, len(ACQUISITION_STATES) - 1):
        from_state = ACQUISITION_STATES[i]
        to_state = ACQUISITION_STATES[i + 1]
        edges.append(_edge(
            f"{format_id}:{from_state}",
            f"{format_id}:{to_state}",
            "stale_propagates_to",
        ))

    graph_id = _stable_hash({
        "format": format_id,
        "stale_origin": stale_origin,
        "graph": "stale_propagation",
    })
    return {
        "graph_type": "stale_propagation_graph",
        "graph_id": graph_id,
        "format": format_id,
        "stale_origin": stale_origin,
        "stale_affected_states": [ACQUISITION_STATES[i] for i in range(origin_order, len(ACQUISITION_STATES))],
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "simulation_note": f"SIMULATION — stale propagation from {stale_origin} for {format_id.upper()}",
        "governance": _governance_copy(),
    }


# ---------------------------------------------------------------------------
# Graph 4: Evidence Dependency Graph
# ---------------------------------------------------------------------------

def build_evidence_dependency_graph(format_id: str) -> dict:
    """
    Build the evidence dependency graph showing which evidence artifacts
    are required at each lifecycle state.
    """
    nodes = []
    edges = []

    for state, evidence_list in STATE_EVIDENCE_REQUIREMENTS.items():
        state_node_id = f"{format_id}:{state}"
        nodes.append(_node(state_node_id, "lifecycle_state", state, format=format_id))

        for evidence in evidence_list:
            ev_node_id = f"{format_id}:{state}:{evidence}"
            nodes.append(_node(ev_node_id, "evidence_artifact", evidence, format=format_id, state=state))
            edges.append(_edge(
                ev_node_id,
                state_node_id,
                "required_for_advance",
            ))

    graph_id = _stable_hash({"format": format_id, "graph": "evidence_dependency"})
    total_evidence = sum(len(v) for v in STATE_EVIDENCE_REQUIREMENTS.values())
    return {
        "graph_type": "evidence_dependency_graph",
        "graph_id": graph_id,
        "format": format_id,
        "total_evidence_artifacts": total_evidence,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "simulation_note": f"SIMULATION — evidence dependencies for {format_id.upper()}",
        "governance": _governance_copy(),
    }


# ---------------------------------------------------------------------------
# Graph 5: Replay Lineage Graph
# ---------------------------------------------------------------------------

def build_replay_lineage_graph(format_id: str, sprints: list[str] | None = None) -> dict:
    """
    Build the replay lineage graph showing sprint history and replay chain.
    """
    if sprints is None:
        # Default R10/R11/R12 sprint chain
        sprints = [
            "R10-ACQUISITION-ENGINE-POC",
            "R10-CLOSURE-HARDENING",
            "R11-ACQUISITION-PLANNING-INTEGRATION",
            "R12-ACQUISITION-ENGINE-IV",
        ]

    nodes = []
    edges = []

    for i, sprint in enumerate(sprints):
        nodes.append(_node(
            f"sprint:{sprint}",
            "sprint_node",
            sprint,
            format=format_id,
            sprint_index=i,
        ))
        if i > 0:
            edges.append(_edge(
                f"sprint:{sprints[i-1]}",
                f"sprint:{sprint}",
                "replay_chains_to",
            ))

    graph_id = _stable_hash({
        "format": format_id,
        "sprints": sprints,
        "graph": "replay_lineage",
    })
    return {
        "graph_type": "replay_lineage_graph",
        "graph_id": graph_id,
        "format": format_id,
        "sprint_count": len(sprints),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "simulation_note": f"SIMULATION — sprint replay lineage for {format_id.upper()}",
        "governance": _governance_copy(),
    }


# ---------------------------------------------------------------------------
# Graph 6: Verification Dependency Graph
# ---------------------------------------------------------------------------

def build_verification_dependency_graph(format_id: str) -> dict:
    """
    Build the DEC-034 IV verification dependency graph.
    Shows which stages require independent verification.
    """
    iv_stages = [
        ("REQUIREMENTS_GENERATION", "DEC034_IV", "requirements_iv"),
        ("PLANNING_READY", "human_review", "planning_iv"),
        ("EVIDENCE_READY", "gate_11_sub_gates", "evidence_iv"),
    ]

    nodes = []
    edges = []

    for source_state, iv_stage, label in iv_stages:
        source_id = f"{format_id}:{source_state}"
        iv_id = f"{format_id}:IV:{iv_stage}"
        nodes.append(_node(source_id, "lifecycle_state", source_state, format=format_id))
        nodes.append(_node(iv_id, "iv_requirement", iv_stage, format=format_id, iv_label=label))
        edges.append(_edge(source_id, iv_id, "requires_iv", label))

    graph_id = _stable_hash({"format": format_id, "graph": "verification_dependency"})
    return {
        "graph_type": "verification_dependency_graph",
        "graph_id": graph_id,
        "format": format_id,
        "iv_stages": [s[1] for s in iv_stages],
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "simulation_note": f"SIMULATION — IV dependencies for {format_id.upper()} (DEC-034)",
        "governance": _governance_copy(),
    }


# ---------------------------------------------------------------------------
# Multi-format isolation check
# ---------------------------------------------------------------------------

def simulate_multi_format_isolation(format_ids: list[str]) -> dict:
    """
    Verify that acquisition graphs for different formats are fully isolated —
    no shared nodes, no cross-format state contamination.

    Returns
    -------
    dict with isolation check results
    """
    all_node_ids: set[str] = set()
    violations: list[str] = []
    format_graphs = {}

    for fmt in format_ids:
        dep_graph = build_acquisition_dependency_graph(fmt)
        fmt_nodes = {n["id"] for n in dep_graph["nodes"]}
        overlap = all_node_ids & fmt_nodes
        if overlap:
            violations.append(f"{fmt}: node overlap with prior formats: {overlap}")
        all_node_ids |= fmt_nodes
        format_graphs[fmt] = dep_graph

    return {
        "checked_formats": format_ids,
        "total_nodes": len(all_node_ids),
        "violations": violations,
        "isolation_valid": len(violations) == 0,
        "governance": _governance_copy(),
    }


# ---------------------------------------------------------------------------
# Main entrypoint: simulate all graphs for a format
# ---------------------------------------------------------------------------

def simulate_acquisition_graphs(
    format_id: str,
    current_state: str = STATE_CANDIDATE,
    stale_origin: str = STATE_SPEC_NORMALIZATION,
    sprints: list[str] | None = None,
) -> dict:
    """
    Run all 6 acquisition graph simulations for a format.

    Parameters
    ----------
    format_id : str
        Format to simulate (e.g. 'zst', 'hwp')
    current_state : str
        Current lifecycle state for onboarding transition graph
    stale_origin : str
        State where stale condition originates for stale propagation graph
    sprints : list[str] | None
        Sprint history for replay lineage graph (uses default if None)

    Returns
    -------
    dict — AcquisitionGraphBundle with all 6 graphs
    """
    dep = build_acquisition_dependency_graph(format_id)
    onboard = build_onboarding_transition_graph(format_id, current_state)
    stale = build_stale_propagation_graph(format_id, stale_origin)
    evidence = build_evidence_dependency_graph(format_id)
    replay = build_replay_lineage_graph(format_id, sprints)
    verify = build_verification_dependency_graph(format_id)

    all_graphs = {
        "acquisition_dependency_graph": dep,
        "onboarding_transition_graph": onboard,
        "stale_propagation_graph": stale,
        "evidence_dependency_graph": evidence,
        "replay_lineage_graph": replay,
        "verification_dependency_graph": verify,
    }

    total_nodes = sum(g["node_count"] for g in all_graphs.values())
    total_edges = sum(g["edge_count"] for g in all_graphs.values())

    simulation_id = _stable_hash({
        "format": format_id,
        "current_state": current_state,
        "stale_origin": stale_origin,
    })

    return {
        "format": format_id,
        "simulation_id": simulation_id,
        "graph_count": len(all_graphs),
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "graphs": all_graphs,
        "governance": _governance_copy(),
        "simulation_note": (
            f"SIMULATION — acquisition graphs for {format_id.upper()}. "
            "Not an acquisition authorization. Dry-run only."
        ),
    }
