"""
multi_format_planning.py -- Lane C Deliverable (CONWAY-R7R8)

Multi-format orchestration planning layer.

PURPOSE:
  Aggregate format context, stale state, lane selection, and implementation
  planning across multiple formats simultaneously. Produces a unified
  multi-format planning summary for human-supervised orchestration.

SUPPORTS:
  - FODS, FODT (current)
  - Designed for extensibility: HWP/HWPX, ALZ/EGG, public-spec formats

OUTPUTS:
  - per_format_context: authority state per format
  - per_format_stale: stale verdict per format
  - per_format_lanes: selected/blocked lanes per format
  - per_format_plan: implementation plan expansion per format
  - orchestration_order: deterministic dependency-aware planning order
  - cross_format_summary: aggregated metrics

DRY-RUN ONLY. No implementation execution.

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

SUPPORTED_FORMATS = ["fods", "fodt"]


def plan_multi_format(formats: list[str] | None = None) -> dict:
    """
    Run multi-format planning for a list of formats.

    Parameters
    ----------
    formats : list[str] | None
        Format IDs to plan. Defaults to all supported formats.

    Returns
    -------
    dict with:
      formats_requested: list[str]
      formats_authoritative: list[str]
      formats_blocked: list[str]
      formats_stale: list[str]
      per_format_context: dict[str, dict]    -- resolver output per format
      per_format_stale: dict[str, str]       -- stale verdict per format
      per_format_lanes: dict[str, dict]      -- lane selector output per format
      per_format_plan: dict[str, dict]       -- expander output per format
      orchestration_order: list[dict]        -- recommended planning order
      cross_format_summary: dict             -- aggregated metrics
      governance: dict
    """
    from format_context_resolver import resolve_format_context
    from lane_selector import select_lanes
    from implementation_plan_expander import expand_implementation_plan

    if formats is None:
        formats = list(SUPPORTED_FORMATS)

    per_ctx: dict[str, dict] = {}
    per_stale: dict[str, str] = {}
    per_lanes: dict[str, dict] = {}
    per_plan: dict[str, dict] = {}

    authoritative: list[str] = []
    blocked: list[str] = []
    stale_formats: list[str] = []

    for fmt in formats:
        ctx = resolve_format_context(fmt)
        per_ctx[fmt] = ctx

        req_state = ctx["requirements_state"]["status"]
        stale_info = ctx["requirements_state"].get("stale") or {}
        stale_verdict = stale_info.get("verdict", "FRESH") if isinstance(stale_info, dict) else "FRESH"
        per_stale[fmt] = stale_verdict

        if stale_verdict == "STALE_BLOCKED":
            stale_formats.append(fmt)

        if req_state == "REQUIREMENTS_AUTHORITATIVE" and stale_verdict != "STALE_BLOCKED":
            authoritative.append(fmt)
        else:
            blocked.append(fmt)

        lane_result = select_lanes(ctx)
        per_lanes[fmt] = lane_result

        plan_result = expand_implementation_plan(fmt)
        per_plan[fmt] = plan_result

    # Build orchestration order — authoritative + non-stale first
    orchestration_order = []
    for fmt in formats:
        ctx = per_ctx[fmt]
        plan = per_plan[fmt]
        stale = per_stale[fmt]
        req_state = ctx["requirements_state"]["status"]

        orchestration_order.append({
            "format_id": fmt,
            "requirements_state": req_state,
            "stale_verdict": stale,
            "expansion_status": plan.get("expansion_status", "UNKNOWN"),
            "accepted_count": plan.get("accepted_count", 0),
            "slice_count": len(plan.get("implementation_slices", [])),
            "ready_for_planning": (
                req_state == "REQUIREMENTS_AUTHORITATIVE"
                and stale != "STALE_BLOCKED"
            ),
        })

    # Sort: ready formats first
    orchestration_order.sort(key=lambda x: (0 if x["ready_for_planning"] else 1, x["format_id"]))

    # Cross-format summary
    total_accepted = sum(
        per_plan[f].get("accepted_count", 0) for f in formats
    )
    total_slices = sum(
        len(per_plan[f].get("implementation_slices", [])) for f in formats
    )
    total_taskcards = sum(
        len(per_plan[f].get("planning_taskcards", [])) for f in formats
    )

    cross_summary = {
        "total_formats": len(formats),
        "authoritative_formats": len(authoritative),
        "blocked_formats": len(blocked),
        "stale_formats": len(stale_formats),
        "total_accepted_requirements": total_accepted,
        "total_implementation_slices": total_slices,
        "total_planning_taskcards": total_taskcards,
        "planning_ready": len(authoritative) > 0,
    }

    governance = {
        "commercial_product_ready": False,
        "gate_self_approval_allowed": False,
        "autonomous_execution_allowed": False,
        "dry_run_only": True,
        "implementation_requires_human_authorization": True,
    }

    return {
        "formats_requested": formats,
        "formats_authoritative": authoritative,
        "formats_blocked": blocked,
        "formats_stale": stale_formats,
        "per_format_context": per_ctx,
        "per_format_stale": per_stale,
        "per_format_lanes": per_lanes,
        "per_format_plan": per_plan,
        "orchestration_order": orchestration_order,
        "cross_format_summary": cross_summary,
        "governance": governance,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Multi-format planning orchestration")
    parser.add_argument("formats", nargs="*", default=None, help="Format IDs (default: all)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = plan_multi_format(args.formats if args.formats else None)

    if args.json:
        # Exclude large nested dicts for readability
        slim = {k: v for k, v in result.items()
                if k not in ("per_format_context", "per_format_lanes", "per_format_plan")}
        print(json.dumps(slim, indent=2))
        return

    summary = result["cross_format_summary"]
    print(f"\n=== Multi-Format Planning Summary ===")
    print(f"  Formats:     {', '.join(result['formats_requested'])}")
    print(f"  Authoritative: {result['formats_authoritative']}")
    print(f"  Blocked:       {result['formats_blocked']}")
    print(f"  Stale:         {result['formats_stale']}")
    print(f"  Total accepted reqs:  {summary['total_accepted_requirements']}")
    print(f"  Total slices:         {summary['total_implementation_slices']}")
    print(f"  Total taskcards:      {summary['total_planning_taskcards']}")
    print(f"  Planning ready:       {summary['planning_ready']}")
    print(f"\n  Orchestration order:")
    for item in result["orchestration_order"]:
        status = "READY" if item["ready_for_planning"] else "BLOCKED"
        print(f"    [{status}] {item['format_id']}: {item['accepted_count']} accepted, "
              f"{item['slice_count']} slices, stale={item['stale_verdict']}")


if __name__ == "__main__":
    main()
