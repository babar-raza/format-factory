"""
replay_fingerprint.py -- Lane E Deliverable (CONWAY-R7R8)

Deterministic replay fingerprinting for governed orchestration.

PURPOSE:
  Produce deterministic, stable fingerprints for:
  - Prompt content (hash of generated prompt text)
  - Lane selection (hash of selected/blocked lanes)
  - Requirement sets (hash of accepted requirement IDs)
  - Stale check state (hash of stale verdict + checks)
  - Planning expansion (hash of taskcard IDs)

  Fingerprints allow detecting when any component of the planning chain
  has changed between runs (replay inconsistency detection).

FINGERPRINT TYPES:
  content_hash  -- SHA-256 of sorted requirement IDs or prompt text
  structure_hash -- SHA-256 of structured planning metadata

REPLAY VERDICT:
  CONSISTENT    -- all fingerprints match expected values
  INCONSISTENT  -- one or more fingerprints have changed
  BASELINE      -- no prior baseline; current run establishes baseline

ALLOWED:
  - Reading planning outputs (dicts)
  - Computing deterministic hashes
  - Comparing against stored baselines

NOT ALLOWED:
  - Mutating planning data
  - Auto-regenerating requirements
  - Approving gates
  - Writing to source files

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


def _stable_hash(data: Any) -> str:
    """
    Compute a stable SHA-256 hash of any JSON-serializable object.
    Sorts dict keys for stability.
    """
    normalized = json.dumps(data, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def fingerprint_requirements(accepted_ids: list[str]) -> str:
    """
    Fingerprint a list of accepted requirement IDs.
    Sorted to ensure stability regardless of load order.
    """
    return _stable_hash(sorted(accepted_ids))


def fingerprint_lanes(selected_lanes: list[str], blocked_lanes: list[str]) -> str:
    """Fingerprint lane selection output."""
    return _stable_hash({
        "selected": sorted(selected_lanes),
        "blocked": sorted(blocked_lanes),
    })


def fingerprint_prompt(prompt_text: str) -> str:
    """Fingerprint prompt content. Normalizes whitespace."""
    # Normalize line endings and strip trailing whitespace per line
    lines = [line.rstrip() for line in prompt_text.splitlines()]
    normalized = "\n".join(lines).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def fingerprint_stale(stale_result: dict) -> str:
    """Fingerprint stale detection output."""
    slim = {
        "verdict": stale_result.get("verdict", "UNKNOWN"),
        "checks": stale_result.get("checks", {}),
        "blocker_count": stale_result.get("blocker_count", 0),
    }
    return _stable_hash(slim)


def fingerprint_plan(plan_result: dict) -> str:
    """Fingerprint implementation plan expansion output."""
    slim = {
        "expansion_status": plan_result.get("expansion_status", ""),
        "accepted_count": plan_result.get("accepted_count", 0),
        "slice_ids": sorted(
            sl.get("slice_id", "") for sl in plan_result.get("implementation_slices", [])
        ),
        "taskcard_ids": sorted(
            tc.get("taskcard_id", "") for tc in plan_result.get("planning_taskcards", [])
        ),
    }
    return _stable_hash(slim)


def compute_sprint_fingerprint(fmt: str, sprint_id: str) -> dict:
    """
    Compute a complete sprint fingerprint for a format.

    Runs the full planning chain and fingerprints each component.

    Parameters
    ----------
    fmt : str
        Format ID (e.g. 'fods', 'fodt')
    sprint_id : str
        Sprint identifier for this fingerprint

    Returns
    -------
    dict with:
      format_id: str
      sprint_id: str
      fingerprints: dict[str, str]   -- component → hash
      metadata_summary: dict         -- human-readable summary
      replay_safe: bool              -- True if all components are hashable
    """
    from format_context_resolver import resolve_format_context
    from lane_selector import select_lanes
    from implementation_plan_expander import expand_implementation_plan
    from stale_detection import detect_stale_state
    from swarm_prompt_generator import generate_prompt

    fingerprints: dict[str, str] = {}
    metadata: dict[str, Any] = {}

    # Context + stale
    ctx = resolve_format_context(fmt)
    stale_result = detect_stale_state(fmt)
    fingerprints["stale"] = fingerprint_stale(stale_result)
    metadata["stale_verdict"] = stale_result.get("verdict", "UNKNOWN")

    # Lane selection
    lane_result = select_lanes(ctx)
    fingerprints["lanes"] = fingerprint_lanes(
        lane_result.get("selected_lanes", []),
        lane_result.get("blocked_lanes", []),
    )
    metadata["selected_lane_count"] = len(lane_result.get("selected_lanes", []))
    metadata["blocked_lane_count"] = len(lane_result.get("blocked_lanes", []))

    # Requirements
    req_state = ctx["requirements_state"]["status"]
    metadata["requirements_state"] = req_state

    # Implementation plan
    plan_result = expand_implementation_plan(fmt)
    if plan_result.get("expansion_status") == "EXPANDED":
        accepted_ids = [
            req
            for sl in plan_result.get("implementation_slices", [])
            for req in sl.get("requirements", [])
        ]
        fingerprints["requirements"] = fingerprint_requirements(accepted_ids)
        fingerprints["plan"] = fingerprint_plan(plan_result)
        metadata["accepted_count"] = len(accepted_ids)
    else:
        fingerprints["requirements"] = _stable_hash([])
        fingerprints["plan"] = _stable_hash({})
        metadata["accepted_count"] = 0

    # Prompt (only if AUTHORITATIVE and not stale-blocked)
    stale_verdict = stale_result.get("verdict", "FRESH")
    if req_state == "REQUIREMENTS_AUTHORITATIVE" and stale_verdict != "STALE_BLOCKED":
        prompt_result = generate_prompt(fmt, sprint_id, f"Fingerprint validation for {fmt}")
        if prompt_result.get("prompt"):
            fingerprints["prompt"] = fingerprint_prompt(prompt_result["prompt"])
            metadata["prompt_char_count"] = len(prompt_result["prompt"])
        else:
            fingerprints["prompt"] = _stable_hash("")
            metadata["prompt_char_count"] = 0
    else:
        fingerprints["prompt"] = _stable_hash("")
        metadata["prompt_char_count"] = 0

    replay_safe = all(isinstance(v, str) and len(v) > 0 for v in fingerprints.values())

    return {
        "format_id": fmt,
        "sprint_id": sprint_id,
        "fingerprints": fingerprints,
        "metadata_summary": metadata,
        "replay_safe": replay_safe,
    }


def compare_fingerprints(baseline: dict, current: dict) -> dict:
    """
    Compare two sprint fingerprint results.

    Returns:
      verdict: CONSISTENT | INCONSISTENT | PARTIAL
      changed: list[str]  -- component names that changed
      unchanged: list[str] -- component names that match
    """
    baseline_fp = baseline.get("fingerprints", {})
    current_fp = current.get("fingerprints", {})

    all_keys = set(baseline_fp.keys()) | set(current_fp.keys())
    changed = []
    unchanged = []

    for key in sorted(all_keys):
        b_val = baseline_fp.get(key)
        c_val = current_fp.get(key)
        if b_val == c_val:
            unchanged.append(key)
        else:
            changed.append(key)

    if not changed:
        verdict = "CONSISTENT"
    elif not unchanged:
        verdict = "INCONSISTENT"
    else:
        verdict = "PARTIAL"

    return {
        "verdict": verdict,
        "changed": changed,
        "unchanged": unchanged,
        "baseline_sprint": baseline.get("sprint_id"),
        "current_sprint": current.get("sprint_id"),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Replay fingerprint tool")
    parser.add_argument("format", nargs="?", default="all")
    parser.add_argument("--sprint-id", default="FINGERPRINT-RUN-001")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    formats = ["fods", "fodt"] if args.format == "all" else [args.format]
    for fmt in formats:
        result = compute_sprint_fingerprint(fmt, args.sprint_id)
        if args.json:
            print(json.dumps(result, indent=2))
            continue
        print(f"\n=== Replay Fingerprint: {fmt.upper()} ===")
        print(f"  REPLAY_SAFE: {result['replay_safe']}")
        for comp, fp in result["fingerprints"].items():
            print(f"  {comp}: {fp}")
        for key, val in result["metadata_summary"].items():
            print(f"  meta.{key}: {val}")


if __name__ == "__main__":
    main()
