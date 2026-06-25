#!/usr/bin/env python3
"""
backfill_gap_spec_fact_refs.py — Backfill gap-ledger entries with spec_facts from sal-facts.

Strategy: for each gap entry missing spec_facts, assign the top-N verified fact IDs
from sal-facts-latest.json for the matching format.

Idempotent: skips gaps that already have non-empty spec_facts.
"""
import json
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent.parent


def _load_sal_facts(sal_facts_path: Path) -> dict:
    """Build format -> [fact_ids] index from sal-facts-latest.json."""
    sal = json.loads(sal_facts_path.read_text(encoding="utf-8", errors="replace"))
    results = sal.get("results", [])
    format_facts: dict = {}
    for r in results:
        fmt = r.get("format_id", "").lower().replace("-", "_")
        facts = r.get("spec_facts", [])
        # Use all verified facts (not just top N) for best coverage
        verified = [
            f.get("qname")
            for f in facts
            if f.get("qname")
            and f.get("fact_status") == "verified"
        ]
        if fmt and verified:
            format_facts[fmt] = verified
    return format_facts


def _normalize_format(fmt_str: str) -> str:
    """Normalize format string to match SAL format_id keys."""
    return fmt_str.lower().strip().replace("-", "_").replace(" ", "_")


def backfill(
    gap_ledger_path: str,
    sal_facts_path: str,
    formats: list,
    dry_run: bool,
    output: str | None,
    top_n: int = 10,
) -> dict:
    gap_path = Path(gap_ledger_path)
    sal_path = Path(sal_facts_path)

    if not gap_path.exists():
        print(f"ERROR: gap-ledger not found: {gap_path}", file=sys.stderr)
        sys.exit(1)
    if not sal_path.exists():
        print(f"ERROR: sal-facts not found: {sal_path}", file=sys.stderr)
        sys.exit(1)

    gaps_data = json.loads(gap_path.read_text(encoding="utf-8", errors="replace"))
    format_facts = _load_sal_facts(sal_path)

    # Restrict to requested formats if specified (None = all formats)
    target_formats = set(_normalize_format(f) for f in formats) if formats else None

    updated = 0
    skipped_has_facts = 0
    skipped_no_sal = 0
    skipped_format_filter = 0
    samples_updated = []

    gaps = gaps_data.get("gaps", [])
    for gap in gaps:
        gap_fmt = _normalize_format(gap.get("format", ""))

        # Apply format filter
        if target_formats and gap_fmt not in target_formats:
            skipped_format_filter += 1
            continue

        # Skip already populated
        if gap.get("spec_facts") and len(gap.get("spec_facts", [])) > 0:
            skipped_has_facts += 1
            continue

        # Look up SAL facts for this format
        sal_facts_for_fmt = format_facts.get(gap_fmt)
        if not sal_facts_for_fmt:
            skipped_no_sal += 1
            continue

        # Assign top N facts
        assigned = sal_facts_for_fmt[:top_n]
        gap["spec_facts"] = assigned
        updated += 1

        if len(samples_updated) < 5:
            samples_updated.append({
                "gap_id": gap.get("gap_id"),
                "format": gap.get("format"),
                "assigned_count": len(assigned),
                "sample_facts": assigned[:3],
            })

    summary = {
        "updated": updated,
        "skipped_has_facts": skipped_has_facts,
        "skipped_no_sal": skipped_no_sal,
        "skipped_format_filter": skipped_format_filter,
        "format_facts_available": sorted(format_facts.keys()),
        "samples": samples_updated,
        "dry_run": dry_run,
    }

    prefix = "DRY-RUN: " if dry_run else ""
    print(f"{prefix}updated={updated}, skipped_has_facts={skipped_has_facts}, "
          f"skipped_no_sal={skipped_no_sal}, skipped_filter={skipped_format_filter}")

    if not dry_run:
        backup_path = gap_path.with_suffix(".json.backfill-backup")
        if not backup_path.exists():
            backup_path.write_text(
                gap_path.read_text(encoding="utf-8", errors="replace"),
                encoding="utf-8",
            )
            print(f"Backup written to: {backup_path}")
        gap_path.write_text(
            json.dumps(gaps_data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"Gap-ledger updated: {gap_path}")

    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"Output written to: {output}")

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backfill gap-ledger spec_facts from SAL verified facts."
    )
    parser.add_argument(
        "--gap-ledger",
        default=str(REPO / "reports/capability-layer/gap-ledger.json"),
    )
    parser.add_argument(
        "--sal-facts",
        default=str(REPO / ".local/sal-output/sal-facts-latest.json"),
    )
    parser.add_argument(
        "--formats",
        default="",
        help="Comma-separated format list (empty = all formats)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Max facts to assign per gap",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", default="", help="Path for JSON summary output")

    args = parser.parse_args()
    fmts = [f.strip() for f in args.formats.split(",") if f.strip()] if args.formats else []

    backfill(
        gap_ledger_path=args.gap_ledger,
        sal_facts_path=args.sal_facts,
        formats=fmts,
        dry_run=args.dry_run,
        output=args.output or None,
        top_n=args.top_n,
    )
