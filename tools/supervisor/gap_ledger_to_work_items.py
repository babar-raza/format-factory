"""gap_ledger_to_work_items.py — Phase E (FF-FORENSIC-AUDIT-20260623 / TC-CAPABILITY-REPAIR-002)

Batch compiler: reads gap-ledger.json → converts open gaps to next-work-items.json format.
This is the capability-to-feature compiler Phase 2 implementation.

Priority scoring:
    P0 → score 0 (highest urgency)
    P1 → score 10
    P2 → score 20
    P3 → score 30
    ...
    P8 → score 80 (lowest urgency)
Adjustments:
    blocks_poc=True → -5 (escalate)
    commercial_impact=high → -3
    blocks_readiness=True → -2
    foss_impact=high → -1
    status=not_yet_parsed → demote to score 99

Usage:
    python tools/supervisor/gap_ledger_to_work_items.py [--status open] [--max N] [--out PATH]
    python tools/supervisor/gap_ledger_to_work_items.py --append-to .local/supervisor/next-work-items.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parent.parent.parent
_GAP_LEDGER = _REPO / "reports/capability-layer/gap-ledger.json"
_DEFAULT_OUT = _REPO / ".local/supervisor/next-work-items.json"


def _priority_score(gap: dict[str, Any]) -> int:
    """Compute numeric priority score (lower = higher urgency)."""
    priority_str = str(gap.get("priority", "P4")).strip()
    if priority_str.startswith("P") and priority_str[1:].isdigit():
        score = int(priority_str[1:]) * 10
    else:
        score = 40  # default mid-priority

    # Adjust for impact flags
    if gap.get("blocks_poc"):
        score -= 5
    if str(gap.get("commercial_impact", "")).lower() in ("high", "critical"):
        score -= 3
    if gap.get("blocks_readiness"):
        score -= 2
    if str(gap.get("foss_impact", "")).lower() == "high":
        score -= 1

    # Demote unparsed / missing info
    if gap.get("status") == "not_yet_parsed":
        score = 99

    return max(0, score)


def _gap_to_work_item(gap: dict[str, Any], score: int) -> dict[str, Any]:
    """Convert a gap record to a next-work-items work item."""
    gap_id = gap.get("gap_id", "GAP-UNKNOWN")
    fmt = gap.get("format", "?")
    cap = gap.get("capability_name", "?")
    product_type = gap.get("product_type", "foss")
    gap_type = gap.get("gap_type", "")
    suggested = gap.get("suggested_taskcard", "")

    title = f"[{fmt}] {cap} — {gap_type.replace('_', ' ').title()}" if gap_type else f"[{fmt}] {cap}"

    # Build description from gap fields
    desc_parts = [f"Gap: {gap_id}"]
    if gap.get("current_state"):
        desc_parts.append(f"Current state: {gap['current_state']}")
    if gap.get("notes"):
        desc_parts.append(f"Notes: {gap['notes']}")
    if suggested:
        desc_parts.append(f"Suggested action: {suggested}")
    if gap.get("blockers"):
        desc_parts.append(f"Blockers: {gap['blockers']}")

    spec_facts = gap.get("spec_facts", [])
    if spec_facts:
        desc_parts.append(f"Spec facts: {', '.join(spec_facts[:3])}" + (" ..." if len(spec_facts) > 3 else ""))

    return {
        "item_id": gap_id,
        "title": title,
        "lane": f"product-{product_type}",
        "priority": score,
        "description": " | ".join(desc_parts),
        "acceptance_criteria": (
            gap.get("suggested_verification") or
            f"Implement {cap} for {fmt}; tests pass; spec_facts verified in SAL"
        ),
        "verification_command": f".venv/Scripts/pytest tests/python/{fmt.lower()}/ -q",
        "evidence_expected": f"Test run showing {cap} passing for {fmt}",
        "source": "gap-ledger",
        "gap_id": gap_id,
        "format": fmt,
        "capability_name": cap,
        "gap_type": gap_type,
        "spec_facts": spec_facts[:5],
        "stop_reason_adjudication": "agent-owned",
        "human_required": False,
        "blocked_by": gap.get("blockers") or None,
        "external_gate": False,
    }


def compile_gaps_to_work_items(
    status_filter: str = "open",
    max_items: int = 20,
    format_filter: str | None = None,
) -> list[dict[str, Any]]:
    """Read gap-ledger.json and compile open gaps to work items.

    Args:
        status_filter: Only include gaps with this status (default 'open').
        max_items: Maximum number of items to return (sorted by priority score).
        format_filter: If set, only include gaps for this format.

    Returns:
        List of work item dicts sorted by priority score (ascending = highest priority first).
    """
    if not _GAP_LEDGER.exists():
        return []

    try:
        ledger = json.loads(_GAP_LEDGER.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return []

    gaps = ledger.get("gaps", [])

    # Filter
    filtered = []
    for gap in gaps:
        if gap.get("status") != status_filter:
            continue
        if format_filter and gap.get("format", "").upper() != format_filter.upper():
            continue
        filtered.append(gap)

    # Score and sort
    scored = [(gap, _priority_score(gap)) for gap in filtered]
    scored.sort(key=lambda x: x[1])

    # Convert top N to work items
    return [_gap_to_work_item(gap, score) for gap, score in scored[:max_items]]


def run(
    status_filter: str = "open",
    max_items: int = 20,
    format_filter: str | None = None,
    out_path: Path | None = None,
    append_to: Path | None = None,
) -> dict[str, Any]:
    """Main entry point: compile gaps and write output."""
    work_items = compile_gaps_to_work_items(
        status_filter=status_filter,
        max_items=max_items,
        format_filter=format_filter,
    )

    print("Gap-ledger -> Work Items Compiler")
    print(f"{'='*40}")
    print(f"Status filter: {status_filter}")
    print(f"Max items:     {max_items}")
    print(f"Items selected: {len(work_items)}")

    if work_items:
        print(f"\nTop 5 work items (by priority):")
        for item in work_items[:5]:
            print(f"  [{item['priority']:3d}] {item['item_id']}: {item['title'][:60]}")

    if append_to:
        # Append to existing next-work-items.json (non-destructive)
        try:
            existing = json.loads(append_to.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            existing = {"items": [], "work_selection_mode": "gap-ledger"}
        existing_ids = {i.get("item_id") for i in existing.get("items", [])}
        new_items = [i for i in work_items if i["item_id"] not in existing_ids]
        existing.setdefault("items", []).extend(new_items)
        existing["gap_ledger_compiled_at"] = datetime.now(tz=timezone.utc).isoformat()
        existing["gap_ledger_items_added"] = len(new_items)
        append_to.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        print(f"\nAppended {len(new_items)} new items to {append_to}")
        return existing

    # Write standalone output
    output_path = out_path or _DEFAULT_OUT
    output = {
        "items": work_items,
        "work_selection_mode": "gap-ledger",
        "stream": "mainstream",
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "source": "gap_ledger_to_work_items.py",
        "filters": {
            "status": status_filter,
            "max_items": max_items,
            "format": format_filter,
        },
        "total_items": len(work_items),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"\nOutput written: {output_path}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile gap-ledger.json open gaps to next-work-items.json"
    )
    parser.add_argument("--status", default="open", help="Gap status filter (default: open)")
    parser.add_argument("--max", type=int, default=20, help="Max items to emit (default: 20)")
    parser.add_argument("--format", help="Filter to one format (e.g. FODS)")
    parser.add_argument("--out", help="Output path (default: .local/supervisor/next-work-items.json)")
    parser.add_argument("--append-to", help="Append to existing next-work-items.json (non-destructive)")
    args = parser.parse_args()

    out_path = Path(args.out) if args.out else None
    append_to = Path(args.append_to) if getattr(args, "append_to", None) else None

    run(
        status_filter=args.status,
        max_items=args.max,
        format_filter=args.format,
        out_path=out_path,
        append_to=append_to,
    )


if __name__ == "__main__":
    main()
