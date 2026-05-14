"""
authority_continuity_registry.py -- Lane R9-1 Deliverable (CONWAY-R9)

Authority Continuity Registry for the governed planning/orchestration layer.

PURPOSE:
  Track authoritative planning lineage across:
  - generated requirements (accepted requirement IDs + hashes)
  - replay fingerprints
  - stale-state verdicts
  - planning slices
  - simulation runs
  - gate acceptance state
  - replay lineage
  - execution authorization state

REGISTRY PROPERTIES:
  - deterministic serialization (JSON, sorted keys)
  - cross-format isolation (each format has its own registry entry)
  - replay-safe updates (entries are immutable once finalized)
  - immutable simulation history (append-only simulation log)
  - no nondeterministic timestamps inside fingerprints

GOVERNANCE:
  - commercial_product_ready is always False
  - autonomous_execution_allowed is always False
  - gate_self_approval_allowed is always False
  - simulation history is append-only (never overwritten)

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

# Governance flags — these are immutable constants, never configurable
_GOVERNANCE_FLAGS = {
    "commercial_product_ready": False,
    "autonomous_execution_allowed": False,
    "gate_self_approval_allowed": False,
    "dry_run_only": True,
    "simulation_only": True,
    "implementation_requires_human_authorization": True,
}


def _stable_hash(data: Any) -> str:
    """Deterministic SHA-256 of any JSON-serializable object. Sorted keys."""
    normalized = json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def build_authority_entry(
    fmt: str,
    requirements_state: str,
    accepted_requirement_ids: list[str],
    stale_verdict: str,
    planning_slice_ids: list[str],
    gate_state: dict,
    replay_fingerprint: str | None = None,
    simulation_log: list[dict] | None = None,
) -> dict:
    """
    Build a deterministic authority continuity entry for a format.

    Parameters
    ----------
    fmt : str
        Format ID (e.g. 'fods', 'fodt')
    requirements_state : str
        From format_context_resolver: REQUIREMENTS_AUTHORITATIVE, etc.
    accepted_requirement_ids : list[str]
        Sorted list of ACCEPTED_FOR_VERTICAL_SLICE requirement IDs
    stale_verdict : str
        From stale_detection: FRESH | REVIEW_REQUIRED | STALE_BLOCKED
    planning_slice_ids : list[str]
        Sorted list of planning slice IDs from implementation_plan_expander
    gate_state : dict
        Keys: gates_passed (int), gate_11_status, gate_11_approved (bool)
    replay_fingerprint : str, optional
        From replay_fingerprint module
    simulation_log : list[dict], optional
        Append-only simulation history entries

    Returns
    -------
    dict — authority continuity entry (deterministic, serializable)
    """
    sorted_req_ids = sorted(accepted_requirement_ids)
    sorted_slice_ids = sorted(planning_slice_ids)

    req_hash = _stable_hash(sorted_req_ids)
    slice_hash = _stable_hash(sorted_slice_ids)
    gate_hash = _stable_hash({k: v for k, v in sorted(gate_state.items())})

    authority_id = _stable_hash({
        "format": fmt,
        "req_hash": req_hash,
        "slice_hash": slice_hash,
        "gate_hash": gate_hash,
        "requirements_state": requirements_state,
        "stale_verdict": stale_verdict,
    })

    entry = {
        "authority_id": authority_id,
        "format_id": fmt,
        "requirements_state": requirements_state,
        "accepted_requirement_count": len(sorted_req_ids),
        "accepted_requirement_ids": sorted_req_ids,
        "stale_verdict": stale_verdict,
        "planning_slice_count": len(sorted_slice_ids),
        "planning_slice_ids": sorted_slice_ids,
        "gate_state": gate_state,
        "source_hashes": {
            "requirements_hash": req_hash,
            "slice_hash": slice_hash,
            "gate_hash": gate_hash,
        },
        "replay_fingerprint": replay_fingerprint,
        "simulation_log": list(simulation_log) if simulation_log else [],
        "dependency_lineage": [],
        "format_isolation_marker": f"FORMAT:{fmt.upper()}",
        "governance": dict(_GOVERNANCE_FLAGS),
        "created_date": str(date.today()),
    }
    return entry


def build_full_registry(format_entries: list[dict]) -> dict:
    """
    Build a complete authority continuity registry from per-format entries.

    Parameters
    ----------
    format_entries : list[dict]
        List of dicts returned by build_authority_entry

    Returns
    -------
    dict — full registry (deterministic, cross-format isolated)
    """
    # Sort entries by format_id for determinism
    sorted_entries = sorted(format_entries, key=lambda e: e.get("format_id", ""))

    registry_hash = _stable_hash([e["authority_id"] for e in sorted_entries])

    return {
        "registry_id": registry_hash,
        "format_count": len(sorted_entries),
        "formats": {e["format_id"]: e for e in sorted_entries},
        "format_ids": [e["format_id"] for e in sorted_entries],
        "all_authoritative": all(
            e["requirements_state"] == "REQUIREMENTS_AUTHORITATIVE"
            for e in sorted_entries
        ),
        "any_stale_blocked": any(
            e["stale_verdict"] == "STALE_BLOCKED"
            for e in sorted_entries
        ),
        "governance": dict(_GOVERNANCE_FLAGS),
        "created_date": str(date.today()),
    }


def add_simulation_entry(
    entry: dict,
    simulation_id: str,
    simulation_status: str,
    simulation_summary: str,
) -> dict:
    """
    Append a simulation record to an authority entry's simulation log.
    Simulation log is append-only — prior entries are never modified.

    Parameters
    ----------
    entry : dict
        An authority entry from build_authority_entry
    simulation_id : str
        Unique ID for this simulation run
    simulation_status : str
        One of: SIMULATION_PASS, SIMULATION_FAIL, BLOCKED_STALE,
                BLOCKED_AUTHORITY, BLOCKED_DEPENDENCY, BLOCKED_GOVERNANCE,
                REPLAY_MISMATCH
    simulation_summary : str
        Human-readable summary

    Returns
    -------
    dict — updated entry (new dict, original is not mutated)
    """
    new_entry = dict(entry)
    new_log = list(entry.get("simulation_log", []))
    new_log.append({
        "simulation_id": simulation_id,
        "simulation_status": simulation_status,
        "summary": simulation_summary,
        "simulation_date": str(date.today()),
        "appended_at_index": len(new_log),
    })
    new_entry["simulation_log"] = new_log
    return new_entry


def build_live_registry() -> dict:
    """
    Build a live authority continuity registry from the current repo state.
    Reads format_context_resolver, stale_detection, implementation_plan_expander.
    """
    try:
        from format_context_resolver import resolve_format_context
        from stale_detection import detect_stale_state
        from implementation_plan_expander import expand_implementation_plan
    except ImportError as exc:
        return {
            "registry_id": "ERROR",
            "error": str(exc),
            "format_count": 0,
            "formats": {},
            "format_ids": [],
            "all_authoritative": False,
            "any_stale_blocked": False,
            "governance": dict(_GOVERNANCE_FLAGS),
        }

    entries = []
    for fmt in ["fods", "fodt"]:
        ctx = resolve_format_context(fmt)
        stale = detect_stale_state(fmt)
        plan = expand_implementation_plan(fmt)

        req_ids = ctx.get("accepted_requirement_ids", [])
        slice_ids = [
            s["slice_id"]
            for s in plan.get("implementation_slices", [])
        ]

        gate_state = {
            "gates_passed": ctx.get("gates_passed", 0),
            "gate_11_status": ctx.get("gate_11_status", "unknown"),
            "gate_11_approved": ctx.get("gate_11_approved", False),
        }

        fp = ctx.get("requirements_state", {}).get("replay_fingerprint")
        if not fp:
            fp = _stable_hash(sorted(req_ids))

        entry = build_authority_entry(
            fmt=fmt,
            requirements_state=ctx["requirements_state"]["status"],
            accepted_requirement_ids=req_ids,
            stale_verdict=stale["verdict"],
            planning_slice_ids=slice_ids,
            gate_state=gate_state,
            replay_fingerprint=fp,
        )
        entries.append(entry)

    return build_full_registry(entries)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Authority continuity registry")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    registry = build_live_registry()
    if args.json:
        print(json.dumps(registry, indent=2))
        return

    print(f"=== Authority Continuity Registry ===")
    print(f"  Registry ID:      {registry.get('registry_id', 'ERROR')}")
    print(f"  Formats:          {registry.get('format_ids', [])}")
    print(f"  All authoritative:{registry.get('all_authoritative')}")
    print(f"  Any stale blocked:{registry.get('any_stale_blocked')}")
    for fmt, entry in registry.get("formats", {}).items():
        print(f"\n  [{fmt.upper()}]")
        print(f"    authority_id:    {entry['authority_id']}")
        print(f"    req_state:       {entry['requirements_state']}")
        print(f"    stale_verdict:   {entry['stale_verdict']}")
        print(f"    accepted_count:  {entry['accepted_requirement_count']}")
        print(f"    slice_count:     {entry['planning_slice_count']}")


if __name__ == "__main__":
    main()
