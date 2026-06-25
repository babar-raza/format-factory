"""audit_gap_ledger_sal_refs.py — Phase D (FF-FORENSIC-AUDIT-20260623)

Audits gap-ledger.json for SAL traceability: for each gap entry with spec_facts IDs,
verifies those IDs exist in sal-facts-latest.json. Emits:
    reports/capability-layer/gap-sal-traceability-{date}.json

This establishes whether the capability layer is grounded in real SAL facts,
or whether spec_facts references are dangling (no corresponding SAL entry).

Usage:
    python tools/audit_gap_ledger_sal_refs.py [--out PATH] [--format FMT] [--status STATUS]
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).parent.parent
_SAL_PATH = _REPO / ".local/spec-cache/sal-facts-latest.json"
_GAP_LEDGER_PATH = _REPO / "reports/capability-layer/gap-ledger.json"


def load_all_sal_fact_ids() -> set[str]:
    """Load all SAL fact IDs into a single set for fast lookup."""
    if not _SAL_PATH.exists():
        return set()
    try:
        data = json.loads(_SAL_PATH.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return set()

    all_ids: set[str] = set()
    for result in data.get("results", []):
        for fact in result.get("spec_facts", []):
            qname = fact.get("qname", "")
            if qname.startswith("FACT-"):
                all_ids.add(qname)

    return all_ids


def run_audit(
    format_filter: str | None = None,
    status_filter: str | None = None,
    out_path: Path | None = None,
) -> dict[str, Any]:
    """Audit gap-ledger spec_facts references against SAL output."""
    if not _GAP_LEDGER_PATH.exists():
        print(f"ERROR: {_GAP_LEDGER_PATH} not found")
        return {}

    try:
        ledger = json.loads(_GAP_LEDGER_PATH.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        print(f"ERROR loading gap-ledger: {e}")
        return {}

    gaps = ledger.get("gaps", [])
    sal_ids = load_all_sal_fact_ids()
    print(f"SAL fact IDs loaded: {len(sal_ids)}")
    print(f"Gap-ledger entries: {len(gaps)}")

    per_gap_results = []
    total_with_refs = 0
    total_no_refs = 0
    total_all_resolved = 0
    total_partial = 0
    total_none_resolved = 0
    dangling_refs: list[dict] = []
    fully_orphaned: list[dict] = []

    for gap in gaps:
        fmt = gap.get("format", "").upper()
        if format_filter and fmt.lower() != format_filter.lower():
            continue
        if status_filter and gap.get("status", "") != status_filter:
            continue

        spec_facts = gap.get("spec_facts", [])
        gap_id = gap.get("gap_id", "?")

        if not spec_facts:
            total_no_refs += 1
            per_gap_results.append({
                "gap_id": gap_id,
                "format": fmt,
                "status": gap.get("status", ""),
                "spec_facts_count": 0,
                "resolved_count": 0,
                "traceability": "NO_REFS",
                "dangling": [],
            })
            fully_orphaned.append({"gap_id": gap_id, "format": fmt, "issue": "No spec_facts IDs declared"})
            continue

        total_with_refs += 1
        resolved = [f for f in spec_facts if f in sal_ids]
        dangling = [f for f in spec_facts if f not in sal_ids]

        if len(resolved) == len(spec_facts):
            traceability = "FULLY_RESOLVED"
            total_all_resolved += 1
        elif resolved:
            traceability = "PARTIAL"
            total_partial += 1
        else:
            traceability = "NONE_RESOLVED"
            total_none_resolved += 1

        per_gap_results.append({
            "gap_id": gap_id,
            "format": fmt,
            "status": gap.get("status", ""),
            "spec_facts_count": len(spec_facts),
            "resolved_count": len(resolved),
            "traceability": traceability,
            "dangling": dangling[:5],  # limit to 5 for readability
        })

        if dangling:
            for d in dangling[:3]:
                dangling_refs.append({
                    "gap_id": gap_id,
                    "format": fmt,
                    "dangling_ref": d,
                    "severity": "HIGH" if traceability == "NONE_RESOLVED" else "WARN",
                })

    # Summaries
    total_audited = len(per_gap_results)
    high_severity_dangling = sum(1 for d in dangling_refs if d["severity"] == "HIGH")

    report = {
        "audit_type": "gap_ledger_sal_traceability",
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "sal_facts_path": str(_SAL_PATH),
        "gap_ledger_path": str(_GAP_LEDGER_PATH),
        "sal_total_fact_ids": len(sal_ids),
        "filters_applied": {
            "format": format_filter,
            "status": status_filter,
        },
        "summary": {
            "total_gaps_audited": total_audited,
            "gaps_with_spec_facts": total_with_refs,
            "gaps_without_spec_facts": total_no_refs,
            "fully_resolved": total_all_resolved,
            "partial": total_partial,
            "none_resolved": total_none_resolved,
            "total_dangling_refs_sampled": len(dangling_refs),
            "high_severity_dangling": high_severity_dangling,
            "traceability_pct": (
                round(100 * total_all_resolved / total_with_refs, 1)
                if total_with_refs else None
            ),
        },
        "dangling_ref_samples": dangling_refs[:50],
        "fully_orphaned_gaps": fully_orphaned[:50],
        "per_gap": per_gap_results,
    }

    # Print summary
    print("\nGap Ledger SAL Traceability Report")
    print(f"{'='*50}")
    print(f"Total gaps audited:   {total_audited}")
    print(f"With spec_facts refs: {total_with_refs}")
    print(f"Without refs:         {total_no_refs}")
    print(f"Fully resolved:       {total_all_resolved}")
    print(f"Partial:              {total_partial}")
    print(f"None resolved:        {total_none_resolved}")
    print(f"High severity:        {high_severity_dangling}")
    if total_with_refs:
        pct = round(100 * total_all_resolved / total_with_refs, 1)
        print(f"Traceability:         {pct}%")
    print()

    if dangling_refs[:5]:
        print("Sample dangling refs:")
        for d in dangling_refs[:5]:
            print(f"  {d['gap_id']}: {d['dangling_ref']} ({d['severity']})")

    # Write report
    if out_path is None:
        date_str = datetime.now().strftime("%Y%m%d")
        out_path = _REPO / f"reports/capability-layer/gap-sal-traceability-{date_str}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport written: {out_path}")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Gap ledger SAL traceability audit")
    parser.add_argument("--format", help="Filter to one format (e.g. FODS)")
    parser.add_argument("--status", help="Filter to gap status (e.g. open, closed)")
    parser.add_argument("--out", help="Output path for report JSON")
    args = parser.parse_args()

    out_path = Path(args.out) if args.out else None
    report = run_audit(
        format_filter=args.format,
        status_filter=args.status,
        out_path=out_path,
    )

    high = report.get("summary", {}).get("high_severity_dangling", 0)
    if high > 0:
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
