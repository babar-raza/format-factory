"""
merge_sal_facts.py — Merge per-format sal-facts files into the combined sal-facts-latest.json.

TC-LA-001: SAL ingestion for formats with existing spec-cache content.

For each per-format sal-facts file in .local/spec-cache/, if it contains more
spec_facts than the current combined database entry for that format, the combined
database is updated.

Only merges if per-format file has MORE facts (never downgrade the combined DB).
Does not overwrite if combined already has equal or more facts for that format.

Usage:
    python tools/spec/merge_sal_facts.py [--dry-run] [--formats csv,toml,abw]

Exit codes:
    0 — success (may have merged zero or more formats)
    1 — error reading/writing files
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_SPEC_CACHE = _REPO / ".local" / "spec-cache"
_COMBINED = _SPEC_CACHE / "sal-facts-latest.json"

# Known filename variations for per-format files
_FORMAT_FILE_CANDIDATES = {
    "csv": ["sal-facts-CSV.json", "sal-facts-csv.json"],
    "tsv": ["sal-facts-tsv.json"],
    "toml": ["sal-facts-toml.json"],
    "abw": ["sal-facts-abw.json"],
    "dif": ["sal-facts-dif.json"],
    "gnumeric": ["sal-facts-gnumeric.json"],
    "sylk": ["sal-facts-sylk.json"],
    "ndjson": ["sal-facts-ndjson.json"],
    "xcf": ["sal-facts-xcf.json"],
    "zst": ["sal-facts-zst.json"],
    "qoi": ["sal-facts-qoi.json"],
    "pbm": ["sal-facts-pbm.json"],
    "pgm": ["sal-facts-pgm.json"],
    "ppm": ["sal-facts-ppm.json"],
}


def _find_per_format_file(format_id: str) -> Path | None:
    for candidate in _FORMAT_FILE_CANDIDATES.get(format_id, [f"sal-facts-{format_id}.json"]):
        p = _SPEC_CACHE / candidate
        if p.exists():
            return p
    return None


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_fact(fact: dict) -> dict:
    """Ensure fact has required fields, normalizing schema variants.

    Some per-format files use 'description' instead of 'claim' — normalize to 'claim'.
    The 'qname' field must be present and match FACT-FORMAT-NNN pattern.
    """
    fact = dict(fact)
    # Normalize: use 'description' as 'claim' fallback
    if "claim" not in fact and "description" in fact:
        fact["claim"] = fact["description"]
    required = ("qname", "claim")
    for field in required:
        if field not in fact:
            raise ValueError(f"Fact missing required field '{field}': {fact}")
    return fact


def merge_formats(
    formats: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    """
    Merge per-format sal-facts files into the combined database.

    Returns a summary dict with keys: merged, skipped, errors, total_facts_before, total_facts_after.
    """
    if not _COMBINED.exists():
        raise FileNotFoundError(f"Combined sal-facts database not found: {_COMBINED}")

    combined = _load_json(_COMBINED)
    results: list[dict] = combined.get("results", [])

    # Build index: format_id -> index in results list
    results_index: dict[str, int] = {}
    for i, entry in enumerate(results):
        results_index[entry["format_id"]] = i

    total_before = sum(len(e.get("spec_facts", [])) for e in results)

    formats_to_check = formats or list(_FORMAT_FILE_CANDIDATES.keys())
    summary = {"merged": [], "skipped": [], "errors": [], "total_facts_before": total_before, "total_facts_after": 0}

    for fmt_id in formats_to_check:
        per_format_path = _find_per_format_file(fmt_id)
        if per_format_path is None:
            summary["skipped"].append({"format_id": fmt_id, "reason": "no_per_format_file"})
            continue

        try:
            per_fmt_data = _load_json(per_format_path)
        except Exception as exc:
            summary["errors"].append({"format_id": fmt_id, "reason": f"parse_error: {exc}"})
            continue

        per_fmt_facts = per_fmt_data.get("spec_facts", [])
        if not per_fmt_facts:
            summary["skipped"].append({"format_id": fmt_id, "reason": "no_facts_in_per_format_file"})
            continue

        # Validate all facts have required fields
        try:
            per_fmt_facts = [_normalize_fact(f) for f in per_fmt_facts]
        except ValueError as exc:
            summary["errors"].append({"format_id": fmt_id, "reason": f"invalid_fact: {exc}"})
            continue

        current_count = 0
        existing_idx = results_index.get(fmt_id)
        if existing_idx is not None:
            current_count = len(results[existing_idx].get("spec_facts", []))

        if len(per_fmt_facts) <= current_count:
            summary["skipped"].append({
                "format_id": fmt_id,
                "reason": "combined_already_has_equal_or_more_facts",
                "combined_count": current_count,
                "per_format_count": len(per_fmt_facts),
            })
            continue

        # Merge: update or insert the format entry in results
        new_entry: dict = {
            "format_id": fmt_id,
            "display_name": per_fmt_data.get("display_name", fmt_id.upper()),
            "spec_body": per_fmt_data.get("spec_body", per_fmt_data.get("spec_source", "")),
            "spec_version": per_fmt_data.get("spec_version", ""),
            "spec_url": per_fmt_data.get("spec_url", ""),
            "spec_facts": per_fmt_facts,
        }

        if not dry_run:
            if existing_idx is not None:
                results[existing_idx] = new_entry
            else:
                results.append(new_entry)
                results_index[fmt_id] = len(results) - 1

        summary["merged"].append({
            "format_id": fmt_id,
            "facts_before": current_count,
            "facts_after": len(per_fmt_facts),
            "per_format_file": str(per_format_path.name),
        })

    if not dry_run:
        # Update combined database
        combined["results"] = results
        total_after = sum(len(e.get("spec_facts", [])) for e in results)
        combined["spec_facts_total"] = total_after
        combined["formats_processed"] = len(results)
        combined["generated_at"] = datetime.now(timezone.utc).isoformat()
        combined["generator"] = "merge_sal_facts.py (TC-LA-001)"
        _COMBINED.write_text(json.dumps(combined, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        summary["total_facts_after"] = total_after
    else:
        summary["total_facts_after"] = total_before

    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Merge per-format sal-facts files into sal-facts-latest.json"
    )
    parser.add_argument(
        "--formats",
        help="Comma-separated list of format IDs to merge (default: all known)",
        default=None,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be merged without writing changes",
    )
    args = parser.parse_args(argv)

    formats = [f.strip() for f in args.formats.split(",")] if args.formats else None

    try:
        result = merge_formats(formats=formats, dry_run=args.dry_run)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"{'DRY RUN — ' if args.dry_run else ''}SAL facts merge complete")
    print(f"  Facts before: {result['total_facts_before']}")
    print(f"  Facts after:  {result['total_facts_after']}")
    print(f"  Merged: {len(result['merged'])} format(s)")
    for m in result["merged"]:
        print(f"    {m['format_id']}: {m['facts_before']} -> {m['facts_after']} facts (from {m['per_format_file']})")
    if result["skipped"]:
        print(f"  Skipped: {len(result['skipped'])} format(s)")
        for s in result["skipped"]:
            print(f"    {s['format_id']}: {s['reason']}")
    if result["errors"]:
        print(f"  ERRORS: {len(result['errors'])}")
        for e in result["errors"]:
            print(f"    {e['format_id']}: {e['reason']}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
