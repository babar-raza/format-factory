"""
acquisition_lifecycle_simulator.py -- Lane B Deliverable (FORMAT-FACTORY-R10)

Acquisition Lifecycle Simulator for the format-factory governed planning layer.

PURPOSE:
  Simulate the complete format acquisition lifecycle for any format — both current
  active formats (FODS, FODT) and future candidates (public-spec, non-Aspose).
  All outputs are deterministic descriptions of what WOULD happen.
  No source mutation, no gate approval, no implementation execution.

LIFECYCLE STATES:
  CANDIDATE               -- Format is a backlog candidate; audit not yet started
  SUPPORT_MATRIX_AUDIT    -- Verifying current Aspose support coverage
  SPEC_DISCOVERY          -- Finding public spec or documentation sources
  SPEC_NORMALIZATION      -- Caching and normalizing spec locally
  REQUIREMENTS_GENERATION -- AI-assisted requirements synthesis from spec
  VERIFIER_REVIEW         -- LANE_R5 verifier review of generated requirements
  DEC034_IV               -- Independent verification sprint (separate session)
  PLANNING_READY          -- Requirements authoritative; planning can begin
  IMPLEMENTATION_SIMULATION -- R9-style governed sprint simulation
  EVIDENCE_READY          -- Evidence bundle built and validated
  BLOCKED                 -- Blocked by stale, missing spec, or governance issue
  DEFERRED                -- Intentionally deferred with documented reason

STATE TRANSITIONS:
  CANDIDATE → SUPPORT_MATRIX_AUDIT → SPEC_DISCOVERY → SPEC_NORMALIZATION
    → REQUIREMENTS_GENERATION → VERIFIER_REVIEW → DEC034_IV → PLANNING_READY
    → IMPLEMENTATION_SIMULATION → EVIDENCE_READY

  Any state can transition to BLOCKED or DEFERRED.

NOT ALLOWED:
  - Real source mutation
  - Gate approval
  - Fetching specs from the internet
  - Claiming unsupported_by_aspose=true without audit
  - Moving a format from NEEDS_AUDIT to READY without audit

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

# Lifecycle state constants
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

# State ordering for progression tracking
STATE_ORDER = {
    STATE_CANDIDATE: 0,
    STATE_SUPPORT_MATRIX_AUDIT: 1,
    STATE_SPEC_DISCOVERY: 2,
    STATE_SPEC_NORMALIZATION: 3,
    STATE_REQUIREMENTS_GENERATION: 4,
    STATE_VERIFIER_REVIEW: 5,
    STATE_DEC034_IV: 6,
    STATE_PLANNING_READY: 7,
    STATE_IMPLEMENTATION_SIMULATION: 8,
    STATE_EVIDENCE_READY: 9,
    STATE_BLOCKED: -1,
    STATE_DEFERRED: -2,
}

# Required gates per lifecycle state
STATE_REQUIRED_GATES = {
    STATE_CANDIDATE: ["support_matrix_audit_not_started"],
    STATE_SUPPORT_MATRIX_AUDIT: ["gate_1_format_identified", "gate_2_spec_known"],
    STATE_SPEC_DISCOVERY: ["gate_3_spec_sourced"],
    STATE_SPEC_NORMALIZATION: ["gate_4_spec_normalized"],
    STATE_REQUIREMENTS_GENERATION: ["gate_5_requirements_generated", "gate_6_schema_validation"],
    STATE_VERIFIER_REVIEW: ["gate_7_verifier_review_pass"],
    STATE_DEC034_IV: ["gate_8_dec034_iv_pass"],
    STATE_PLANNING_READY: ["gate_9_planning_slices_ready"],
    STATE_IMPLEMENTATION_SIMULATION: ["gate_10_simulation_pass"],
    STATE_EVIDENCE_READY: ["gate_11_evidence_bundle_valid"],
}

# Blockers per state
STATE_BLOCKERS = {
    STATE_CANDIDATE: [],
    STATE_SUPPORT_MATRIX_AUDIT: ["aspose_support_unknown"],
    STATE_SPEC_DISCOVERY: ["no_public_spec", "legal_clearance_required"],
    STATE_SPEC_NORMALIZATION: ["spec_format_unknown", "spec_too_large"],
    STATE_REQUIREMENTS_GENERATION: ["spec_not_normalized", "ai_synthesis_failed"],
    STATE_VERIFIER_REVIEW: ["verifier_review_fail", "requirements_schema_invalid"],
    STATE_DEC034_IV: ["prior_iv_pass_required", "separate_session_required"],
    STATE_PLANNING_READY: ["stale_blocked", "requirements_not_authoritative"],
    STATE_IMPLEMENTATION_SIMULATION: ["simulation_blocked", "dependency_missing"],
    STATE_EVIDENCE_READY: ["bundle_validation_fail", "test_suite_fail"],
}

# Governance flags — immutable
_GOVERNANCE_FLAGS = {
    "commercial_product_ready": False,
    "autonomous_execution_allowed": False,
    "gate_self_approval_allowed": False,
    "dry_run_only": True,
    "simulation_only": True,
    "implementation_requires_human_authorization": True,
    "unsupported_by_aspose_requires_audit": True,
}


def _stable_hash(data: Any) -> str:
    """Deterministic SHA-256 of any JSON-serializable object."""
    normalized = json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def simulate_lifecycle_state(
    fmt: str,
    current_state: str,
    spec_available: bool = False,
    spec_type: str = "unknown",
    support_matrix_audited: bool = False,
    aspose_supported: bool | None = None,
    requirements_state: str = "REQUIREMENTS_MISSING",
    stale_verdict: str = "FRESH",
    gates_passed: int = 0,
    blockers: list[str] | None = None,
    deferred_reason: str | None = None,
) -> dict:
    """
    Simulate the lifecycle state of a format.

    Parameters
    ----------
    fmt : str
        Format ID (e.g. 'fods', 'hwpx', 'alz')
    current_state : str
        Current lifecycle state constant
    spec_available : bool
        Whether a public specification is available
    spec_type : str
        Type of spec: 'full_public', 'partial_public', 'reverse_engineering', 'none', 'unknown'
    support_matrix_audited : bool
        Whether Aspose support matrix has been audited for this format
    aspose_supported : bool | None
        Whether Aspose supports this format (None = not audited)
    requirements_state : str
        Current requirements authority state
    stale_verdict : str
        Current stale verdict (FRESH / REVIEW_REQUIRED / STALE_BLOCKED)
    gates_passed : int
        Number of acquisition gates passed (0-11)
    blockers : list[str], optional
        Active blockers for this format
    deferred_reason : str, optional
        Reason for deferral (if DEFERRED state)

    Returns
    -------
    dict — lifecycle state simulation
    """
    if blockers is None:
        blockers = []

    state_order_val = STATE_ORDER.get(current_state, -99)
    is_terminal = current_state in (STATE_BLOCKED, STATE_DEFERRED, STATE_EVIDENCE_READY)

    # Determine next state
    if current_state in (STATE_BLOCKED, STATE_DEFERRED):
        next_state = None
    elif current_state == STATE_EVIDENCE_READY:
        next_state = None
    else:
        current_idx = STATE_ORDER.get(current_state, 0)
        next_states = [s for s, idx in STATE_ORDER.items() if idx == current_idx + 1]
        next_state = next_states[0] if next_states else None

    # Compute active blockers
    active_blockers = list(blockers)
    if not support_matrix_audited and current_state not in (STATE_CANDIDATE,):
        active_blockers.append("support_matrix_audit_required")
    if stale_verdict == "STALE_BLOCKED":
        active_blockers.append("stale_blocked")
    if requirements_state != "REQUIREMENTS_AUTHORITATIVE" and state_order_val >= STATE_ORDER[STATE_PLANNING_READY]:
        active_blockers.append("requirements_not_authoritative")

    # Required next actions
    next_actions = _get_next_actions(fmt, current_state, support_matrix_audited, spec_available,
                                     requirements_state, stale_verdict)

    # Evidence requirements
    evidence_requirements = _get_evidence_requirements(fmt, current_state)

    simulation_id = _stable_hash({
        "fmt": fmt,
        "state": current_state,
        "spec_available": spec_available,
        "requirements_state": requirements_state,
        "stale_verdict": stale_verdict,
        "gates_passed": gates_passed,
    })

    return {
        "format_id": fmt,
        "current_state": current_state,
        "state_order": state_order_val,
        "next_state": next_state,
        "is_terminal": is_terminal,
        "is_blocked": bool(active_blockers) or current_state == STATE_BLOCKED,
        "spec_available": spec_available,
        "spec_type": spec_type,
        "support_matrix_audited": support_matrix_audited,
        "aspose_supported": aspose_supported,
        "requirements_state": requirements_state,
        "stale_verdict": stale_verdict,
        "gates_passed": gates_passed,
        "active_blockers": active_blockers,
        "deferred_reason": deferred_reason,
        "next_actions": next_actions,
        "evidence_requirements": evidence_requirements,
        "required_gates": STATE_REQUIRED_GATES.get(current_state, []),
        "simulation_id": simulation_id,
        "simulation_note": (
            f"Format {fmt.upper()} is at state {current_state}. "
            f"This is a simulation describing what WOULD happen next. "
            f"No implementation has been executed."
        ),
        "governance": dict(_GOVERNANCE_FLAGS),
        "dry_run_only": True,
        "autonomous_execution_allowed": False,
        "simulated_date": str(date.today()),
    }


def _get_next_actions(
    fmt: str,
    state: str,
    support_matrix_audited: bool,
    spec_available: bool,
    requirements_state: str,
    stale_verdict: str,
) -> list[str]:
    """Return ordered list of next actions for a format in a given state."""
    actions = []
    if state == STATE_CANDIDATE:
        actions.append(f"[SIM] Run support-matrix audit for {fmt.upper()} against current Aspose libraries")
        actions.append(f"[SIM] Document support gaps and overlaps in support-matrix audit report")
    elif state == STATE_SUPPORT_MATRIX_AUDIT:
        actions.append(f"[SIM] Locate public specification or documentation for {fmt.upper()}")
        actions.append(f"[SIM] Classify spec as: full_public / partial_public / reverse_engineering / none")
    elif state == STATE_SPEC_DISCOVERY:
        actions.append(f"[SIM] Download and cache {fmt.upper()} spec locally (AGENTS.md Section T)")
        actions.append(f"[SIM] Normalize spec into format-factory local spec cache")
    elif state == STATE_SPEC_NORMALIZATION:
        actions.append(f"[SIM] Generate requirements from normalized spec (AI-assisted)")
        actions.append(f"[SIM] Validate generated requirements against schema")
    elif state == STATE_REQUIREMENTS_GENERATION:
        actions.append(f"[SIM] Submit generated requirements for LANE_R5 verifier review")
    elif state == STATE_VERIFIER_REVIEW:
        actions.append(f"[SIM] Run DEC-034 independent verification sprint (separate session)")
    elif state == STATE_DEC034_IV:
        actions.append(f"[SIM] Confirm REQUIREMENTS_AUTHORITATIVE state in format_context_resolver")
        actions.append(f"[SIM] Build implementation plan via implementation_plan_expander")
    elif state == STATE_PLANNING_READY:
        actions.append(f"[SIM] Run execution_simulator.simulate_format_sprint('{fmt}')")
        actions.append(f"[SIM] Record simulation results in authority continuity registry")
    elif state == STATE_IMPLEMENTATION_SIMULATION:
        actions.append(f"[SIM] Build evidence bundle with sprint-specific metadata directory")
        actions.append(f"[SIM] Run validate_evidence_bundle.py — expect BUNDLE_VALIDATION: PASS")
    elif state == STATE_BLOCKED:
        actions.append(f"[SIM] Human review required to clear blockers before proceeding")
    elif state == STATE_DEFERRED:
        actions.append(f"[SIM] No action until deferral is lifted by human authorization")
    return actions


def _get_evidence_requirements(fmt: str, state: str) -> list[str]:
    """Return evidence requirements for a format at a given lifecycle state."""
    base = [
        f"BUNDLE_VALIDATION: PASS",
        f"METADATA_IDENTITY: CONSISTENT (sprint_id matching)",
        f"No src/net/ or src/python/ mutations",
    ]
    if state in (STATE_REQUIREMENTS_GENERATION, STATE_VERIFIER_REVIEW, STATE_DEC034_IV):
        base.append(f"generated-requirements/{fmt}/*.yaml — schema-validated")
        base.append(f"generated-requirements/{fmt}/verifier-review.yaml — LANE_R5_PASS")
    if state in (STATE_PLANNING_READY, STATE_IMPLEMENTATION_SIMULATION):
        base.append(f"Replay fingerprint — deterministic")
        base.append(f"Authority entry — format_isolation_marker: FORMAT:{fmt.upper()}")
    return base


def simulate_format_acquisition(fmt: str, profile: dict | None = None) -> dict:
    """
    Simulate the complete acquisition lifecycle for a format using a profile.

    Parameters
    ----------
    fmt : str
        Format ID
    profile : dict, optional
        Lifecycle profile with state, spec info, etc. If None, uses default CANDIDATE profile.

    Returns
    -------
    dict — full lifecycle simulation
    """
    if profile is None:
        profile = {}

    state = profile.get("state", STATE_CANDIDATE)
    return simulate_lifecycle_state(
        fmt=fmt,
        current_state=state,
        spec_available=profile.get("spec_available", False),
        spec_type=profile.get("spec_type", "unknown"),
        support_matrix_audited=profile.get("support_matrix_audited", False),
        aspose_supported=profile.get("aspose_supported", None),
        requirements_state=profile.get("requirements_state", "REQUIREMENTS_MISSING"),
        stale_verdict=profile.get("stale_verdict", "FRESH"),
        gates_passed=profile.get("gates_passed", 0),
        blockers=profile.get("blockers", []),
        deferred_reason=profile.get("deferred_reason", None),
    )


def simulate_multi_format_acquisition(format_profiles: dict[str, dict]) -> dict:
    """
    Simulate acquisition lifecycle for multiple formats simultaneously.

    Parameters
    ----------
    format_profiles : dict[str, dict]
        Map of format_id → lifecycle profile

    Returns
    -------
    dict — aggregate simulation results
    """
    per_format = {
        fmt: simulate_format_acquisition(fmt, profile)
        for fmt, profile in format_profiles.items()
    }

    all_planning_ready = all(
        STATE_ORDER.get(r["current_state"], -1) >= STATE_ORDER[STATE_PLANNING_READY]
        for r in per_format.values()
    )
    any_blocked = any(r["is_blocked"] for r in per_format.values())
    any_deferred = any(r["current_state"] == STATE_DEFERRED for r in per_format.values())

    state_distribution: dict[str, int] = {}
    for r in per_format.values():
        s = r["current_state"]
        state_distribution[s] = state_distribution.get(s, 0) + 1

    return {
        "formats_simulated": sorted(format_profiles.keys()),
        "per_format": per_format,
        "all_planning_ready": all_planning_ready,
        "any_blocked": any_blocked,
        "any_deferred": any_deferred,
        "state_distribution": state_distribution,
        "governance": dict(_GOVERNANCE_FLAGS),
        "dry_run_only": True,
        "autonomous_execution_allowed": False,
        "simulated_date": str(date.today()),
    }


# Built-in format profiles for known formats
KNOWN_FORMAT_PROFILES = {
    "fods": {
        "state": STATE_EVIDENCE_READY,
        "spec_available": True,
        "spec_type": "full_public",
        "support_matrix_audited": True,
        "aspose_supported": True,
        "requirements_state": "REQUIREMENTS_AUTHORITATIVE",
        "stale_verdict": "FRESH",
        "gates_passed": 10,
    },
    "fodt": {
        "state": STATE_EVIDENCE_READY,
        "spec_available": True,
        "spec_type": "full_public",
        "support_matrix_audited": True,
        "aspose_supported": True,
        "requirements_state": "REQUIREMENTS_AUTHORITATIVE",
        "stale_verdict": "FRESH",
        "gates_passed": 10,
    },
    "hwpx": {
        "state": STATE_CANDIDATE,
        "spec_available": True,
        "spec_type": "partial_public",
        "support_matrix_audited": False,
        "aspose_supported": None,
        "requirements_state": "REQUIREMENTS_MISSING",
        "gates_passed": 0,
    },
    "hwp": {
        "state": STATE_CANDIDATE,
        "spec_available": False,
        "spec_type": "reverse_engineering",
        "support_matrix_audited": False,
        "aspose_supported": None,
        "requirements_state": "REQUIREMENTS_MISSING",
        "gates_passed": 0,
    },
    "alz": {
        "state": STATE_CANDIDATE,
        "spec_available": False,
        "spec_type": "reverse_engineering",
        "support_matrix_audited": False,
        "aspose_supported": None,
        "requirements_state": "REQUIREMENTS_MISSING",
        "gates_passed": 0,
    },
    "egg": {
        "state": STATE_CANDIDATE,
        "spec_available": True,
        "spec_type": "partial_public",
        "support_matrix_audited": False,
        "aspose_supported": None,
        "requirements_state": "REQUIREMENTS_MISSING",
        "gates_passed": 0,
    },
    "hwt": {
        "state": STATE_CANDIDATE,
        "spec_available": True,
        "spec_type": "partial_public",
        "support_matrix_audited": False,
        "aspose_supported": None,
        "requirements_state": "REQUIREMENTS_MISSING",
        "gates_passed": 0,
    },
}


def simulate_standard_formats() -> dict:
    """Simulate the acquisition lifecycle for all known standard formats."""
    return simulate_multi_format_acquisition(KNOWN_FORMAT_PROFILES)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Acquisition lifecycle simulator")
    parser.add_argument("format", nargs="?", default="all")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.format == "all":
        result = simulate_standard_formats()
        if args.json:
            print(json.dumps(result, indent=2))
            return
        print(f"=== Acquisition Lifecycle Simulation: ALL FORMATS ===")
        print(f"  Formats: {result['formats_simulated']}")
        print(f"  Any blocked: {result['any_blocked']}")
        print(f"  All planning ready: {result['all_planning_ready']}")
        print(f"  State distribution: {result['state_distribution']}")
        for fmt, r in result["per_format"].items():
            blocked_str = f" [BLOCKED: {r['active_blockers']}]" if r["active_blockers"] else ""
            print(f"  [{fmt.upper()}] {r['current_state']}{blocked_str}")
    else:
        profile = KNOWN_FORMAT_PROFILES.get(args.format, {})
        result = simulate_format_acquisition(args.format, profile)
        if args.json:
            print(json.dumps(result, indent=2))
            return
        print(f"=== Lifecycle Simulation: {args.format.upper()} ===")
        print(f"  State:    {result['current_state']}")
        print(f"  Next:     {result['next_state']}")
        print(f"  Blocked:  {result['is_blocked']}")
        if result["active_blockers"]:
            print(f"  Blockers: {result['active_blockers']}")
        print(f"  Next actions:")
        for a in result["next_actions"]:
            print(f"    {a}")


if __name__ == "__main__":
    main()
