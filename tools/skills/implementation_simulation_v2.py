"""
implementation_simulation_v2.py -- Lane F (FORMAT-FACTORY-R10)

Governed implementation simulation v2 with structured graph outputs.
Produces 6 graph types for format acquisition planning:
  - dependency_graph
  - taskcard_graph
  - evidence_graph
  - replay_lineage_graph
  - stale_state_graph
  - authority_graph

SIMULATION ONLY — no source mutation, no gate approval, no real execution.

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
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
    "graphs_are_simulation_outputs_not_authorizations": True,
}

# ---------------------------------------------------------------------------
# Node / Edge types
# ---------------------------------------------------------------------------

NODE_TYPE_FORMAT = "format"
NODE_TYPE_GATE = "gate"
NODE_TYPE_TASK = "task"
NODE_TYPE_EVIDENCE = "evidence"
NODE_TYPE_AUTHORITY = "authority"
NODE_TYPE_STALE_DOMAIN = "stale_domain"
NODE_TYPE_FINGERPRINT = "fingerprint"

EDGE_TYPE_DEPENDENCY = "depends_on"
EDGE_TYPE_SEQUENCE = "followed_by"
EDGE_TYPE_PRODUCES = "produces"
EDGE_TYPE_REQUIRES = "requires"
EDGE_TYPE_PROPAGATES_TO = "propagates_to"
EDGE_TYPE_AUTHORIZES = "authorizes"
EDGE_TYPE_CHAINS_TO = "chains_to"

# Lifecycle gates in order
GATE_SEQUENCE = [
    "SUPPORT_MATRIX_AUDIT",
    "SPEC_DISCOVERY",
    "SPEC_NORMALIZATION",
    "REQUIREMENTS_GENERATION",
    "VERIFIER_REVIEW",
    "DEC034_IV",
    "PLANNING_READY",
    "IMPLEMENTATION_SIMULATION",
    "EVIDENCE_READY",
    "GATE_11",
]

# Task cards per gate
_GATE_TASKS: dict[str, list[str]] = {
    "SUPPORT_MATRIX_AUDIT": [
        "[SIM] Audit Aspose support matrix for format",
        "[SIM] Verify legal clearance for spec access",
        "[SIM] Record audit result in backlog",
    ],
    "SPEC_DISCOVERY": [
        "[SIM] Locate and download public spec document",
        "[SIM] Assess spec completeness score",
        "[SIM] Identify spec gaps requiring reverse engineering",
    ],
    "SPEC_NORMALIZATION": [
        "[SIM] Extract structure and encoding rules from spec",
        "[SIM] Produce normalized spec summary artifact",
        "[SIM] Schema-validate normalization output",
    ],
    "REQUIREMENTS_GENERATION": [
        "[SIM] Generate candidate requirements from normalized spec",
        "[SIM] Schema-validate all generated requirements",
        "[SIM] Tag requirements with PENDING_IV status",
    ],
    "VERIFIER_REVIEW": [
        "[SIM] Independent agent reviews requirements",
        "[SIM] Check for completeness and consistency",
        "[SIM] Tag passing requirements VERIFIER_REVIEWED",
    ],
    "DEC034_IV": [
        "[SIM] Run DEC-034 independent verification sprint",
        "[SIM] Confirm requirements authority status",
        "[SIM] Tag requirements REQUIREMENTS_AUTHORITATIVE",
    ],
    "PLANNING_READY": [
        "[SIM] Generate implementation plan from authoritative requirements",
        "[SIM] Assign task cards to sprint lanes",
        "[SIM] Validate planning bundle runtime",
    ],
    "IMPLEMENTATION_SIMULATION": [
        "[SIM] Simulate C4-C6 vertical slice implementation",
        "[SIM] Run governed execution simulator",
        "[SIM] Capture simulation output artifacts",
    ],
    "EVIDENCE_READY": [
        "[SIM] Collect all gate evidence artifacts",
        "[SIM] Build and validate evidence bundle",
        "[SIM] Record bundle hash in authority registry",
    ],
    "GATE_11": [
        "[SIM] Prepare Gate 11 sub-gate evidence (G11-A through G11-G)",
        "[SIM] Await human review and approval (Gate 11 CANNOT be self-approved)",
        "[SIM] commercial_product_ready remains false until human approves Gate 11",
    ],
}

# Stale propagation domains
_STALE_DOMAINS = [
    "spec_cache",
    "requirements",
    "planning_slices",
    "simulation",
    "evidence_bundle",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stable_hash(data: Any) -> str:
    payload = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _governance_copy() -> dict[str, Any]:
    return dict(_GOVERNANCE_FLAGS)


def _node(node_id: str, label: str, node_type: str, **metadata: Any) -> dict[str, Any]:
    return {"id": node_id, "label": label, "type": node_type, "metadata": dict(metadata)}


def _edge(from_id: str, to_id: str, edge_type: str, label: str = "") -> dict[str, Any]:
    return {"from": from_id, "to": to_id, "type": edge_type, "label": label}


# ---------------------------------------------------------------------------
# Graph builders
# ---------------------------------------------------------------------------

def build_dependency_graph(fmt: str, formats_in_group: list[str] | None = None) -> dict[str, Any]:
    """
    Build a dependency graph for a format within its group.
    Nodes: format nodes + gate nodes.
    Edges: format depends_on gates; gates have sequential dependencies.
    """
    group = list(formats_in_group or [fmt])
    nodes: list[dict] = []
    edges: list[dict] = []

    # Format nodes
    for f in group:
        nodes.append(_node(f"fmt:{f}", f.upper(), NODE_TYPE_FORMAT, is_primary=(f == fmt)))

    # Gate nodes
    for gate in GATE_SEQUENCE:
        nodes.append(_node(
            f"gate:{fmt}:{gate}",
            gate.replace("_", " "),
            NODE_TYPE_GATE,
            format=fmt,
            gate_self_approval_allowed=False,
        ))

    # Format → first gate
    edges.append(_edge(f"fmt:{fmt}", f"gate:{fmt}:{GATE_SEQUENCE[0]}", EDGE_TYPE_SEQUENCE, "enters"))

    # Gate → Gate sequence
    for i in range(len(GATE_SEQUENCE) - 1):
        edges.append(_edge(
            f"gate:{fmt}:{GATE_SEQUENCE[i]}",
            f"gate:{fmt}:{GATE_SEQUENCE[i + 1]}",
            EDGE_TYPE_SEQUENCE,
            "followed_by",
        ))

    # Cross-format dependency edge (hwp depends on hwpx audit)
    if fmt == "hwp" and "hwpx" in group:
        edges.append(_edge("fmt:hwpx", f"gate:{fmt}:SUPPORT_MATRIX_AUDIT", EDGE_TYPE_DEPENDENCY, "audit_informs"))
    if fmt == "hwt" and "hwpx" in group:
        edges.append(_edge("fmt:hwpx", f"gate:{fmt}:SPEC_DISCOVERY", EDGE_TYPE_DEPENDENCY, "spec_informs"))
    if fmt == "egg" and "alz" in group:
        edges.append(_edge("fmt:alz", f"gate:{fmt}:SPEC_DISCOVERY", EDGE_TYPE_DEPENDENCY, "spec_informs"))

    graph_id = _stable_hash({"type": "dependency", "fmt": fmt, "group": sorted(group)})
    return {
        "graph_id": graph_id,
        "graph_type": "dependency_graph",
        "format": fmt,
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "governance": _governance_copy(),
        "dry_run_only": True,
        "graph_note": "SIMULATION — dependency graph for planning purposes only.",
    }


def build_taskcard_graph(fmt: str, gates_completed: list[str] | None = None) -> dict[str, Any]:
    """
    Build a task card graph for a format, showing ordered tasks per gate.
    Nodes: task nodes grouped by gate.
    Edges: sequential task ordering within each gate; gate → task links.
    """
    completed = set(gates_completed or [])
    nodes: list[dict] = []
    edges: list[dict] = []
    prev_gate_last_task: str | None = None

    for gate in GATE_SEQUENCE:
        tasks = _GATE_TASKS.get(gate, [])
        gate_node_id = f"gate:{fmt}:{gate}"
        nodes.append(_node(
            gate_node_id,
            gate.replace("_", " "),
            NODE_TYPE_GATE,
            format=fmt,
            completed=(gate in completed),
        ))

        # Link previous gate's last task → this gate node
        if prev_gate_last_task:
            edges.append(_edge(prev_gate_last_task, gate_node_id, EDGE_TYPE_SEQUENCE, "gate_transition"))

        task_ids: list[str] = []
        for i, task in enumerate(tasks):
            task_id = f"task:{fmt}:{gate}:{i}"
            nodes.append(_node(
                task_id,
                task,
                NODE_TYPE_TASK,
                format=fmt,
                gate=gate,
                task_index=i,
                completed=(gate in completed),
            ))
            task_ids.append(task_id)
            edges.append(_edge(gate_node_id, task_id, EDGE_TYPE_SEQUENCE, "contains"))
            if i > 0:
                edges.append(_edge(task_ids[i - 1], task_id, EDGE_TYPE_SEQUENCE, "then"))

        if task_ids:
            prev_gate_last_task = task_ids[-1]

    graph_id = _stable_hash({"type": "taskcard", "fmt": fmt, "completed": sorted(completed)})
    return {
        "graph_id": graph_id,
        "graph_type": "taskcard_graph",
        "format": fmt,
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "gates_completed": sorted(completed),
        "total_gates": len(GATE_SEQUENCE),
        "governance": _governance_copy(),
        "dry_run_only": True,
        "graph_note": "SIMULATION — task card graph for sprint planning. No execution authorized.",
    }


def build_evidence_graph(fmt: str) -> dict[str, Any]:
    """
    Build an evidence graph showing what evidence artifacts each gate produces.
    Nodes: gate nodes + evidence artifact nodes.
    Edges: gate PRODUCES evidence; evidence REQUIRED_BY next gate.
    """
    nodes: list[dict] = []
    edges: list[dict] = []

    evidence_map = {
        "SUPPORT_MATRIX_AUDIT": "audit_result_record",
        "SPEC_DISCOVERY": "spec_document_reference",
        "SPEC_NORMALIZATION": "normalized_spec_artifact",
        "REQUIREMENTS_GENERATION": "generated_requirements_set",
        "VERIFIER_REVIEW": "verifier_review_report",
        "DEC034_IV": "iv_sprint_report",
        "PLANNING_READY": "planning_bundle",
        "IMPLEMENTATION_SIMULATION": "simulation_output_artifact",
        "EVIDENCE_READY": "evidence_bundle_hash",
        "GATE_11": "gate_11_human_approval_record",
    }

    for gate in GATE_SEQUENCE:
        gate_id = f"gate:{fmt}:{gate}"
        nodes.append(_node(gate_id, gate.replace("_", " "), NODE_TYPE_GATE, format=fmt))

        ev_name = evidence_map.get(gate, f"evidence_{gate.lower()}")
        ev_id = f"evidence:{fmt}:{ev_name}"
        nodes.append(_node(
            ev_id,
            ev_name.replace("_", " "),
            NODE_TYPE_EVIDENCE,
            format=fmt,
            gate=gate,
            visibility="internal",
        ))
        edges.append(_edge(gate_id, ev_id, EDGE_TYPE_PRODUCES, "produces"))

    # Evidence → next gate REQUIRES
    gate_evidence_ids = [f"evidence:{fmt}:{evidence_map.get(g, f'evidence_{g.lower()}')}" for g in GATE_SEQUENCE]
    for i in range(len(GATE_SEQUENCE) - 1):
        next_gate_id = f"gate:{fmt}:{GATE_SEQUENCE[i + 1]}"
        edges.append(_edge(gate_evidence_ids[i], next_gate_id, EDGE_TYPE_REQUIRES, "required_by"))

    graph_id = _stable_hash({"type": "evidence", "fmt": fmt})
    return {
        "graph_id": graph_id,
        "graph_type": "evidence_graph",
        "format": fmt,
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "evidence_artifacts": list(evidence_map.values()),
        "governance": _governance_copy(),
        "dry_run_only": True,
        "graph_note": "SIMULATION — evidence dependency graph. All artifacts are simulated.",
    }


def build_replay_lineage_graph(fmt: str, sprint_ids: list[str] | None = None) -> dict[str, Any]:
    """
    Build a replay lineage graph showing hash-chained sprint fingerprints.
    Nodes: fingerprint nodes per sprint.
    Edges: chains_to links forming the hash chain.
    """
    sprints = sprint_ids or [f"R{i}" for i in range(1, 6)]
    nodes: list[dict] = []
    edges: list[dict] = []
    prior_fp = "GENESIS"
    prior_id = None

    for i, sprint in enumerate(sprints):
        fp_data = {"fmt": fmt, "sprint": sprint, "prior": prior_fp}
        fp = _stable_hash(fp_data)
        lineage_hash = _stable_hash({"prior": prior_fp, "fingerprint": fp, "sprint_id": sprint})
        node_id = f"fp:{fmt}:{sprint}"
        nodes.append(_node(
            node_id,
            f"{sprint}: {fp[:8]}…",
            NODE_TYPE_FINGERPRINT,
            format=fmt,
            sprint_id=sprint,
            fingerprint=fp,
            lineage_hash=lineage_hash,
            is_genesis=(i == 0),
            entry_index=i,
        ))
        if prior_id:
            edges.append(_edge(prior_id, node_id, EDGE_TYPE_CHAINS_TO, "chains_to"))
        prior_fp = fp
        prior_id = node_id

    graph_id = _stable_hash({"type": "replay_lineage", "fmt": fmt, "sprints": sprints})
    return {
        "graph_id": graph_id,
        "graph_type": "replay_lineage_graph",
        "format": fmt,
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "sprint_count": len(sprints),
        "genesis_sprint": sprints[0] if sprints else None,
        "latest_sprint": sprints[-1] if sprints else None,
        "governance": _governance_copy(),
        "dry_run_only": True,
        "graph_note": "SIMULATION — replay lineage hash chain for drift detection.",
    }


def build_stale_state_graph(fmt: str) -> dict[str, Any]:
    """
    Build a stale-state propagation graph for a format.
    Nodes: stale domain nodes.
    Edges: propagates_to links following the propagation chain.
    """
    nodes: list[dict] = []
    edges: list[dict] = []

    for domain in _STALE_DOMAINS:
        nodes.append(_node(
            f"stale:{fmt}:{domain}",
            domain.replace("_", " "),
            NODE_TYPE_STALE_DOMAIN,
            format=fmt,
            domain=domain,
            severity="TIER_0_CLEAN",  # default; runtime checks would update this
        ))

    # Propagation chain: spec_cache → requirements → planning_slices → simulation → evidence_bundle
    for i in range(len(_STALE_DOMAINS) - 1):
        from_id = f"stale:{fmt}:{_STALE_DOMAINS[i]}"
        to_id = f"stale:{fmt}:{_STALE_DOMAINS[i + 1]}"
        edges.append(_edge(from_id, to_id, EDGE_TYPE_PROPAGATES_TO, "stale_propagates_to"))

    graph_id = _stable_hash({"type": "stale_state", "fmt": fmt, "domains": _STALE_DOMAINS})
    return {
        "graph_id": graph_id,
        "graph_type": "stale_state_graph",
        "format": fmt,
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "stale_domains": list(_STALE_DOMAINS),
        "governance": _governance_copy(),
        "dry_run_only": True,
        "graph_note": "SIMULATION — stale-state propagation topology. Severity populated at runtime.",
    }


def build_authority_graph(fmt: str) -> dict[str, Any]:
    """
    Build an authority chain graph for a format.
    Nodes: authority sources (spec → requirements → planning → simulation).
    Edges: authorizes links from upstream to downstream.
    """
    authority_chain = [
        ("auth:spec_document", "Spec Document", NODE_TYPE_AUTHORITY),
        ("auth:normalized_spec", "Normalized Spec", NODE_TYPE_AUTHORITY),
        ("auth:generated_requirements", "Generated Requirements (PENDING_IV)", NODE_TYPE_AUTHORITY),
        ("auth:verifier_reviewed", "Verifier-Reviewed Requirements", NODE_TYPE_AUTHORITY),
        ("auth:requirements_authoritative", "Requirements (AUTHORITATIVE — post DEC-034 IV)", NODE_TYPE_AUTHORITY),
        ("auth:planning_bundle", "Planning Bundle", NODE_TYPE_AUTHORITY),
        ("auth:simulation_output", "Simulation Output", NODE_TYPE_AUTHORITY),
        ("auth:gate_11_approval", "Gate 11 — Human Approval (NOT APPROVED)", NODE_TYPE_AUTHORITY),
    ]

    nodes: list[dict] = []
    edges: list[dict] = []

    for node_id, label, node_type in authority_chain:
        fmt_node_id = f"{node_id}:{fmt}"
        is_approved = node_id == "auth:gate_11_approval"
        nodes.append(_node(
            fmt_node_id,
            label,
            node_type,
            format=fmt,
            approved=(False if is_approved else None),
            gate_self_approval_allowed=False,
        ))

    for i in range(len(authority_chain) - 1):
        from_id = f"{authority_chain[i][0]}:{fmt}"
        to_id = f"{authority_chain[i + 1][0]}:{fmt}"
        edges.append(_edge(from_id, to_id, EDGE_TYPE_AUTHORIZES, "authorizes"))

    graph_id = _stable_hash({"type": "authority", "fmt": fmt})
    return {
        "graph_id": graph_id,
        "graph_type": "authority_graph",
        "format": fmt,
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "gate_11_approved": False,
        "governance": _governance_copy(),
        "dry_run_only": True,
        "graph_note": (
            "SIMULATION — authority chain graph. Gate 11 NOT APPROVED. "
            "commercial_product_ready: false."
        ),
    }


# ---------------------------------------------------------------------------
# Full simulation v2 output
# ---------------------------------------------------------------------------

def simulate_v2(
    fmt: str,
    formats_in_group: list[str] | None = None,
    gates_completed: list[str] | None = None,
    sprint_ids: list[str] | None = None,
) -> dict[str, Any]:
    """
    Produce all 6 simulation graphs for a single format.

    Parameters
    ----------
    fmt : str
        Format ID.
    formats_in_group : list[str] | None
        Other formats in the same acquisition group (for cross-format dependency edges).
    gates_completed : list[str] | None
        Gates already completed for this format.
    sprint_ids : list[str] | None
        Sprint IDs for replay lineage (defaults to R1-R5).

    Returns
    -------
    dict  JSON-serializable v2 simulation output with all 6 graphs.
    """
    group = formats_in_group or [fmt]
    completed = gates_completed or []
    sprints = sprint_ids or [f"R{i}" for i in range(1, 6)]

    graphs = {
        "dependency_graph": build_dependency_graph(fmt, group),
        "taskcard_graph": build_taskcard_graph(fmt, completed),
        "evidence_graph": build_evidence_graph(fmt),
        "replay_lineage_graph": build_replay_lineage_graph(fmt, sprints),
        "stale_state_graph": build_stale_state_graph(fmt),
        "authority_graph": build_authority_graph(fmt),
    }

    simulation_id = _stable_hash({
        "fmt": fmt,
        "group": sorted(group),
        "completed": sorted(completed),
        "sprints": sprints,
    })

    total_nodes = sum(g["node_count"] for g in graphs.values())
    total_edges = sum(g["edge_count"] for g in graphs.values())

    return {
        "simulation_id": simulation_id,
        "format": fmt,
        "graphs": graphs,
        "graph_types": sorted(graphs.keys()),
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "gate_11_approved": False,
        "governance": _governance_copy(),
        "dry_run_only": True,
        "autonomous_execution_allowed": False,
        "simulation_note": (
            "SIMULATION v2 — all graphs are planning estimates. "
            "No execution authorized. Gate 11 NOT APPROVED."
        ),
    }


def simulate_v2_standard_formats() -> dict[str, Any]:
    """
    Run simulate_v2 for the standard format set (fods, fodt, hwpx, hwp, alz, egg).
    """
    standard_formats = {
        "fods": {"group": ["fods", "fodt"], "completed": list(GATE_SEQUENCE[:-1])},
        "fodt": {"group": ["fods", "fodt"], "completed": list(GATE_SEQUENCE[:-1])},
        "hwpx": {"group": ["hwpx", "hwp", "hwt"], "completed": []},
        "hwp": {"group": ["hwpx", "hwp", "hwt"], "completed": []},
        "alz": {"group": ["alz", "egg"], "completed": []},
        "egg": {"group": ["alz", "egg"], "completed": []},
    }

    per_format: dict[str, Any] = {}
    for fmt, kwargs in standard_formats.items():
        per_format[fmt] = simulate_v2(
            fmt,
            formats_in_group=kwargs["group"],
            gates_completed=kwargs["completed"],
        )

    agg_id = _stable_hash({"type": "v2_standard", "formats": sorted(standard_formats.keys())})
    return {
        "aggregate_simulation_id": agg_id,
        "formats_simulated": sorted(standard_formats.keys()),
        "per_format": per_format,
        "format_count": len(standard_formats),
        "gate_11_approved": False,
        "governance": _governance_copy(),
        "dry_run_only": True,
        "autonomous_execution_allowed": False,
    }
