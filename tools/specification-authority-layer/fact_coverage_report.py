"""
fact_coverage_report.py — Per-format verified fact coverage reporter.

Scans all verified-facts-review.yaml files under .local/spec-cache/ and produces:
  - .local/sal-output/fact-coverage-report.json  (machine-readable)
  - .local/sal-output/fact-coverage-summary.md   (human-readable)

Usage:
    python fact_coverage_report.py [--format <id>] [--json]

Flags:
    --format <id>   Only report one format
    --json          Write JSON summary to stdout instead of files
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SPEC_CACHE = _REPO_ROOT / ".local" / "spec-cache"
_SAL_OUTPUT = _REPO_ROOT / ".local" / "sal-output"

_VERIFIED_STATUSES = frozenset(["verified", "verified_with_note"])
_PENDING_STATUSES = frozenset(["pending_verification", "needs_review"])

# TC-SA-HEAL-007: Infer fact_category from claim_id naming convention.
# FACT-{FORMAT}-EX-* = structural_enumeration (auto-extracted xml element scan)
# All others = behavioral (hand-curated spec requirements)
import re as _re
_EX_PATTERN = _re.compile(r"^FACT-[A-Z]+-EX-", _re.IGNORECASE)


def _infer_fact_category(claim_id: str) -> str:
    """Return 'structural_enumeration' for FACT-*-EX-* ids; else 'behavioral'."""
    if _EX_PATTERN.match(claim_id):
        return "structural_enumeration"
    return "behavioral"


def _count_by_category(facts: list[dict]) -> dict[str, int]:
    """Count verified facts split by behavioral vs structural_enumeration."""
    counts: dict[str, int] = {"behavioral": 0, "structural_enumeration": 0}
    _VERIFIED = frozenset(["verified", "verified_with_note"])
    for fact in facts:
        prov = fact.get("provenance", {}) or {}
        status = prov.get("verification_status") or fact.get("verification_status", "unknown")
        if status not in _VERIFIED:
            continue
        explicit = fact.get("fact_category") or ""
        cat = explicit if explicit in counts else _infer_fact_category(
            fact.get("claim_id") or fact.get("fact_id") or ""
        )
        counts[cat] = counts.get(cat, 0) + 1
    return counts


def _load_review_yaml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("{"):
        return json.loads(text)
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}
    except ImportError:
        raise RuntimeError(f"PyYAML required to parse: {path}")


def _count_by_status(facts: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for fact in facts:
        prov = fact.get("provenance", {}) or {}
        status = prov.get("verification_status") or fact.get("verification_status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _build_format_report(review_file: Path, format_id: str) -> dict:
    data = _load_review_yaml(review_file)
    facts = data.get("facts", [])
    counts = _count_by_status(facts)

    total = len(facts)
    verified = counts.get("verified", 0)
    verified_with_note = counts.get("verified_with_note", 0)
    pending = sum(counts.get(s, 0) for s in _PENDING_STATUSES)
    not_found = counts.get("not_found_in_normalized_text", 0)
    other = total - verified - verified_with_note - pending - not_found

    effective_verified = verified + verified_with_note
    coverage_pct = round(100.0 * effective_verified / total, 1) if total > 0 else 0.0
    cat_counts = _count_by_category(facts)
    behavioral_count = cat_counts["behavioral"]
    structural_count = cat_counts["structural_enumeration"]

    return {
        "format_id": format_id,
        "review_file": str(review_file),
        "total_registered": total,
        "verified": verified,
        "verified_with_note": verified_with_note,
        "effective_verified": effective_verified,
        "pending": pending,
        "not_found_in_normalized_text": not_found,
        "other": other,
        "coverage_percent": coverage_pct,
        "status_breakdown": counts,
        "behavioral_count": behavioral_count,
        "structural_enumeration_count": structural_count,
    }


def generate_report(format_id: str | None = None) -> dict:
    if format_id:
        pattern = f"{format_id.lower()}/*/workbench/verified-facts-review.yaml"
    else:
        pattern = "*/*/workbench/verified-facts-review.yaml"

    review_files = sorted(_SPEC_CACHE.glob(pattern))

    formats = []
    for rf in review_files:
        fmt = rf.parts[-4]  # .local/spec-cache/{format}/{version}/workbench/file
        try:
            formats.append(_build_format_report(rf, fmt))
        except Exception as exc:
            print(f"  [{fmt}] Error reading {rf.name}: {exc}", file=sys.stderr)

    total_registered = sum(f["total_registered"] for f in formats)
    total_verified = sum(f["effective_verified"] for f in formats)
    total_pending = sum(f["pending"] for f in formats)
    total_behavioral = sum(f["behavioral_count"] for f in formats)
    total_structural = sum(f["structural_enumeration_count"] for f in formats)
    formats_with_coverage = sum(1 for f in formats if f["effective_verified"] > 0)
    formats_no_coverage = len(formats) - formats_with_coverage

    return {
        "generated_at": date.today().isoformat(),
        "formats": formats,
        "summary": {
            "total_formats_with_facts": len(formats),
            "total_formats_with_any_coverage": formats_with_coverage,
            "total_formats_no_coverage": formats_no_coverage,
            "total_verified": total_verified,
            "total_pending": total_pending,
            "total_registered": total_registered,
            "overall_coverage_percent": (
                round(100.0 * total_verified / total_registered, 1)
                if total_registered > 0 else 0.0
            ),
            "behavioral_coverage": total_behavioral,
            "structural_enumeration_coverage": total_structural,
        },
    }


def _write_markdown_summary(report: dict, out_path: Path) -> None:
    lines = [
        "# SAL Fact Coverage Summary",
        f"Generated: {report['generated_at']}",
        "",
        "## Per-Format Coverage",
        "",
        "| Format | Verified | Verified+Note | Pending | Not Found | Total | Coverage % |",
        "|--------|----------|---------------|---------|-----------|-------|------------|",
    ]
    for f in report["formats"]:
        lines.append(
            f"| {f['format_id']} | {f['verified']} | {f['verified_with_note']} | "
            f"{f['pending']} | {f['not_found_in_normalized_text']} | "
            f"{f['total_registered']} | {f['coverage_percent']}% |"
        )
    s = report["summary"]
    lines += [
        "",
        "## Summary",
        f"- Total formats with facts: {s['total_formats_with_facts']}",
        f"- Formats with any coverage: {s['total_formats_with_any_coverage']}",
        f"- Total verified (effective): {s['total_verified']}",
        f"- Total pending: {s['total_pending']}",
        f"- Total registered: {s['total_registered']}",
        f"- Overall coverage: {s['overall_coverage_percent']}%",
        f"- Behavioral coverage: {s['behavioral_coverage']} (hand-curated spec requirements)",
        f"- Structural enumeration coverage: {s['structural_enumeration_coverage']} (auto-extracted FACT-*-EX-* ids)",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="SAL fact coverage reporter")
    parser.add_argument("--format", dest="format_id", help="Only report one format")
    parser.add_argument("--json", action="store_true", help="Write JSON to stdout")
    args = parser.parse_args()

    report = generate_report(args.format_id)

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    _SAL_OUTPUT.mkdir(parents=True, exist_ok=True)

    json_path = _SAL_OUTPUT / "fact-coverage-report.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Report: {json_path}", file=sys.stderr)

    md_path = _SAL_OUTPUT / "fact-coverage-summary.md"
    _write_markdown_summary(report, md_path)
    print(f"Summary: {md_path}", file=sys.stderr)

    s = report["summary"]
    print(
        f"\nTotal: {s['total_verified']} verified / {s['total_registered']} registered "
        f"({s['overall_coverage_percent']}% coverage)",
        file=sys.stderr,
    )
    for f in report["formats"]:
        print(
            f"  [{f['format_id']}] {f['effective_verified']}/{f['total_registered']} "
            f"({f['coverage_percent']}%) — {f['pending']} pending",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
