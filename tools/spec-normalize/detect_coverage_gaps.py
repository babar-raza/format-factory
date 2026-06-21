"""
detect_coverage_gaps.py — Detect spec sections not covered by any requirement pack or verified fact.

format-factory project — Spec Workbench v1
Created: TC-0020 (2026-06-18)

For each normalized spec (sections.jsonl), checks whether each section_id appears in:
  - The workbench's verified facts (section_id field in provenance)
  - Any requirement pack in workbench/requirement-packs/
  - Any task packet in workbench/task-packets/

Sections with no coverage are flagged as gaps. This helps identify where the workbench
needs to be extended before consulting it for gate work.

Usage:
    python detect_coverage_gaps.py --format-id fods --version 1.3
    python detect_coverage_gaps.py --all            # check all formats with sections.jsonl
    python detect_coverage_gaps.py --format-id fods --version 1.3 --json

Output:
    Lists uncovered sections with their titles and page ranges.
    If all sections have coverage: prints "FULL COVERAGE" and exits 0.
    If gaps exist: prints gap table and exits 1.

Local-only: never reads network. Never modifies files.

License: Apache-2.0 (project-owned, format-factory)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _spec_cache_dir(fmt: str, ver: str) -> Path:
    return _repo_root() / ".local" / "spec-cache" / fmt / ver


def _spec_cache_root() -> Path:
    return _repo_root() / ".local" / "spec-cache"


# ---------------------------------------------------------------------------
# Section loading
# ---------------------------------------------------------------------------

def _load_sections(fmt: str, ver: str) -> list[dict[str, Any]]:
    """Load sections from normalized sections.jsonl."""
    path = _spec_cache_dir(fmt, ver) / "normalized" / "sections.jsonl"
    if not path.exists():
        return []
    sections = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    sections.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return sections


# ---------------------------------------------------------------------------
# Covered section IDs from workbench artifacts
# ---------------------------------------------------------------------------

def _collect_covered_ids(workbench_dir: Path) -> set[str]:
    """Collect all section_ids referenced in any workbench artifact."""
    covered: set[str] = set()

    # verified-facts-auto-seed.yaml (JSON/YAML format)
    for fname in ["verified-facts-auto-seed.yaml", "verified-facts-review.yaml"]:
        f = workbench_dir / fname
        if f.exists():
            try:
                import re
                text = f.read_text(encoding="utf-8")
                for m in re.finditer(r'section_id:\s*"?([^"\n,}]+)"?', text):
                    val = m.group(1).strip()
                    if val and val != "null" and val != "None":
                        covered.add(val)
            except Exception:
                pass

    # requirement-packs/
    req_dir = workbench_dir / "requirement-packs"
    if req_dir.exists():
        for rf in req_dir.glob("*.yaml"):
            try:
                import re
                text = rf.read_text(encoding="utf-8")
                for m in re.finditer(r'section_id:\s*"?([^"\n,}]+)"?', text):
                    val = m.group(1).strip()
                    if val and val != "null":
                        covered.add(val)
                # Also grab sections: list entries
                for m in re.finditer(r'sections:\s*\[([^\]]+)\]', text):
                    for sid in m.group(1).split(","):
                        sid = sid.strip().strip('"').strip("'")
                        if sid:
                            covered.add(sid)
            except Exception:
                pass

    # task-packets/
    tp_dir = workbench_dir / "task-packets"
    if tp_dir.exists():
        for tp in tp_dir.glob("*.yaml"):
            try:
                import re
                text = tp.read_text(encoding="utf-8")
                for m in re.finditer(r'section_id:\s*"?([^"\n,}]+)"?', text):
                    val = m.group(1).strip()
                    if val and val != "null":
                        covered.add(val)
            except Exception:
                pass

    return covered


# ---------------------------------------------------------------------------
# Per-format analysis
# ---------------------------------------------------------------------------

def analyze_format(fmt: str, ver: str) -> dict[str, Any]:
    spec_dir = _spec_cache_dir(fmt, ver)
    workbench_dir = spec_dir / "workbench"
    sections = _load_sections(fmt, ver)

    result: dict[str, Any] = {
        "format_id": fmt,
        "version": ver,
        "total_sections": len(sections),
        "covered_count": 0,
        "gap_count": 0,
        "coverage_pct": 0.0,
        "gaps": [],
        "status": "NO_SECTIONS",
    }

    if not sections:
        return result

    if not workbench_dir.exists():
        result["status"] = "NO_WORKBENCH"
        result["gap_count"] = len(sections)
        result["gaps"] = [
            {"section_id": s["section_id"], "title": s.get("title", ""), "pages": f"{s.get('first_page', '?')}-{s.get('last_page', '?')}"}
            for s in sections
        ]
        return result

    covered = _collect_covered_ids(workbench_dir)

    gaps = []
    for s in sections:
        sid = s.get("section_id", "")
        if sid not in covered:
            gaps.append({
                "section_id": sid,
                "title": s.get("title", ""),
                "pages": f"{s.get('first_page', '?')}-{s.get('last_page', '?')}",
            })

    covered_count = len(sections) - len(gaps)
    coverage_pct = (covered_count / len(sections) * 100) if sections else 0.0

    result.update({
        "covered_count": covered_count,
        "gap_count": len(gaps),
        "coverage_pct": round(coverage_pct, 1),
        "gaps": gaps,
        "status": "FULL_COVERAGE" if not gaps else "GAPS_FOUND",
    })
    return result


# ---------------------------------------------------------------------------
# Discover all formats that have sections.jsonl
# ---------------------------------------------------------------------------

def _discover_formats_with_sections() -> list[tuple[str, str]]:
    root = _spec_cache_root()
    if not root.exists():
        return []
    pairs: list[tuple[str, str]] = []
    for fmt_dir in sorted(root.iterdir()):
        if not fmt_dir.is_dir():
            continue
        for ver_dir in sorted(fmt_dir.iterdir()):
            sections_file = ver_dir / "normalized" / "sections.jsonl"
            if sections_file.exists():
                pairs.append((fmt_dir.name, ver_dir.name))
    return pairs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Detect spec sections not covered by workbench artifacts (TC-0020)"
    )
    parser.add_argument("--format-id", help="Format ID (e.g. fods)")
    parser.add_argument("--version", help="Spec version (e.g. 1.3)")
    parser.add_argument("--all", action="store_true",
                        help="Check all formats that have sections.jsonl")
    parser.add_argument("--json", action="store_true", dest="json_out",
                        help="Output machine-readable JSON")
    parser.add_argument("--gaps-only", action="store_true",
                        help="Print only gap entries (suppresses covered sections)")
    args = parser.parse_args(argv)

    if not args.all and not (args.format_id and args.version):
        parser.error("Provide --format-id and --version, or use --all")

    if args.all:
        pairs = _discover_formats_with_sections()
        if not pairs:
            print("No formats with sections.jsonl found.", file=sys.stderr)
            return 2
    else:
        pairs = [(args.format_id, args.version)]

    results = [analyze_format(fmt, ver) for fmt, ver in pairs]

    if args.json_out:
        print(json.dumps(results, indent=2))
        return 1 if any(r["gap_count"] > 0 for r in results) else 0

    # Human-readable output
    has_gaps = False
    for r in results:
        label = f"{r['format_id']}/{r['version']}"
        status = r["status"]
        total = r["total_sections"]
        covered = r["covered_count"]
        pct = r["coverage_pct"]

        if status in ("NO_SECTIONS", "NO_WORKBENCH"):
            print(f"{label}: {status} (total={total})")
            continue

        print(f"\n{label}: {status} — {covered}/{total} sections covered ({pct}%)")

        if r["gaps"]:
            has_gaps = True
            print(f"  {'SECTION_ID':<12} {'PAGES':<12} TITLE")
            print("  " + "-" * 60)
            for gap in r["gaps"]:
                title = gap["title"]
                if len(title) > 40:
                    title = title[:37] + "..."
                print(f"  {gap['section_id']:<12} {gap['pages']:<12} {title}")

    return 1 if has_gaps else 0


if __name__ == "__main__":
    sys.exit(main())
