"""
capability_to_feature_compiler.py — Planning stub: gap-ledger → advisory taskcard YAML stubs.

DEDUPLICATION NOTICE (TC-LA-007, 2026-06-26):
  This is the PLANNING tool — it generates advisory YAML stub files for human review.
  It is NOT the pipeline integration.

  CANONICAL PIPELINE implementation: tools/supervisor/capability_feature_compiler.py
    → Produces next-work-items.json consumed by autonomous_cycle.py
    → Use this for supervisor loop work selection

  THIS TOOL (tools/capability_layer/capability_to_feature_compiler.py):
    → Produces per-gap YAML stub files in reports/capability-layer/taskcard-stubs/
    → Output is advisory only (status: "backlog", requires_human_confirmation: true)
    → Use this for offline planning and gap triage

  Gap-filtering rules in this file are intentionally simpler than the pipeline version.
  If you need authoritative skip-status rules, see _SKIP_STATUSES in the pipeline version.

Purpose: Read gap-ledger.json → output feature taskcard YAML stubs for agent consumption.

Governance:
  - Generated taskcard stubs have provenance: "gap_ledger_derived" and status: "backlog"
  - Stubs require human confirmation before promotion to active taskcards
  - This tool does NOT auto-execute taskcards; stubs are advisory only

Usage:
    python tools/capability_layer/capability_to_feature_compiler.py \
      --gap-ledger reports/capability-layer/gap-ledger.json \
      --output-dir reports/capability-layer/taskcard-stubs \
      --max-priority P1

Created: 2026-06-23
Task: TC-UNIFIED-034 (majestic-cooking-waffle Phase 3c)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_DEFAULT_GAP_LEDGER = "reports/capability-layer/gap-ledger.json"
_PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def load_gaps(gap_ledger_path: str) -> list[dict]:
    """Load gaps from gap-ledger.json.

    The gap ledger has root object with a "gaps" key containing a list.
    Returns the list of gap dicts.
    """
    p = Path(gap_ledger_path)
    if not p.exists():
        raise FileNotFoundError(f"Gap ledger not found: {p}")
    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data.get("gaps", [])


def filter_actionable_gaps(gaps: list[dict], max_priority: str = "P1") -> list[dict]:
    """Filter to gaps at or above the given priority threshold.

    Excludes:
    - Already closed/resolved gaps
    - Gaps blocked by external gates
    - Gaps with priority lower than max_priority

    Priority ordering: P0 (highest) < P1 < P2 < P3 (lowest).
    max_priority="P1" means include P0 and P1, exclude P2 and P3.
    """
    max_rank = _PRIORITY_ORDER.get(max_priority, 1)
    result = []
    for gap in gaps:
        status = gap.get("status", "open")
        if status in ("closed", "CLOSED", "resolved", "RESOLVED"):
            continue
        if gap.get("blocked_by_external_gate"):
            continue
        priority = gap.get("priority", "P3")
        rank = _PRIORITY_ORDER.get(priority, 99)
        if rank <= max_rank:
            result.append(gap)
    # Sort: P0 first, then P1, then by gap_id for determinism
    result.sort(key=lambda g: (_PRIORITY_ORDER.get(g.get("priority", "P3"), 99), g.get("gap_id", "")))
    return result


def generate_taskcard_stubs(gaps: list[dict], output_dir: str) -> list[str]:
    """Generate YAML taskcard stub files from gap list.

    Each stub file is named: {gap_id}-taskcard-stub.yaml
    Returns list of generated file paths.

    Governance constraints:
    - provenance: "gap_ledger_derived" (mandatory)
    - status: "backlog" (mandatory — not active until confirmed)
    - advisory_only: true
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for gap in gaps:
        gap_id = gap.get("gap_id", "GAP-UNKNOWN")
        fmt = gap.get("format", "unknown")
        capability = gap.get("capability_name", gap.get("capability", "unknown"))
        priority = gap.get("priority", "P3")
        stub = {
            "task_id": f"TC-FEAT-{gap_id}",
            "gap_id": gap_id,
            "format": fmt,
            "capability_name": capability,
            "priority": priority,
            "status": "backlog",
            "provenance": "gap_ledger_derived",
            "advisory_only": True,
            "requires_human_confirmation": True,
            "title": f"Implement {capability} for {fmt}",
            "objective": (
                f"Implement the {capability!r} capability for the {fmt} format "
                f"to close gap {gap_id}."
            ),
            "spec_facts": gap.get("spec_facts", []),
            "gap_source": gap.get("source", "gap_ledger"),
            "gap_notes": gap.get("notes", ""),
            "phase2_extensions": {
                "sal_fact_refs": gap.get("spec_facts", []),  # Phase 2 IMPLEMENTED: wired to gap spec_facts
                "qname_refs": [],     # Future: wire to QName registry
            },
        }
        fname = out / f"{gap_id}-taskcard-stub.yaml"
        fname.write_text(json.dumps(stub, indent=2) + "\n", encoding="utf-8")
        written.append(str(fname))
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate feature taskcard stubs from gap ledger",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--gap-ledger",
        default=_DEFAULT_GAP_LEDGER,
        help=f"Path to gap-ledger.json (default: {_DEFAULT_GAP_LEDGER})",
    )
    parser.add_argument(
        "--output-dir",
        default="reports/capability-layer/taskcard-stubs",
        help="Output directory for taskcard stub YAML files",
    )
    parser.add_argument(
        "--max-priority",
        default="P1",
        choices=list(_PRIORITY_ORDER.keys()),
        help="Maximum priority to include (default: P1; includes P0 and P1)",
    )
    args = parser.parse_args(argv)

    try:
        gaps = load_gaps(args.gap_ledger)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    actionable = filter_actionable_gaps(gaps, max_priority=args.max_priority)
    print(f"Total gaps: {len(gaps)}")
    print(f"Actionable gaps (priority <= {args.max_priority}): {len(actionable)}")

    if not actionable:
        print("No actionable gaps found — no stubs generated")
        return 0

    written = generate_taskcard_stubs(actionable, args.output_dir)
    print(f"Generated {len(written)} taskcard stub(s) in: {args.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
