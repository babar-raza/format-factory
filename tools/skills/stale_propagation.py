"""
stale_propagation.py -- Lane R9-5 Deliverable (CONWAY-R9)

Advanced stale-state propagation with severity tiers.

PURPOSE:
  Extend stale-state detection with multi-tier severity classification,
  propagation chain tracking, and actionable remediation guidance.
  This module DOES NOT modify stale_detection.py.

SEVERITY TIERS:
  TIER_0_CLEAN       -- No stale indicators; all checks pass
  TIER_1_ADVISORY    -- Minor warnings; planning can proceed with review
  TIER_2_REVIEW      -- Moderate staleness; human review recommended before advancing
  TIER_3_BLOCKED     -- Critical staleness; simulation and planning are BLOCKED
  TIER_4_CORRUPTED   -- Data integrity issue; requires immediate human intervention

PROPAGATION CHAIN:
  Staleness detected in one domain propagates to dependent domains:
  - Requirements stale → planning slices stale → simulation blocked
  - IV stale → gate state advisory → bundle suspect
  - Verifier stale → requirements advisory → planning advisory

NOT ALLOWED:
  - Modifying stale_detection.py
  - Bypassing STALE_BLOCKED gates
  - Approving gates to clear stale status
  - Marking requirements as fresh without human review

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

# Severity tier constants
TIER_0_CLEAN = "TIER_0_CLEAN"
TIER_1_ADVISORY = "TIER_1_ADVISORY"
TIER_2_REVIEW = "TIER_2_REVIEW"
TIER_3_BLOCKED = "TIER_3_BLOCKED"
TIER_4_CORRUPTED = "TIER_4_CORRUPTED"

# Tier ordering for comparison
TIER_ORDER = {
    TIER_0_CLEAN: 0,
    TIER_1_ADVISORY: 1,
    TIER_2_REVIEW: 2,
    TIER_3_BLOCKED: 3,
    TIER_4_CORRUPTED: 4,
}

# Stale verdict → base tier mapping
VERDICT_TO_BASE_TIER = {
    "FRESH": TIER_0_CLEAN,
    "REVIEW_REQUIRED": TIER_2_REVIEW,
    "STALE_BLOCKED": TIER_3_BLOCKED,
}

# Domain propagation rules: domain → list of downstream domains
PROPAGATION_RULES = {
    "requirements": ["planning_slices", "simulation", "replay_fingerprint"],
    "verifier_review": ["requirements", "planning_slices"],
    "iv_state": ["gate_state", "planning_bundle"],
    "planning_slices": ["simulation", "planning_bundle"],
    "gate_state": ["planning_bundle"],
    "replay_fingerprint": ["simulation"],
    "simulation": [],
    "planning_bundle": [],
}

# Remediation guidance per tier
REMEDIATION_GUIDANCE = {
    TIER_0_CLEAN: "No action required. All checks pass.",
    TIER_1_ADVISORY: (
        "Review stale warnings before advancing to next planning phase. "
        "Minor staleness may be acceptable with documented justification."
    ),
    TIER_2_REVIEW: (
        "Human review required before advancing. Re-run stale detection after "
        "reviewing all REVIEW_REQUIRED checks. Document review decision."
    ),
    TIER_3_BLOCKED: (
        "BLOCKED. Simulation and planning are blocked by critical stale state. "
        "Human must re-verify requirements, re-run IV, and clear STALE_BLOCKED "
        "verdict before any sprint proceeds."
    ),
    TIER_4_CORRUPTED: (
        "CRITICAL. Data integrity issue detected. Immediate human intervention required. "
        "Do not run any sprints. Re-validate all source files and evidence bundles."
    ),
}


def _max_tier(tiers: list[str]) -> str:
    """Return the highest severity tier from a list."""
    if not tiers:
        return TIER_0_CLEAN
    return max(tiers, key=lambda t: TIER_ORDER.get(t, 0))


def _propagate_tier(domain: str, tier: str, visited: set[str] | None = None) -> dict[str, str]:
    """
    Propagate a tier from a domain to all downstream domains.
    Returns a dict of {domain: propagated_tier}.
    """
    if visited is None:
        visited = set()
    if domain in visited:
        return {}
    visited.add(domain)

    result = {domain: tier}
    # Downstream domains receive at most one tier lower than source
    downstream_tier = tier if TIER_ORDER.get(tier, 0) > 0 else TIER_0_CLEAN
    # Advisory doesn't propagate beyond one level
    if TIER_ORDER.get(tier, 0) >= TIER_ORDER[TIER_2_REVIEW]:
        for downstream in PROPAGATION_RULES.get(domain, []):
            sub_result = _propagate_tier(downstream, downstream_tier, visited)
            result.update(sub_result)
    return result


def classify_stale_tier(
    verdict: str,
    blocker_count: int,
    warning_count: int,
    checks: dict[str, Any],
) -> str:
    """
    Classify a stale detection result into a severity tier.

    Parameters
    ----------
    verdict : str
        Stale verdict from stale_detection: FRESH | REVIEW_REQUIRED | STALE_BLOCKED
    blocker_count : int
        Number of blocking checks that failed
    warning_count : int
        Number of warning checks that triggered
    checks : dict
        Per-check results from stale_detection

    Returns
    -------
    str — severity tier (TIER_0_CLEAN through TIER_4_CORRUPTED)
    """
    base_tier = VERDICT_TO_BASE_TIER.get(verdict, TIER_2_REVIEW)

    # Escalate tier based on blocker count
    if blocker_count >= 3:
        return TIER_4_CORRUPTED
    if blocker_count >= 2:
        return TIER_3_BLOCKED

    # Check for data integrity issues
    # stale_detection may return string values ('PASS'/'FAIL') or dicts ({'status': ..., 'severity': ...})
    dir_check = checks.get("directory_exists", {})
    if isinstance(dir_check, str):
        dir_status, dir_severity = dir_check, "BLOCKER"
    elif isinstance(dir_check, dict):
        dir_status = dir_check.get("status", "")
        dir_severity = dir_check.get("severity", "")
    else:
        dir_status, dir_severity = "", ""
    if dir_status == "FAIL" and dir_severity == "BLOCKER":
        return TIER_4_CORRUPTED

    # Warning-only escalation
    if warning_count >= 3 and base_tier == TIER_0_CLEAN:
        return TIER_1_ADVISORY

    return base_tier


def build_propagation_report(
    fmt: str,
    verdict: str,
    blocker_count: int,
    warning_count: int,
    checks: dict[str, Any],
    reasons: list[str],
) -> dict:
    """
    Build a full stale propagation report for a format.

    Parameters
    ----------
    fmt : str
        Format ID (e.g. 'fods', 'fodt')
    verdict : str
        Stale verdict from stale_detection
    blocker_count : int
        Number of blocking checks
    warning_count : int
        Number of warning checks
    checks : dict
        Per-check results from stale_detection
    reasons : list[str]
        Reason strings from stale_detection

    Returns
    -------
    dict — full propagation report
    """
    tier = classify_stale_tier(verdict, blocker_count, warning_count, checks)

    # Determine source domains based on check failures
    source_domains: dict[str, str] = {}

    def _check_failed(check_name: str) -> bool:
        c = checks.get(check_name, {})
        if isinstance(c, str):
            return c in ("FAIL", "WARN")
        elif isinstance(c, dict):
            return c.get("status") in ("FAIL", "WARN")
        return False

    if _check_failed("accepted_count_consistent") or _check_failed("timestamp_consistency"):
        source_domains["requirements"] = tier

    if _check_failed("verifier_after_generation"):
        source_domains["verifier_review"] = tier

    if _check_failed("iv_after_verification"):
        source_domains["iv_state"] = tier

    if _check_failed("no_modification_after_iv"):
        source_domains["requirements"] = _max_tier([
            source_domains.get("requirements", TIER_0_CLEAN),
            TIER_1_ADVISORY,
        ])

    # If no specific source domain detected but verdict is not FRESH
    if not source_domains and verdict != "FRESH":
        source_domains["requirements"] = tier

    # Propagate from all source domains
    propagated: dict[str, str] = {}
    for domain, domain_tier in source_domains.items():
        propagated.update(_propagate_tier(domain, domain_tier))

    # Aggregate tier across all propagated domains
    all_tiers = list(propagated.values()) or [tier]
    aggregate_tier = _max_tier(all_tiers)

    # Build affected domains list
    affected_domains = sorted(
        [d for d, t in propagated.items() if t != TIER_0_CLEAN],
        key=lambda d: TIER_ORDER.get(propagated[d], 0),
        reverse=True,
    )

    remediation = REMEDIATION_GUIDANCE.get(aggregate_tier, "Unknown tier.")
    simulation_allowed = aggregate_tier not in (TIER_3_BLOCKED, TIER_4_CORRUPTED)

    return {
        "format_id": fmt,
        "verdict": verdict,
        "aggregate_tier": aggregate_tier,
        "source_domains": source_domains,
        "propagated_tiers": propagated,
        "affected_domains": affected_domains,
        "blocker_count": blocker_count,
        "warning_count": warning_count,
        "reasons": reasons,
        "remediation": remediation,
        "simulation_allowed": simulation_allowed,
        "planning_allowed": simulation_allowed,
        "governance": {
            "commercial_product_ready": False,
            "autonomous_execution_allowed": False,
            "gate_self_approval_allowed": False,
            "dry_run_only": True,
        },
    }


def propagate_stale_state(fmt: str) -> dict:
    """
    Run full stale-state propagation for a format.
    Reads from stale_detection and builds a propagation report.

    Parameters
    ----------
    fmt : str
        Format ID

    Returns
    -------
    dict — propagation report
    """
    try:
        from stale_detection import detect_stale_state
    except ImportError as exc:
        return {
            "format_id": fmt,
            "verdict": "UNKNOWN",
            "aggregate_tier": TIER_4_CORRUPTED,
            "error": str(exc),
            "simulation_allowed": False,
            "planning_allowed": False,
        }

    result = detect_stale_state(fmt)
    return build_propagation_report(
        fmt=fmt,
        verdict=result["verdict"],
        blocker_count=result.get("blocker_count", 0),
        warning_count=result.get("warning_count", 0),
        checks=result.get("checks", {}),
        reasons=result.get("reasons", []),
    )


def propagate_all_formats(formats: list[str] | None = None) -> dict:
    """
    Run stale propagation for all governed formats.

    Parameters
    ----------
    formats : list[str], optional
        Defaults to ['fods', 'fodt'].

    Returns
    -------
    dict — aggregate propagation results
    """
    if formats is None:
        formats = ["fods", "fodt"]

    per_format = {fmt: propagate_stale_state(fmt) for fmt in formats}
    all_clean = all(r["aggregate_tier"] == TIER_0_CLEAN for r in per_format.values())
    any_blocked = any(
        TIER_ORDER.get(r["aggregate_tier"], 0) >= TIER_ORDER[TIER_3_BLOCKED]
        for r in per_format.values()
    )
    max_tier = _max_tier([r["aggregate_tier"] for r in per_format.values()])

    return {
        "formats": formats,
        "per_format": per_format,
        "all_clean": all_clean,
        "any_blocked": any_blocked,
        "aggregate_tier": max_tier,
        "simulation_allowed": not any_blocked,
        "governance": {
            "commercial_product_ready": False,
            "autonomous_execution_allowed": False,
        },
    }


def main():
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Stale propagation report")
    parser.add_argument("format", nargs="?", default="all")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.format == "all":
        result = propagate_all_formats()
    else:
        result = propagate_stale_state(args.format)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    if args.format == "all":
        print(f"=== Stale Propagation: ALL FORMATS ===")
        print(f"  All clean:    {result['all_clean']}")
        print(f"  Any blocked:  {result['any_blocked']}")
        print(f"  Max tier:     {result['aggregate_tier']}")
        for fmt, r in result["per_format"].items():
            print(f"\n  [{fmt.upper()}] {r['aggregate_tier']} (verdict: {r['verdict']})")
            if r.get("affected_domains"):
                print(f"    Affected: {r['affected_domains']}")
    else:
        result = propagate_stale_state(args.format)
        print(f"=== Stale Propagation: {args.format.upper()} ===")
        print(f"  Verdict:        {result['verdict']}")
        print(f"  Aggregate tier: {result['aggregate_tier']}")
        print(f"  Simulation OK:  {result['simulation_allowed']}")
        print(f"  Remediation:    {result['remediation']}")


if __name__ == "__main__":
    main()
