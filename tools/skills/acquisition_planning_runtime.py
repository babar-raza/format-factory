"""
acquisition_planning_runtime.py -- R11 Deliverable (FORMAT-FACTORY-R11)

Unified Acquisition Planning Runtime for the format-factory governed planning layer.

PURPOSE:
  Integrate the R10 acquisition-engine POC tools into a cohesive, governed
  acquisition-planning runtime that produces an auditable acquisition plan
  for the first candidate format.

  This runtime CONSUMES:
  - acquisition_lifecycle_simulator.KNOWN_FORMAT_PROFILES
  - candidate_format_backlog.ALL_BACKLOG / get_candidates_by_tier()
  - public_spec_readiness_scorer.score_standard_candidates() / score_multiple_formats()
  - multi_format_acquisition_planner.plan_all_groups()
  - implementation_simulation_v2.simulate_v2()

  This runtime PRODUCES:
  - Ranked candidate output
  - First-candidate acquisition plan
  - Lifecycle simulation for selected candidate
  - Simulation v2 graph summary
  - Governance-compliant PlanningBundle

SIMULATION ONLY — no source mutation, no gate approval, no internet fetches,
no real acquisition execution.

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

# R10 tool imports
from acquisition_lifecycle_simulator import (
    KNOWN_FORMAT_PROFILES,
    simulate_format_acquisition,
)
from candidate_format_backlog import (
    TIER_A_NEAR_TERM,
    TIER_B_MEDIUM_TERM,
    TIER_C_LONG_TERM,
    TIER_ACTIVE,
    get_candidates_by_tier,
)
from public_spec_readiness_scorer import (
    STANDARD_CANDIDATE_SPECS,
    score_multiple_formats,
)
from multi_format_acquisition_planner import plan_all_groups
from implementation_simulation_v2 import simulate_v2


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
    "scores_are_estimates_not_decisions": True,
    "plans_are_estimates_not_commitments": True,
}

# Valid tier string → backlog tier constant mapping
_TIER_MAP: dict[str, str] = {
    "TIER_A": TIER_A_NEAR_TERM,
    "TIER_B": TIER_B_MEDIUM_TERM,
    "TIER_C": TIER_C_LONG_TERM,
    "TIER_ACTIVE": TIER_ACTIVE,
}

# Known scorer specs indexed by format_id for quick lookup
_KNOWN_SCORER_SPECS: dict[str, dict] = {
    s["fmt"]: s for s in STANDARD_CANDIDATE_SPECS
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stable_hash(data: Any) -> str:
    """Deterministic SHA-256 of any JSON-serializable object, first 16 hex chars."""
    normalized = json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def _governance_copy() -> dict[str, Any]:
    """Return a shallow copy of governance flags (not a reference)."""
    return dict(_GOVERNANCE_FLAGS)


def _backlog_entry_to_scorer_spec(entry: dict) -> dict:
    """
    Convert a backlog entry to a scorer spec dict, using STANDARD_CANDIDATE_SPECS
    data where available, or deriving from backlog fields otherwise.
    """
    fmt = entry["format_id"]
    # Use known spec if available (authoritative)
    if fmt in _KNOWN_SCORER_SPECS:
        return dict(_KNOWN_SCORER_SPECS[fmt])

    # Derive from backlog entry
    spec_type = entry.get("spec_type", "unknown")
    binary_format = spec_type == "reverse_engineering"
    sample_files_known = spec_type in ("full_public", "partial_public", "community_documented")
    legal_use_clear = spec_type == "full_public"
    open_source_reference = False
    existing_parsers_known = False

    return {
        "fmt": fmt,
        "spec_type": spec_type,
        "category": entry.get("category", "word_processing"),
        "binary_format": binary_format,
        "sample_files_known": sample_files_known,
        "legal_use_clear": legal_use_clear,
        "open_source_reference": open_source_reference,
        "existing_parsers_known": existing_parsers_known,
    }


def _build_graph_summary(sim_v2: dict) -> dict:
    """Extract a concise graph summary from simulate_v2 output."""
    graphs = sim_v2.get("graphs", {})
    summary = {}
    for graph_type, graph_data in graphs.items():
        summary[graph_type] = {
            "node_count": graph_data.get("node_count", 0),
            "edge_count": graph_data.get("edge_count", 0),
            "graph_id": graph_data.get("graph_id", ""),
        }
    return {
        "format": sim_v2.get("format", ""),
        "simulation_id": sim_v2.get("simulation_id", ""),
        "total_nodes": sim_v2.get("total_nodes", 0),
        "total_edges": sim_v2.get("total_edges", 0),
        "per_graph": summary,
        "gate_11_approved": False,
        "graph_note": (
            "SIMULATION — graph summary only. Full graphs available via simulate_v2()."
        ),
    }


def _build_proposed_acquisition_lanes(first_candidate: str, lifecycle_sim: dict) -> list[str]:
    """Propose acquisition sprint lanes for the first candidate."""
    state = lifecycle_sim.get("current_state", "CANDIDATE")
    lanes = []
    if state == "CANDIDATE":
        lanes.append(f"[LANE] Support-matrix audit for {first_candidate.upper()}")
        lanes.append(f"[LANE] Spec discovery and classification for {first_candidate.upper()}")
        lanes.append(f"[LANE] Legal clearance review for {first_candidate.upper()} spec access")
    elif state == "SUPPORT_MATRIX_AUDIT":
        lanes.append(f"[LANE] Spec discovery for {first_candidate.upper()}")
    elif state == "PLANNING_READY":
        lanes.append(f"[LANE] Implementation simulation (R9-style) for {first_candidate.upper()}")
    elif state == "EVIDENCE_READY":
        lanes.append(f"[LANE] Gate 11 preparation sub-gates for {first_candidate.upper()}")
    lanes.append("[LANE] DEC-034 independent verification sprint (separate session)")
    lanes.append("[LANE] Evidence bundle build and validation")
    return lanes


def _build_risks(first_candidate: str, scorer_result: dict) -> list[str]:
    """Build risk list from scorer and lifecycle data."""
    risks = []
    score = scorer_result.get("composite_score", 0)
    spec_type = scorer_result.get("spec_type", "unknown")

    if spec_type == "reverse_engineering":
        risks.append(f"[RISK] {first_candidate.upper()} requires reverse engineering — legal review required before spec access")
    if spec_type in ("none", "unknown"):
        risks.append(f"[RISK] No known public spec for {first_candidate.upper()} — acquisition may be blocked at SPEC_DISCOVERY")
    if score < 7.0:
        risks.append(f"[RISK] Score {score}/10 below ACQUISITION_READY threshold (7.0) — investigation sprint recommended first")
    risks.append("[RISK] aspose_supported is None — audit required before DEC-033 compatibility is known")
    risks.append("[RISK] Requirements generation has not started — REQUIREMENTS_AUTHORITATIVE state not reached")
    return risks


def _build_non_goals(first_candidate: str) -> list[str]:
    """Build explicit non-goals for the acquisition plan."""
    return [
        f"[NON-GOAL] Do NOT begin implementation of {first_candidate.upper()} until PLANNING_READY state is reached",
        "[NON-GOAL] Do NOT approve Gate 11 for any format (requires human review)",
        "[NON-GOAL] Do NOT set commercial_product_ready=True",
        "[NON-GOAL] Do NOT fetch internet resources (spec cache required locally first)",
        "[NON-GOAL] Do NOT execute autonomous rollout",
        "[NON-GOAL] Do NOT modify src/net/ or src/python/ product sources",
    ]


def _build_rationale(first_candidate: str, scorer_result: dict, ranked: list[dict]) -> str:
    """Build selection rationale for the first candidate."""
    score = scorer_result.get("composite_score", 0)
    readiness_tier = scorer_result.get("readiness_tier", "UNKNOWN")
    spec_type = scorer_result.get("spec_type", "unknown")
    rank = next(
        (i + 1 for i, c in enumerate(ranked) if c.get("format_id") == first_candidate),
        1
    )
    return (
        f"{first_candidate.upper()} selected as first candidate (rank #1 of {len(ranked)}, "
        f"score={score}/10, tier={readiness_tier}). "
        f"Spec type: {spec_type}. "
        f"This is the highest-scored candidate in the selected tier based on 8-dimension "
        f"public-spec readiness assessment. Score is an ESTIMATE and does not authorize acquisition — "
        f"human review and support-matrix audit required before proceeding."
    )


# ---------------------------------------------------------------------------
# Main runtime entrypoint
# ---------------------------------------------------------------------------

def run_acquisition_planning(
    tier: str = "TIER_A",
    top_n: int = 5,
    dry_run: bool = True,
) -> dict:
    """
    Run the unified acquisition planning pipeline.

    Parameters
    ----------
    tier : str
        Tier to select candidates from: "TIER_A", "TIER_B", "TIER_C", "TIER_ACTIVE"
        Raises ValueError for unknown tier.
    top_n : int
        Maximum number of candidates to include in ranking output (1+).
    dry_run : bool
        Must always be True (enforced). False raises ValueError.

    Returns
    -------
    dict — PlanningBundle with full planning output.

    Raises
    ------
    ValueError
        If tier is unknown or dry_run is False.
    """
    # --- Input validation ---
    if not dry_run:
        raise ValueError("dry_run must be True — runtime is simulation-only")
    if tier not in _TIER_MAP:
        raise ValueError(
            f"Unknown tier: {tier!r}. Valid tiers: {sorted(_TIER_MAP.keys())}"
        )
    if top_n < 1:
        top_n = 1

    tier_constant = _TIER_MAP[tier]

    # --- Step 1: Get candidates from backlog ---
    candidates = get_candidates_by_tier(tier_constant)

    # --- Step 2: Build scoring specs ---
    scoring_specs = [_backlog_entry_to_scorer_spec(entry) for entry in candidates]

    # --- Step 3: Score and rank ---
    if not scoring_specs:
        return {
            "bundle_id": _stable_hash({"tier": tier, "top_n": top_n}),
            "tier": tier,
            "top_n": top_n,
            "dry_run_only": True,
            "simulation_only": True,
            "candidate_ranking": [],
            "selected_first_candidate": None,
            "first_candidate_readiness_score": None,
            "first_candidate_rationale": f"No candidates found for tier {tier}",
            "first_candidate_blockers": [],
            "first_candidate_required_evidence": [],
            "first_candidate_proposed_acquisition_lanes": [],
            "first_candidate_risks": [],
            "first_candidate_non_goals": [],
            "lifecycle_simulation": {},
            "simulation_graph_summary": {},
            "multi_format_plan": plan_all_groups(),
            "governance": _governance_copy(),
            "next_recommended_sprint": "R12_FIRST_CANDIDATE_EVIDENCE_PACK",
        }

    scoring_result = score_multiple_formats(scoring_specs)
    ranked_all = scoring_result.get("ranked", [])
    top_candidates = ranked_all[:top_n]

    # --- Step 4: Select first candidate ---
    first_candidate = scoring_result.get("top_candidate") or (
        top_candidates[0]["format_id"] if top_candidates else None
    )

    if first_candidate is None:
        first_candidate_score_data: dict = {}
        lifecycle_sim: dict = {}
        sim_v2_summary: dict = {}
        rationale = "No candidates available."
        blockers: list[str] = []
        required_evidence: list[str] = []
        proposed_lanes: list[str] = []
        risks: list[str] = []
        non_goals = _build_non_goals("unknown")
        readiness_score = None
    else:
        first_candidate_score_data = scoring_result["scores"].get(first_candidate, {})
        readiness_score = first_candidate_score_data.get("composite_score")

        # --- Step 5: Lifecycle simulation ---
        profile = KNOWN_FORMAT_PROFILES.get(first_candidate, {})
        lifecycle_sim = simulate_format_acquisition(first_candidate, profile)
        blockers = lifecycle_sim.get("active_blockers", [])
        required_evidence = lifecycle_sim.get("evidence_requirements", [])

        # --- Step 6: Simulation v2 graphs ---
        sim_v2_output = simulate_v2(first_candidate)
        sim_v2_summary = _build_graph_summary(sim_v2_output)

        # --- Step 7: Build plan components ---
        rationale = _build_rationale(first_candidate, first_candidate_score_data, ranked_all)
        proposed_lanes = _build_proposed_acquisition_lanes(first_candidate, lifecycle_sim)
        risks = _build_risks(first_candidate, first_candidate_score_data)
        non_goals = _build_non_goals(first_candidate)

    # --- Step 8: Multi-format plan ---
    multi_plan = plan_all_groups()

    # --- Step 9: Build bundle ---
    bundle_id = _stable_hash({
        "tier": tier,
        "top_n": top_n,
        "first_candidate": first_candidate,
        "ranked": [(c["format_id"], c["score"]) for c in top_candidates],
    })

    return {
        "bundle_id": bundle_id,
        "tier": tier,
        "top_n": top_n,
        "dry_run_only": True,
        "simulation_only": True,
        "candidate_ranking": top_candidates,
        "selected_first_candidate": first_candidate,
        "first_candidate_readiness_score": readiness_score,
        "first_candidate_rationale": rationale,
        "first_candidate_blockers": blockers,
        "first_candidate_required_evidence": required_evidence,
        "first_candidate_proposed_acquisition_lanes": proposed_lanes,
        "first_candidate_risks": risks,
        "first_candidate_non_goals": non_goals,
        "lifecycle_simulation": lifecycle_sim,
        "simulation_graph_summary": sim_v2_summary,
        "multi_format_plan": multi_plan,
        "governance": _governance_copy(),
        "next_recommended_sprint": "R12_FIRST_CANDIDATE_EVIDENCE_PACK",
        "bundle_note": (
            "SIMULATION ONLY — planning estimates, not commitments. "
            "No acquisition executed. Gate 11 NOT APPROVED. "
            "commercial_product_ready: false."
        ),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Acquisition planning runtime")
    parser.add_argument("--tier", default="TIER_A", help="Candidate tier")
    parser.add_argument("--top-n", type=int, default=5, help="Top N candidates")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    result = run_acquisition_planning(tier=args.tier, top_n=args.top_n)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("=== Acquisition Planning Runtime ===")
    print(f"  Tier:             {result['tier']}")
    print(f"  Top N:            {result['top_n']}")
    print(f"  dry_run_only:     {result['dry_run_only']}")
    print(f"  simulation_only:  {result['simulation_only']}")
    print("")
    print(f"  Candidate Ranking (top {result['top_n']}):")
    for r in result["candidate_ranking"]:
        print(f"    {r['format_id']:12s}  score={r['score']:.2f}  tier={r['tier']}")
    print("")
    print(f"  Selected first candidate: {result['selected_first_candidate']}")
    print(f"  Readiness score:          {result['first_candidate_readiness_score']}")
    print("")
    if result["first_candidate_blockers"]:
        print("  Blockers:")
        for b in result["first_candidate_blockers"]:
            print(f"    {b}")
    print("")
    print("  Proposed acquisition lanes:")
    for lane in result["first_candidate_proposed_acquisition_lanes"]:
        print(f"    {lane}")
    print("")
    print(f"  Next recommended sprint: {result['next_recommended_sprint']}")
    print(f"  {result['bundle_note']}")


if __name__ == "__main__":
    main()
