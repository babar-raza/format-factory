"""
implementation_plan_expander.py -- Lane B Deliverable (CONWAY-R7R8)

Deterministic implementation-planning expansion engine.

PURPOSE:
  Convert authoritative generated requirements into structured implementation
  planning slices. Produces planning taskcards, dependency groups, lane
  recommendations, test expectations, and evidence expectations — all as
  dry-run planning artifacts only.

OUTPUTS:
  - implementation_slices: grouped requirement sets by capability level
  - planning_taskcards: per-slice taskcard descriptors
  - dependency_groups: implementation order with prerequisites
  - lane_recommendations: which LANE-I-* handles each slice
  - test_expectations: what test coverage each slice requires
  - evidence_expectations: what evidence each slice must produce

ALLOWED:
  - Reading generated requirements
  - Reading format context
  - Generating planning artifacts (dry-run only)
  - Expanding requirement IDs into taskcard descriptors

NOT ALLOWED:
  - Source code generation
  - Implementation execution
  - Gate approval
  - Mutation of source files (src/net/, src/python/)
  - Overriding authority chain

FODT CRITICAL PROPAGATION:
  FODT-REQ-040 (iterative traversal, no recursion) is annotated on all
  LANE-I-OBJECT-MODEL and LANE-I-LOAD slices for FODT format.

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REQS_DIR = REPO_ROOT / "generated-requirements"
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

# Capability level → implementation lane mapping
CAPABILITY_LANE_MAP = {
    "C0": "LANE-I-LOAD",
    "C1": "LANE-I-LOAD",
    "C2": "LANE-I-LOAD",
    "C3": "LANE-I-LOAD",
    "C4": "LANE-I-OBJECT-MODEL",
    "C5": "LANE-I-OBJECT-MODEL",
    "C6": "LANE-I-EDIT",
    "C7": "LANE-I-SAVE",
    "C8": "LANE-I-SAVE",
    "C9": "LANE-I-TESTS",
    "C10": "LANE-I-TESTS",
}

# Dependency order: each lane may only begin after its prerequisites are done
LANE_PREREQUISITES = {
    "LANE-I-LOAD": [],
    "LANE-I-OBJECT-MODEL": ["LANE-I-LOAD"],
    "LANE-I-EDIT": ["LANE-I-LOAD", "LANE-I-OBJECT-MODEL"],
    "LANE-I-SAVE": ["LANE-I-LOAD", "LANE-I-OBJECT-MODEL", "LANE-I-EDIT"],
    "LANE-I-TESTS": ["LANE-I-LOAD", "LANE-I-OBJECT-MODEL"],
}


def _load_yaml(path: Path) -> dict:
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _load_accepted_requirements(fmt: str) -> list[dict]:
    """Load all ACCEPTED_FOR_VERTICAL_SLICE requirements for a format."""
    req_files = [
        "commercial-requirements.yaml",
        "object-model-requirements.yaml",
        "save-edit-requirements.yaml",
        "conversion-requirements.yaml",
    ]
    accepted = []
    seen: set[str] = set()
    fmt_dir = REQS_DIR / fmt
    for fname in req_files:
        path = fmt_dir / fname
        if not path.exists():
            continue
        data = _load_yaml(path)
        for req in data.get("requirements", []):
            if req.get("status") != "ACCEPTED_FOR_VERTICAL_SLICE":
                continue
            rid = req.get("requirement_id", "")
            if not rid or rid in seen:
                continue
            seen.add(rid)
            accepted.append({
                "requirement_id": rid,
                "title": req.get("title", ""),
                "capability_level": req.get("capability_level", ""),
                "requirement_type": req.get("requirement_type", ""),
                "source_file": fname,
            })
    return accepted


def _load_known_constraints(fmt: str) -> list[dict]:
    """Load critical constraints from verifier-review and traceability-map."""
    constraints = []
    fmt_dir = REQS_DIR / fmt

    vr = _load_yaml(fmt_dir / "verifier-review.yaml")
    verdict = vr.get("verifier_verdict", {})
    auth = verdict.get("implementation_authorization", {})
    constraint = auth.get("critical_constraint")
    if constraint:
        constraints.append({"source": "verifier_review", "constraint": constraint, "scope": "global"})

    tm = _load_yaml(fmt_dir / "traceability-map.yaml")
    for entry in tm.get("critical_requirements", []):
        if isinstance(entry, dict):
            for req_id, desc in entry.items():
                constraints.append({"source": "traceability_map", "requirement_id": req_id, "constraint": desc, "scope": req_id})

    return constraints


def _group_by_lane(requirements: list[dict]) -> dict[str, list[dict]]:
    """Group requirements by their target implementation lane."""
    groups: dict[str, list[dict]] = {}
    for req in requirements:
        cap = req.get("capability_level", "")
        lane = CAPABILITY_LANE_MAP.get(cap, "LANE-I-TESTS")
        if lane not in groups:
            groups[lane] = []
        groups[lane].append(req)
    return groups


def _build_taskcard(
    lane_id: str,
    requirements: list[dict],
    fmt: str,
    constraints: list[dict],
    slice_index: int,
) -> dict:
    """Build a planning taskcard for a lane slice."""
    req_ids = [r["requirement_id"] for r in requirements]
    prerequisites = LANE_PREREQUISITES.get(lane_id, [])

    # Determine applicable constraints
    applicable_constraints = []
    for c in constraints:
        scope = c.get("scope", "global")
        if scope == "global":
            applicable_constraints.append(c)
        elif scope in req_ids:
            applicable_constraints.append(c)

    # Test expectations: each accepted requirement needs at least one test
    test_expectations = [
        f"At least one unit test covering {rid} behavior"
        for rid in req_ids
    ]
    test_expectations.append(f"All {len(req_ids)} requirements in this slice have passing tests")

    # Evidence expectations
    evidence_expectations = [
        f"Test run output: all {len(req_ids)} requirement tests PASS",
        f"No source mutation outside src/net/{fmt}/ or src/python/{fmt}/",
        f"No gate approval in this sprint",
    ]

    return {
        "taskcard_id": f"PLAN-{fmt.upper()}-{lane_id.replace('LANE-', '')}-{slice_index:03d}",
        "format": fmt,
        "lane_id": lane_id,
        "slice_index": slice_index,
        "requirement_ids": req_ids,
        "requirement_count": len(req_ids),
        "prerequisites": prerequisites,
        "applicable_constraints": applicable_constraints,
        "test_expectations": test_expectations,
        "evidence_expectations": evidence_expectations,
        "implementation_note": (
            f"Implement {len(req_ids)} accepted requirements in {lane_id}. "
            f"All must be covered by tests before evidence bundle is built. "
            f"DRY-RUN PLAN ONLY — no execution until human-authorized."
        ),
        "dry_run_only": True,
        "autonomous_execution_allowed": False,
    }


def _build_dependency_groups(lane_groups: dict[str, list[dict]]) -> list[dict]:
    """
    Build ordered dependency groups for implementation.
    Returns a list of dependency group dicts ordered by prerequisite depth.
    """
    # BFS ordering by prerequisite count
    ordered_lanes = []
    seen = set()

    def _depth(lane_id: str, visited: set[str] = None) -> int:
        if visited is None:
            visited = set()
        if lane_id in visited:
            return 0  # cycle guard
        visited.add(lane_id)
        prereqs = LANE_PREREQUISITES.get(lane_id, [])
        if not prereqs:
            return 0
        return 1 + max(_depth(p, visited.copy()) for p in prereqs)

    lane_ids = sorted(lane_groups.keys(), key=lambda lid: _depth(lid))
    for lane_id in lane_ids:
        if lane_id not in seen:
            seen.add(lane_id)
            ordered_lanes.append(lane_id)

    groups = []
    for i, lane_id in enumerate(ordered_lanes):
        reqs = lane_groups.get(lane_id, [])
        prereqs = LANE_PREREQUISITES.get(lane_id, [])
        active_prereqs = [p for p in prereqs if p in lane_groups]
        groups.append({
            "group_index": i + 1,
            "lane_id": lane_id,
            "requirement_count": len(reqs),
            "prerequisite_lanes": active_prereqs,
            "can_start_immediately": len(active_prereqs) == 0,
        })
    return groups


def expand_implementation_plan(fmt: str) -> dict:
    """
    Expand authoritative requirements into a structured implementation plan.

    Parameters
    ----------
    fmt : str
        Format ID (e.g. 'fods', 'fodt')

    Returns
    -------
    dict with:
      format_id: str
      expansion_status: str  -- EXPANDED | BLOCKED_NOT_AUTHORITATIVE | BLOCKED_STALE
      requirements_state: str
      stale_verdict: str
      implementation_slices: list[dict]
      planning_taskcards: list[dict]
      dependency_groups: list[dict]
      lane_recommendations: dict[str, list[str]]  -- lane_id → [requirement_ids]
      test_expectations: dict[str, list[str]]
      evidence_expectations: dict[str, list[str]]
      known_constraints: list[dict]
      accepted_count: int
      future_scoped_count: int
      governance: dict
    """
    from format_context_resolver import resolve_format_context

    fmt_ctx = resolve_format_context(fmt)
    req_state = fmt_ctx["requirements_state"]["status"]
    stale_info = fmt_ctx["requirements_state"].get("stale") or {}
    stale_verdict = stale_info.get("verdict", "FRESH") if isinstance(stale_info, dict) else "FRESH"

    governance = {
        "commercial_product_ready": False,
        "gate_self_approval_allowed": False,
        "autonomous_execution_allowed": False,
        "dry_run_only": True,
        "implementation_requires_human_authorization": True,
    }

    if req_state != "REQUIREMENTS_AUTHORITATIVE":
        return {
            "format_id": fmt,
            "expansion_status": "BLOCKED_NOT_AUTHORITATIVE",
            "requirements_state": req_state,
            "stale_verdict": stale_verdict,
            "implementation_slices": [],
            "planning_taskcards": [],
            "dependency_groups": [],
            "lane_recommendations": {},
            "test_expectations": {},
            "evidence_expectations": {},
            "known_constraints": [],
            "accepted_count": 0,
            "future_scoped_count": 0,
            "governance": governance,
        }

    if stale_verdict == "STALE_BLOCKED":
        return {
            "format_id": fmt,
            "expansion_status": "BLOCKED_STALE",
            "requirements_state": req_state,
            "stale_verdict": stale_verdict,
            "implementation_slices": [],
            "planning_taskcards": [],
            "dependency_groups": [],
            "lane_recommendations": {},
            "test_expectations": {},
            "evidence_expectations": {},
            "known_constraints": [],
            "accepted_count": 0,
            "future_scoped_count": 0,
            "governance": governance,
        }

    # Load requirements
    accepted = _load_accepted_requirements(fmt)
    constraints = _load_known_constraints(fmt)

    # Count future-scoped (not accepted)
    all_req_files = [
        "commercial-requirements.yaml", "object-model-requirements.yaml",
        "save-edit-requirements.yaml", "conversion-requirements.yaml",
    ]
    future_count = 0
    fmt_dir = REQS_DIR / fmt
    seen_future: set[str] = set()
    for fname in all_req_files:
        data = _load_yaml(fmt_dir / fname)
        for req in data.get("requirements", []):
            rid = req.get("requirement_id", "")
            if rid and rid not in seen_future and req.get("status") != "ACCEPTED_FOR_VERTICAL_SLICE":
                seen_future.add(rid)
                future_count += 1

    # Group by lane
    lane_groups = _group_by_lane(accepted)

    # Build taskcards
    taskcards = []
    lane_recommendations: dict[str, list[str]] = {}
    test_expectations: dict[str, list[str]] = {}
    evidence_expectations: dict[str, list[str]] = {}

    for lane_id, reqs in sorted(lane_groups.items()):
        card = _build_taskcard(lane_id, reqs, fmt, constraints, len(taskcards) + 1)
        taskcards.append(card)
        lane_recommendations[lane_id] = [r["requirement_id"] for r in reqs]
        test_expectations[lane_id] = card["test_expectations"]
        evidence_expectations[lane_id] = card["evidence_expectations"]

    # Build dependency groups
    dep_groups = _build_dependency_groups(lane_groups)

    # Build implementation slices (one per lane)
    slices = []
    for lane_id, reqs in sorted(lane_groups.items()):
        slices.append({
            "slice_id": f"{fmt.upper()}-{lane_id.replace('LANE-', '')}",
            "lane_id": lane_id,
            "requirements": [r["requirement_id"] for r in reqs],
            "capability_levels": sorted(set(r["capability_level"] for r in reqs)),
            "constraint_applies": any(
                c.get("scope") == "global" or c.get("scope") in [r["requirement_id"] for r in reqs]
                for c in constraints
            ),
        })

    return {
        "format_id": fmt,
        "expansion_status": "EXPANDED",
        "requirements_state": req_state,
        "stale_verdict": stale_verdict,
        "implementation_slices": slices,
        "planning_taskcards": taskcards,
        "dependency_groups": dep_groups,
        "lane_recommendations": lane_recommendations,
        "test_expectations": test_expectations,
        "evidence_expectations": evidence_expectations,
        "known_constraints": constraints,
        "accepted_count": len(accepted),
        "future_scoped_count": future_count,
        "governance": governance,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Implementation plan expander")
    parser.add_argument("format", nargs="?", default="all", help="Format ID or 'all'")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    formats = ["fods", "fodt"] if args.format == "all" else [args.format]
    for fmt in formats:
        result = expand_implementation_plan(fmt)
        if args.json:
            print(json.dumps(result, indent=2))
            continue
        print(f"\n=== Implementation Plan: {fmt.upper()} ===")
        print(f"  EXPANSION_STATUS: {result['expansion_status']}")
        print(f"  ACCEPTED: {result['accepted_count']}")
        print(f"  FUTURE_SCOPED: {result['future_scoped_count']}")
        print(f"  SLICES: {len(result['implementation_slices'])}")
        print(f"  TASKCARDS: {len(result['planning_taskcards'])}")
        for dg in result["dependency_groups"]:
            prereqs = dg["prerequisite_lanes"] or ["none"]
            print(f"    Group {dg['group_index']}: {dg['lane_id']} "
                  f"({dg['requirement_count']} reqs, prereqs: {prereqs})")


if __name__ == "__main__":
    main()
