"""
execution_simulator.py -- Lane R9-2 Deliverable (CONWAY-R9)

Governed Execution Simulator for the format-factory orchestration layer.

PURPOSE:
  Simulate what an implementation sprint WOULD do for a given format,
  without executing any code, writing any source files, or triggering
  any gate approval. All outputs are deterministic, dry-run descriptions.

SIMULATION OUTPUTS (per-format):
  - per-lane simulation summaries (descriptive, not executable)
  - constraint propagation results
  - stale-state enforcement decisions
  - authority continuity entries
  - gate-state snapshots (no approval)
  - simulation pass/fail verdicts

NOT ALLOWED (simulation safety boundary):
  - Subprocess execution
  - File writes to src/net/ or src/python/
  - Gate approval or gate-state mutation
  - Bypassing stale blocks
  - Claiming commercial_product_ready = True

SIMULATION STATUSES:
  SIMULATION_PASS           -- All lanes simulated successfully
  SIMULATION_FAIL           -- Simulation produced structured errors
  BLOCKED_STALE             -- Stale verdict prevents simulation
  BLOCKED_AUTHORITY         -- Requirements not authoritative
  BLOCKED_DEPENDENCY        -- Prerequisite lane not met
  BLOCKED_GOVERNANCE        -- Governance check failed
  REPLAY_MISMATCH           -- Fingerprint mismatch detected

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

# Module-level imports for patchability in tests.
# These names are used directly by simulate_format_sprint so that
# `patch("execution_simulator.resolve_format_context", ...)` works correctly.
try:
    from format_context_resolver import resolve_format_context
    from stale_detection import detect_stale_state
    from implementation_plan_expander import expand_implementation_plan
    from authority_continuity_registry import (
        build_authority_entry,
        add_simulation_entry,
        _stable_hash as _reg_hash,
    )
    _DEPS_AVAILABLE = True
except ImportError:
    resolve_format_context = None  # type: ignore[assignment]
    detect_stale_state = None  # type: ignore[assignment]
    expand_implementation_plan = None  # type: ignore[assignment]
    build_authority_entry = None  # type: ignore[assignment]
    add_simulation_entry = None  # type: ignore[assignment]
    _reg_hash = None  # type: ignore[assignment]
    _DEPS_AVAILABLE = False

# Governance flags — simulation never overrides these
_GOVERNANCE_FLAGS = {
    "commercial_product_ready": False,
    "autonomous_execution_allowed": False,
    "gate_self_approval_allowed": False,
    "dry_run_only": True,
    "simulation_only": True,
    "implementation_requires_human_authorization": True,
}

# Simulation lane IDs (mirrors CAPABILITY_LANE_MAP in implementation_plan_expander)
SIMULATION_LANES = [
    "LANE-I-LOAD",
    "LANE-I-OBJECT-MODEL",
    "LANE-I-EDIT",
    "LANE-I-SAVE",
    "LANE-I-TESTS",
]

# Lane dependency order for simulation
LANE_PREREQUISITES = {
    "LANE-I-LOAD": [],
    "LANE-I-OBJECT-MODEL": ["LANE-I-LOAD"],
    "LANE-I-EDIT": ["LANE-I-LOAD", "LANE-I-OBJECT-MODEL"],
    "LANE-I-SAVE": ["LANE-I-LOAD", "LANE-I-OBJECT-MODEL", "LANE-I-EDIT"],
    "LANE-I-TESTS": ["LANE-I-LOAD", "LANE-I-OBJECT-MODEL"],
}


def _stable_hash(data: Any) -> str:
    """Deterministic SHA-256 of any JSON-serializable object. Sorted keys."""
    normalized = json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def _build_lane_simulation(
    lane_id: str,
    fmt: str,
    requirement_ids: list[str],
    constraints: list[dict],
    completed_lanes: set[str],
) -> dict:
    """
    Simulate a single implementation lane.

    Returns a lane simulation dict describing what WOULD happen.
    No code is generated; no source files are written.
    """
    prereqs = LANE_PREREQUISITES.get(lane_id, [])
    unmet_prereqs = [p for p in prereqs if p not in completed_lanes]

    if unmet_prereqs:
        return {
            "lane_id": lane_id,
            "format_id": fmt,
            "simulation_status": "BLOCKED_DEPENDENCY",
            "requirement_ids": requirement_ids,
            "unmet_prerequisites": unmet_prereqs,
            "simulated_actions": [],
            "constraint_violations": [],
            "test_simulation": {"expected_test_count": 0, "test_coverage_met": False},
            "evidence_simulation": {"evidence_items": []},
            "simulation_note": (
                f"Lane {lane_id} cannot be simulated: prerequisites not met: {unmet_prereqs}. "
                f"This is a dependency enforcement check — not a blocking governance error."
            ),
            "dry_run_only": True,
            "autonomous_execution_allowed": False,
        }

    # Check constraint propagation
    constraint_violations = []
    for c in constraints:
        scope = c.get("scope", "global")
        if scope == "global" or scope in requirement_ids:
            constraint_text = c.get("constraint", "")
            # Mark as simulation-noted (not violated — just propagated)
            constraint_violations.append({
                "constraint": constraint_text,
                "scope": scope,
                "propagated_to_lane": lane_id,
                "simulation_action": "CONSTRAINT_NOTED",
            })

    # Simulated actions: descriptive only
    simulated_actions = [
        f"[SIM] Would implement {len(requirement_ids)} requirements in {lane_id} for format {fmt.upper()}",
        f"[SIM] Would write implementation code in src/net/{fmt}/ or src/python/{fmt}/",
        f"[SIM] Would NOT execute any code — implementation requires human authorization",
        f"[SIM] Would produce tests covering all {len(requirement_ids)} requirement IDs",
        f"[SIM] Would generate evidence bundle after test suite passes",
    ]

    # Test simulation
    test_simulation = {
        "expected_test_count": max(1, len(requirement_ids)),
        "test_coverage_met": False,  # Not met until actual implementation
        "test_note": (
            f"Simulation estimates ≥{max(1, len(requirement_ids))} tests needed. "
            f"Actual coverage determined by human implementation sprint."
        ),
    }

    # Evidence simulation
    evidence_items = [
        f"test-run-output-{fmt}-{lane_id.lower().replace('lane-', '')}.txt",
        f"no-src-mutation-proof-{fmt}.txt",
        f"gate-state-snapshot-{fmt}.yaml",
    ]

    return {
        "lane_id": lane_id,
        "format_id": fmt,
        "simulation_status": "SIMULATION_PASS",
        "requirement_ids": requirement_ids,
        "unmet_prerequisites": [],
        "simulated_actions": simulated_actions,
        "constraint_violations": constraint_violations,
        "test_simulation": test_simulation,
        "evidence_simulation": {"evidence_items": evidence_items},
        "simulation_note": (
            f"Simulation of {lane_id} for {fmt.upper()} complete. "
            f"This describes what a human-authorized implementation sprint WOULD do. "
            f"No source code was generated or executed."
        ),
        "dry_run_only": True,
        "autonomous_execution_allowed": False,
    }


def simulate_format_sprint(fmt: str) -> dict:
    """
    Simulate a full implementation sprint for a format.

    Parameters
    ----------
    fmt : str
        Format ID (e.g. 'fods', 'fodt')

    Returns
    -------
    dict with:
      format_id: str
      simulation_status: str
      lane_simulations: list[dict]
      authority_entry: dict
      gate_state_snapshot: dict
      constraint_propagation: list[dict]
      stale_verdict: str
      requirements_state: str
      simulation_id: str
      simulation_summary: str
      governance: dict
      dry_run_only: bool
      autonomous_execution_allowed: bool
    """
    if not _DEPS_AVAILABLE or resolve_format_context is None:
        return {
            "format_id": fmt,
            "simulation_status": "BLOCKED_GOVERNANCE",
            "lane_simulations": [],
            "authority_entry": None,
            "gate_state_snapshot": {},
            "constraint_propagation": [],
            "stale_verdict": "UNKNOWN",
            "requirements_state": "UNKNOWN",
            "simulation_id": "ERROR",
            "simulation_summary": "Dependencies not available (import error at module load)",
            "governance": dict(_GOVERNANCE_FLAGS),
            "dry_run_only": True,
            "autonomous_execution_allowed": False,
        }

    # Load context
    ctx = resolve_format_context(fmt)
    stale = detect_stale_state(fmt)
    plan = expand_implementation_plan(fmt)

    req_state = ctx["requirements_state"]["status"]
    stale_verdict = stale["verdict"]

    # Governance checks
    if req_state != "REQUIREMENTS_AUTHORITATIVE":
        return _blocked_result(
            fmt, "BLOCKED_AUTHORITY",
            f"Requirements not authoritative (state={req_state}). Simulation cannot proceed.",
            req_state, stale_verdict,
        )

    if stale_verdict == "STALE_BLOCKED":
        return _blocked_result(
            fmt, "BLOCKED_STALE",
            f"Stale state blocks simulation (verdict=STALE_BLOCKED). Human review required.",
            req_state, stale_verdict,
        )

    if plan["expansion_status"] not in ("EXPANDED",):
        return _blocked_result(
            fmt, "BLOCKED_AUTHORITY",
            f"Implementation plan not expanded (status={plan['expansion_status']}). Cannot simulate.",
            req_state, stale_verdict,
        )

    # Collect lane recommendations from plan
    lane_rec = plan["lane_recommendations"]
    known_constraints = plan["known_constraints"]

    # Gate state snapshot (no approval — read-only)
    gate_state_snapshot = {
        "gates_passed": ctx.get("gates_passed", 0),
        "gate_11_status": ctx.get("gate_11_status", "unknown"),
        "gate_11_approved": False,  # NEVER set to True by simulation
        "simulation_read_only": True,
    }

    # Simulate each lane in dependency order
    lane_simulations = []
    completed_lanes: set[str] = set()
    all_pass = True

    for lane_id in SIMULATION_LANES:
        req_ids = lane_rec.get(lane_id, [])
        if not req_ids:
            continue  # skip lanes with no requirements for this format

        sim = _build_lane_simulation(
            lane_id=lane_id,
            fmt=fmt,
            requirement_ids=req_ids,
            constraints=known_constraints,
            completed_lanes=completed_lanes,
        )
        lane_simulations.append(sim)

        if sim["simulation_status"] == "SIMULATION_PASS":
            completed_lanes.add(lane_id)
        else:
            all_pass = False

    overall_status = "SIMULATION_PASS" if all_pass else "SIMULATION_FAIL"

    # Build simulation summary
    lane_count = len(lane_simulations)
    pass_count = sum(1 for s in lane_simulations if s["simulation_status"] == "SIMULATION_PASS")
    req_ids = ctx.get("accepted_requirement_ids", [])

    simulation_summary = (
        f"Format {fmt.upper()}: {pass_count}/{lane_count} lanes simulated. "
        f"{len(req_ids)} accepted requirements. "
        f"State={req_state}, Stale={stale_verdict}. "
        f"DRY-RUN ONLY — no implementation executed."
    )

    # Build authority entry with simulation appended
    slice_ids = [s["slice_id"] for s in plan["implementation_slices"]]
    simulation_id = _stable_hash({
        "fmt": fmt,
        "req_ids": sorted(req_ids),
        "date": str(date.today()),
        "lane_count": lane_count,
    })

    authority_entry = build_authority_entry(
        fmt=fmt,
        requirements_state=req_state,
        accepted_requirement_ids=req_ids,
        stale_verdict=stale_verdict,
        planning_slice_ids=slice_ids,
        gate_state=gate_state_snapshot,
        replay_fingerprint=None,
    )
    authority_entry = add_simulation_entry(
        authority_entry,
        simulation_id=simulation_id,
        simulation_status=overall_status,
        simulation_summary=simulation_summary,
    )

    # Collect all constraint propagation results
    constraint_propagation = []
    for sim in lane_simulations:
        constraint_propagation.extend(sim.get("constraint_violations", []))

    return {
        "format_id": fmt,
        "simulation_status": overall_status,
        "lane_simulations": lane_simulations,
        "authority_entry": authority_entry,
        "gate_state_snapshot": gate_state_snapshot,
        "constraint_propagation": constraint_propagation,
        "stale_verdict": stale_verdict,
        "requirements_state": req_state,
        "simulation_id": simulation_id,
        "simulation_summary": simulation_summary,
        "governance": dict(_GOVERNANCE_FLAGS),
        "dry_run_only": True,
        "autonomous_execution_allowed": False,
    }


def simulate_all_formats(formats: list[str] | None = None) -> dict:
    """
    Simulate implementation sprints for all governed formats.

    Parameters
    ----------
    formats : list[str], optional
        List of format IDs to simulate. Defaults to ['fods', 'fodt'].

    Returns
    -------
    dict with:
      formats_simulated: list[str]
      per_format_results: dict[str, dict]
      all_pass: bool
      any_blocked: bool
      total_lanes_simulated: int
      governance: dict
    """
    if formats is None:
        formats = ["fods", "fodt"]

    per_format: dict[str, dict] = {}
    for fmt in formats:
        per_format[fmt] = simulate_format_sprint(fmt)

    all_pass = all(
        r["simulation_status"] == "SIMULATION_PASS"
        for r in per_format.values()
    )
    any_blocked = any(
        r["simulation_status"].startswith("BLOCKED_")
        for r in per_format.values()
    )
    total_lanes = sum(
        len(r.get("lane_simulations", []))
        for r in per_format.values()
    )

    return {
        "formats_simulated": formats,
        "per_format_results": per_format,
        "all_pass": all_pass,
        "any_blocked": any_blocked,
        "total_lanes_simulated": total_lanes,
        "governance": dict(_GOVERNANCE_FLAGS),
        "dry_run_only": True,
        "autonomous_execution_allowed": False,
    }


def _blocked_result(
    fmt: str,
    status: str,
    summary: str,
    requirements_state: str,
    stale_verdict: str,
) -> dict:
    """Return a blocked simulation result."""
    return {
        "format_id": fmt,
        "simulation_status": status,
        "lane_simulations": [],
        "authority_entry": None,
        "gate_state_snapshot": {},
        "constraint_propagation": [],
        "stale_verdict": stale_verdict,
        "requirements_state": requirements_state,
        "simulation_id": "BLOCKED",
        "simulation_summary": summary,
        "governance": dict(_GOVERNANCE_FLAGS),
        "dry_run_only": True,
        "autonomous_execution_allowed": False,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Governed execution simulator")
    parser.add_argument("format", nargs="?", default="all", help="Format ID or 'all'")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.format == "all":
        result = simulate_all_formats()
        if args.json:
            print(json.dumps(result, indent=2))
            return
        print(f"=== Simulation Results: ALL FORMATS ===")
        print(f"  All pass:     {result['all_pass']}")
        print(f"  Any blocked:  {result['any_blocked']}")
        print(f"  Total lanes:  {result['total_lanes_simulated']}")
        for fmt, res in result["per_format_results"].items():
            print(f"\n  [{fmt.upper()}] {res['simulation_status']}")
            print(f"    {res['simulation_summary']}")
    else:
        result = simulate_format_sprint(args.format)
        if args.json:
            print(json.dumps(result, indent=2))
            return
        print(f"=== Simulation: {args.format.upper()} ===")
        print(f"  Status:       {result['simulation_status']}")
        print(f"  Summary:      {result['simulation_summary']}")
        for sim in result["lane_simulations"]:
            print(f"\n  [{sim['lane_id']}] {sim['simulation_status']}")
            if sim["simulated_actions"]:
                print(f"    Actions: {len(sim['simulated_actions'])}")


if __name__ == "__main__":
    main()
