#!/usr/bin/env python3
"""
backfill_gap_spec_fact_refs.py — Backfill gap-ledger entries with spec_facts from sal-facts.

Strategy: for each gap entry missing spec_facts, assign the top-N verified fact IDs
from sal-facts-latest.json for the matching format.

Idempotent: skips gaps that already have non-empty spec_facts.
"""
import hashlib
import json
import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent.parent


def _get_head_sha256(gap_path: Path) -> str | None:
    """Return SHA256 of gap-ledger at HEAD, or None if unavailable."""
    try:
        rel = gap_path.relative_to(REPO)
    except ValueError:
        return None
    try:
        blob = subprocess.run(
            ["git", "show", f"HEAD:{rel.as_posix()}"],
            capture_output=True,
            cwd=str(REPO),
            timeout=10,
        )
        if blob.returncode != 0:
            return None
        return hashlib.sha256(blob.stdout).hexdigest()
    except Exception:
        return None


def _check_working_tree_vs_head(gap_path: Path, force_from_stale: bool) -> None:
    """TC-POST-GAP-GUARD-001: Warn/error if working tree gap-ledger differs from HEAD.

    When another session has uncommitted changes in the working tree, the backfill
    would silently operate on stale data. This guard detects the divergence and
    requires --force-from-stale to proceed.
    """
    head_sha = _get_head_sha256(gap_path)
    if head_sha is None:
        return  # Can't compare — allow proceed (git unavailable or new file)
    wt_sha = hashlib.sha256(gap_path.read_bytes()).hexdigest()
    if head_sha == wt_sha:
        return  # Clean — working tree matches HEAD
    msg = (
        f"GAP-GUARD: working tree gap-ledger differs from HEAD.\n"
        f"  HEAD SHA256:         {head_sha}\n"
        f"  Working tree SHA256: {wt_sha}\n"
        f"  Another session may have uncommitted changes.\n"
        f"  Re-read gap-ledger from HEAD or pass --force-from-stale to proceed anyway."
    )
    if force_from_stale:
        print(f"WARNING: {msg}", file=sys.stderr)
    else:
        print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(2)


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


def _keyword_match_facts(
    gap: dict,
    all_facts: list,
    top_n: int = 10,
) -> list:
    """TC-SAL-CARRY-BACKFILL-001: Match facts to a gap by keyword relevance.

    Extracts keywords from the gap's gap_id, title, and description.
    Scores each fact by how many keywords appear in its description/claim text.
    Returns top-n best-scoring facts, or empty list if no match.
    """
    import re

    # Extract keywords from gap metadata
    text_sources = [
        gap.get("gap_id", ""),
        gap.get("title", ""),
        gap.get("description", ""),
        gap.get("capability_name", ""),
    ]
    raw = " ".join(str(s) for s in text_sources if s)
    # Split on non-alpha, lowercase, filter short words
    tokens = re.split(r"[^a-zA-Z]+", raw.lower())
    keywords = {t for t in tokens if len(t) >= 4 and t not in {
        "with", "from", "that", "this", "have", "when", "then", "also",
        "must", "should", "will", "format", "fods", "fodt", "foss"
    }}

    if not keywords:
        return []

    scored = []
    for fact in all_facts:
        desc = (fact.get("description", "") or fact.get("claim", "")).lower()
        score = sum(1 for kw in keywords if kw in desc)
        if score > 0:
            scored.append((score, fact.get("qname", "")))

    scored.sort(key=lambda x: -x[0])
    matched_ids = [qname for _, qname in scored[:top_n] if qname]
    return matched_ids


def _load_sal_facts_with_objects(sal_facts_path: Path) -> dict:
    """Build format -> [fact_objects] index (full dict, not just IDs) for semantic matching."""
    sal = json.loads(sal_facts_path.read_text(encoding="utf-8", errors="replace"))
    results = sal.get("results", [])
    format_facts: dict = {}
    for r in results:
        fmt = r.get("format_id", "").lower().replace("-", "_")
        facts = r.get("spec_facts", [])
        verified = [f for f in facts if f.get("qname") and f.get("fact_status") == "verified"]
        if fmt and verified:
            format_facts[fmt] = verified
    return format_facts


def backfill(
    gap_ledger_path: str,
    sal_facts_path: str,
    formats: list,
    dry_run: bool,
    output: str | None,
    top_n: int = 10,
    semantic_match: bool = False,
    force_overwrite: bool = False,
    force_from_stale: bool = False,
) -> dict:
    gap_path = Path(gap_ledger_path)
    sal_path = Path(sal_facts_path)

    if not gap_path.exists():
        print(f"ERROR: gap-ledger not found: {gap_path}", file=sys.stderr)
        sys.exit(1)
    if not sal_path.exists():
        print(f"ERROR: sal-facts not found: {sal_path}", file=sys.stderr)
        sys.exit(1)

    if not dry_run:
        _check_working_tree_vs_head(gap_path, force_from_stale)

    gaps_data = json.loads(gap_path.read_text(encoding="utf-8", errors="replace"))
    format_facts = _load_sal_facts(sal_path)
    format_facts_obj = _load_sal_facts_with_objects(sal_path) if semantic_match else {}

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

        # Skip already populated (unless --force-overwrite)
        if gap.get("spec_facts") and len(gap.get("spec_facts", [])) > 0:
            if not force_overwrite:
                skipped_has_facts += 1
                continue

        # Look up SAL facts for this format
        sal_facts_for_fmt = format_facts.get(gap_fmt)
        if not sal_facts_for_fmt:
            skipped_no_sal += 1
            continue

        # Assign top N facts (or keyword-matched if --semantic-match)
        if semantic_match:
            all_format_facts_obj = format_facts_obj.get(gap_fmt, [])
            assigned = _keyword_match_facts(gap, all_format_facts_obj, top_n=top_n)
            if not assigned:
                # Fallback to top-N if no keyword match
                assigned = sal_facts_for_fmt[:top_n]
        else:
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
    parser.add_argument(
        "--semantic-match",
        action="store_true",
        help="TC-SAL-CARRY-BACKFILL-001: match facts to gaps by keyword relevance rather than top-N"
    )
    parser.add_argument(
        "--force-overwrite",
        action="store_true",
        help="Overwrite existing spec_facts (default: skip already-populated gaps)"
    )
    parser.add_argument(
        "--force-from-stale",
        action="store_true",
        help="TC-POST-GAP-GUARD-001: proceed even if working tree gap-ledger differs from HEAD (prints WARNING instead of ERROR)"
    )

    args = parser.parse_args()
    fmts = [f.strip() for f in args.formats.split(",") if f.strip()] if args.formats else []

    backfill(
        gap_ledger_path=args.gap_ledger,
        sal_facts_path=args.sal_facts,
        formats=fmts,
        dry_run=args.dry_run,
        output=args.output or None,
        top_n=args.top_n,
        semantic_match=args.semantic_match,
        force_overwrite=args.force_overwrite,
        force_from_stale=args.force_from_stale,
    )
