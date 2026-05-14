"""
planning_bundle_runtime.py -- Lane F Deliverable (CONWAY-R7R8)

Deterministic planning bundle runtime.

PURPOSE:
  Produce a bounded, deterministic dry-run planning bundle containing:
  - Selected lanes
  - Authoritative requirements (IDs only, no implementation)
  - Planning slices (taskcard descriptors)
  - Replay fingerprints
  - Evidence contract references
  - Stale-state verdicts
  - Governance summaries

  Bundles are in-memory dicts — no file system writes in this module.
  Actual file output is the evidence builder's responsibility.

BOUNDED BY DESIGN:
  - No prior ZIP inclusion
  - No implementation artifacts
  - No generated source code
  - No binary assets
  - Size target: < 1 KB per format (JSON)

ALLOWED:
  - Reading all planning outputs
  - Aggregating into a planning bundle dict
  - Computing fingerprints

NOT ALLOWED:
  - Writing to evidence-bundles/ directly
  - Including source code or binaries
  - Gate approval
  - Implementation execution
  - Commercial readiness claims

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))


def build_planning_bundle(
    formats: list[str] | None = None,
    sprint_id: str = "PLANNING-BUNDLE-001",
    sprint_mission: str = "Dry-run planning bundle generation.",
) -> dict:
    """
    Build a deterministic planning bundle for one or more formats.

    Parameters
    ----------
    formats : list[str] | None
        Formats to include. Defaults to ['fods', 'fodt'].
    sprint_id : str
        Sprint identifier for this bundle.
    sprint_mission : str
        Mission description.

    Returns
    -------
    dict with:
      bundle_type: str           -- always 'planning_bundle'
      sprint_id: str
      sprint_mission: str
      timestamp: str
      formats: list[str]
      per_format_summary: dict   -- per-format planning summary
      global_fingerprints: dict  -- per-format fingerprint dict
      stale_verdicts: dict       -- per-format stale verdict
      selected_lanes: dict       -- per-format selected lanes
      evidence_contract_refs: dict  -- planned contract paths
      governance: dict           -- hardcoded safety flags
      bundle_size_warning: bool  -- True if bundle exceeds soft limit
      dry_run_only: bool         -- always True
    """
    from multi_format_planning import plan_multi_format
    from replay_fingerprint import compute_sprint_fingerprint

    if formats is None:
        formats = ["fods", "fodt"]

    timestamp = datetime.utcnow().isoformat() + "Z"

    # Aggregate multi-format planning
    plan_result = plan_multi_format(formats)

    per_format_summary: dict[str, Any] = {}
    global_fingerprints: dict[str, dict] = {}
    stale_verdicts: dict[str, str] = {}
    selected_lanes: dict[str, list] = {}
    evidence_contract_refs: dict[str, str] = {}

    for fmt in formats:
        # Per-format summary (slim — no nested context)
        fmt_plan = plan_result["per_format_plan"].get(fmt, {})
        fmt_lanes = plan_result["per_format_lanes"].get(fmt, {})
        stale = plan_result["per_format_stale"].get(fmt, "UNKNOWN")

        per_format_summary[fmt] = {
            "expansion_status": fmt_plan.get("expansion_status", "UNKNOWN"),
            "accepted_count": fmt_plan.get("accepted_count", 0),
            "slice_count": len(fmt_plan.get("implementation_slices", [])),
            "taskcard_count": len(fmt_plan.get("planning_taskcards", [])),
            "dependency_group_count": len(fmt_plan.get("dependency_groups", [])),
            "stale_verdict": stale,
            "requirements_state": fmt_plan.get("requirements_state", "UNKNOWN"),
        }

        stale_verdicts[fmt] = stale
        selected_lanes[fmt] = fmt_lanes.get("selected_lanes", [])

        # Replay fingerprints
        try:
            fp = compute_sprint_fingerprint(fmt, sprint_id)
            global_fingerprints[fmt] = fp["fingerprints"]
        except Exception as e:
            global_fingerprints[fmt] = {"error": str(e)}

        # Evidence contract reference (planned path, not built)
        evidence_contract_refs[fmt] = (
            f"tools/evidence/contracts/{sprint_id.lower()}-{fmt}.yaml"
        )

    cross_summary = plan_result.get("cross_format_summary", {})

    governance = {
        "commercial_product_ready": False,
        "gate_self_approval_allowed": False,
        "autonomous_execution_allowed": False,
        "dry_run_only": True,
        "implementation_requires_human_authorization": True,
        "dec034_iv_required_before_promotion": True,
        "no_prior_zip_inclusion": True,
    }

    # Rough size estimate (JSON bytes)
    bundle_slim = {
        "per_format_summary": per_format_summary,
        "global_fingerprints": global_fingerprints,
        "stale_verdicts": stale_verdicts,
        "selected_lanes": selected_lanes,
    }
    estimated_size = len(json.dumps(bundle_slim, sort_keys=True))
    SIZE_SOFT_LIMIT = 50_000  # 50 KB soft limit for planning bundle JSON

    return {
        "bundle_type": "planning_bundle",
        "sprint_id": sprint_id,
        "sprint_mission": sprint_mission,
        "timestamp": timestamp,
        "formats": formats,
        "per_format_summary": per_format_summary,
        "global_fingerprints": global_fingerprints,
        "stale_verdicts": stale_verdicts,
        "selected_lanes": selected_lanes,
        "evidence_contract_refs": evidence_contract_refs,
        "cross_format_summary": cross_summary,
        "governance": governance,
        "estimated_json_bytes": estimated_size,
        "bundle_size_warning": estimated_size > SIZE_SOFT_LIMIT,
        "dry_run_only": True,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Planning bundle runtime")
    parser.add_argument("formats", nargs="*", default=None)
    parser.add_argument("--sprint-id", default="PLANNING-BUNDLE-001")
    parser.add_argument("--mission", default="Dry-run planning bundle generation.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = build_planning_bundle(
        formats=args.formats or None,
        sprint_id=args.sprint_id,
        sprint_mission=args.mission,
    )

    if args.json:
        print(json.dumps(result, indent=2))
        return

    summary = result["cross_format_summary"]
    print(f"\n=== Planning Bundle: {result['sprint_id']} ===")
    print(f"  BUNDLE_TYPE:        {result['bundle_type']}")
    print(f"  DRY_RUN_ONLY:       {result['dry_run_only']}")
    print(f"  FORMATS:            {result['formats']}")
    print(f"  ESTIMATED_SIZE:     {result['estimated_json_bytes']} bytes")
    print(f"  SIZE_WARNING:       {result['bundle_size_warning']}")
    print(f"  TOTAL_ACCEPTED:     {summary.get('total_accepted_requirements', 0)}")
    print(f"  TOTAL_TASKCARDS:    {summary.get('total_planning_taskcards', 0)}")
    print(f"  COMMERCIAL_READY:   {result['governance']['commercial_product_ready']}")
    for fmt in result["formats"]:
        fs = result["per_format_summary"][fmt]
        stale = result["stale_verdicts"][fmt]
        print(f"  [{fmt.upper()}] accepted={fs['accepted_count']} "
              f"slices={fs['slice_count']} stale={stale}")


if __name__ == "__main__":
    main()
