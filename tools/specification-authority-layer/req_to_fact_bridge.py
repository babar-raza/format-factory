"""
req_to_fact_bridge.py — TC-SAL-CARRY-WIRE-006: Context Pack to SAL Fact Bridge.

Reads context packs from reports/specification-authority-layer-mwp/context-pack-sample/
and cross-references their requirement_summary entries against sal-facts-latest.json.

Context packs use FACT-* IDs in requirement_summary. This bridge verifies coverage:
  - how many CP fact IDs exist in SAL
  - which are missing
  - coverage % per format

Output: context_pack_fact_coverage.json per format (in .local/sal-artifacts/)

Usage:
    python req_to_fact_bridge.py --format fods
    python req_to_fact_bridge.py --all
    python req_to_fact_bridge.py --all --output-dir .local/sal-artifacts/
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_HERE = Path(__file__).parent
_REPO_ROOT = _HERE.parent.parent
_CP_DIR = _REPO_ROOT / "reports" / "specification-authority-layer-mwp" / "context-pack-sample"
_SAL_FACTS = _REPO_ROOT / ".local" / "sal-output" / "sal-facts-latest.json"
_DEFAULT_OUTPUT_DIR = _REPO_ROOT / ".local" / "sal-artifacts"


def _load_sal_qnames() -> set:
    """Load all fact qnames from sal-facts-latest.json."""
    if not _SAL_FACTS.exists():
        return set()
    try:
        d = json.loads(_SAL_FACTS.read_text(encoding="utf-8", errors="replace"))
        qnames = set()
        for r in d.get("results", []):
            for f in r.get("spec_facts", []):
                q = f.get("qname", "")
                if q:
                    qnames.add(q)
        return qnames
    except Exception as exc:
        print(f"[req_to_fact_bridge] WARN: could not load sal-facts: {exc}", file=sys.stderr)
        return set()


def _load_sal_by_format() -> Dict[str, set]:
    """Load fact qnames indexed by format_id."""
    if not _SAL_FACTS.exists():
        return {}
    try:
        d = json.loads(_SAL_FACTS.read_text(encoding="utf-8", errors="replace"))
        by_format: Dict[str, set] = {}
        for r in d.get("results", []):
            fid = r.get("format_id", "").lower()
            qnames = set(f.get("qname", "") for f in r.get("spec_facts", []) if f.get("qname"))
            by_format[fid] = qnames
        return by_format
    except Exception:
        return {}


def build_coverage(format_id: str, sal_all_qnames: set, sal_by_format: Dict[str, set]) -> Dict[str, Any]:
    """
    Build coverage report for a single format's context pack.

    Returns dict with coverage stats and matched/unmatched IDs.
    """
    cp_path = _CP_DIR / f"{format_id.lower()}-context-pack.json"
    if not cp_path.exists():
        return {
            "format_id": format_id,
            "status": "NO_CONTEXT_PACK",
            "cp_fact_count": 0,
            "matched_count": 0,
            "unmatched_count": 0,
            "coverage_pct": 0.0,
            "matched_ids": [],
            "unmatched_ids": [],
        }

    try:
        cp = json.loads(cp_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"format_id": format_id, "status": "LOAD_ERROR", "error": str(exc)}

    req_summary = cp.get("requirement_summary", [])
    cp_ids = [r.get("req_id", "") for r in req_summary if r.get("req_id")]

    if not cp_ids:
        return {
            "format_id": format_id,
            "status": "EMPTY_REQUIREMENT_SUMMARY",
            "cp_fact_count": 0,
            "matched_count": 0,
            "unmatched_count": 0,
            "coverage_pct": 0.0,
            "matched_ids": [],
            "unmatched_ids": [],
        }

    cp_id_set = set(cp_ids)
    # Match against all SAL qnames (cross-format — context pack IDs may use FACT-{FORMAT}-NNN)
    matched = sorted(cp_id_set & sal_all_qnames)
    unmatched = sorted(cp_id_set - sal_all_qnames)
    total = len(cp_id_set)
    coverage = round(100.0 * len(matched) / total, 1) if total else 0.0

    # Also check format-specific qnames
    format_qnames = sal_by_format.get(format_id.lower(), set())
    format_matched = sorted(cp_id_set & format_qnames)

    return {
        "format_id": format_id,
        "status": "COVERAGE_COMPUTED",
        "cp_fact_count": total,
        "matched_count": len(matched),
        "unmatched_count": len(unmatched),
        "coverage_pct": coverage,
        "matched_ids": matched[:50],  # cap at 50 for readability
        "unmatched_ids": unmatched[:20],
        "format_specific_matched": len(format_matched),
    }


def run_bridge(
    formats: Optional[List[str]] = None,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Run the REQ-to-FACT bridge for one or more formats.

    Args:
        formats: list of format IDs (None = auto-discover from context pack dir)
        output_dir: directory to write output (None = .local/sal-artifacts/)

    Returns:
        dict with keys: formats_processed, total_coverage_pct, results, output_path
    """
    output_dir = Path(output_dir) if output_dir else _DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load SAL qnames once
    sal_all = _load_sal_qnames()
    sal_by_fmt = _load_sal_by_format()
    print(f"[req_to_fact_bridge] Loaded {len(sal_all)} SAL qnames", file=sys.stderr)

    # Discover formats from context pack directory
    if formats:
        fmt_list = [f.lower() for f in formats]
    else:
        cp_files = list(_CP_DIR.glob("*-context-pack.json"))
        fmt_list = [f.stem.replace("-context-pack", "") for f in cp_files]

    results = []
    for fmt in fmt_list:
        cov = build_coverage(fmt, sal_all, sal_by_fmt)
        results.append(cov)

        # Write per-format output
        per_fmt_path = output_dir / f"context_pack_fact_coverage-{fmt}.json"
        per_fmt_path.write_text(json.dumps(cov, indent=2), encoding="utf-8")
        pct = cov.get("coverage_pct", 0.0)
        total = cov.get("cp_fact_count", 0)
        matched = cov.get("matched_count", 0)
        print(
            f"[req_to_fact_bridge] {fmt}: {matched}/{total} CP IDs matched in SAL ({pct}%)",
            file=sys.stderr,
        )

    # Compute aggregate
    with_facts = [r for r in results if r.get("cp_fact_count", 0) > 0]
    avg_pct = round(sum(r.get("coverage_pct", 0) for r in with_facts) / len(with_facts), 1) if with_facts else 0.0

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "req_to_fact_bridge.py v1.0",
        "formats_processed": len(results),
        "formats_with_context_packs": len(with_facts),
        "avg_coverage_pct": avg_pct,
        "results": results,
    }

    out_path = output_dir / "context_pack_fact_coverage-all.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    summary["output_path"] = str(out_path)

    print(f"[req_to_fact_bridge] Average coverage: {avg_pct}% across {len(with_facts)} formats with CPs")
    return summary


def _cli() -> int:
    parser = argparse.ArgumentParser(
        description="REQ-to-FACT Bridge — verify context pack coverage against SAL facts"
    )
    parser.add_argument("--format", help="Format ID (e.g. fods)")
    parser.add_argument("--all", action="store_true", help="Process all discovered context packs")
    parser.add_argument(
        "--output-dir",
        default=str(_DEFAULT_OUTPUT_DIR),
        help="Directory to write coverage JSON files",
    )
    args = parser.parse_args()

    formats = None
    if args.format:
        formats = [args.format]
    elif not args.all:
        formats = None  # default: all

    result = run_bridge(formats=formats, output_dir=Path(args.output_dir))
    print(f"Processed {result['formats_processed']} formats")
    print(f"Average coverage: {result['avg_coverage_pct']}%")
    print(f"Output: {result['output_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
