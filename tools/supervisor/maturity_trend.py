"""maturity_trend.py — Sprint maturity trend extractor.

Reads reports/supervisor/grading-history.jsonl and produces
reports/supervisor/maturity-trend.json with per-sprint quality metrics.

Usage:
    python tools/supervisor/maturity_trend.py
    python tools/supervisor/maturity_trend.py --last 20
    python tools/supervisor/maturity_trend.py --output /path/to/output.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_INPUT = REPO_ROOT / "reports" / "supervisor" / "grading-history.jsonl"
DEFAULT_OUTPUT = REPO_ROOT / "reports" / "supervisor" / "maturity-trend.json"


def _verdict_score(verdict: str) -> float:
    """Numeric quality score for a verdict string."""
    mapping = {
        "ACCEPTED_VERIFIED": 1.0,
        "ACCEPTED": 0.85,
        "UNVERIFIED": 0.70,
        "ACCEPTED_WITH_REWORK": 0.65,
        "ACCEPTED_WITH_WARNINGS": 0.70,
        "CONDITIONAL_PASS": 0.60,
        "REWORK_REQUIRED": 0.30,
        "REJECTED": 0.10,
        "EVIDENCE_QUALITY_ZERO": 0.05,
        "NO_ITEMS_DECLARED": 0.0,
    }
    return mapping.get(verdict.upper().replace(" ", "_"), 0.50)


def load_history(path: Path, last: int | None = None) -> list[dict]:
    """Load JSONL grading history; optionally limit to the last N sprints."""
    if not path.exists():
        return []
    entries = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    if last is not None:
        entries = entries[-last:]
    return entries


def compute_trend(entries: list[dict]) -> list[dict]:
    """Compute per-sprint maturity metrics from grading history entries."""
    sprints: list[dict] = []
    for i, e in enumerate(entries):
        verdict = e.get("verdict", "UNKNOWN")
        rework_items = e.get("rework_items", [])
        rework_count = e.get("rework_count", len(rework_items))
        accepted_count = e.get("accepted_count", 0)
        overclaimed_count = e.get("overclaimed_count", 0)
        total_items = accepted_count + rework_count + overclaimed_count
        sprint: dict = {
            "index": i,
            "sprint_id": e.get("sprint_id", "unknown"),
            "run_id": e.get("run_id"),
            "timestamp": e.get("timestamp"),
            "verdict": verdict,
            "evidence_quality_score": _verdict_score(verdict),
            "accepted_count": accepted_count,
            "rework_count": rework_count,
            "overclaimed_count": overclaimed_count,
            "total_items": total_items,
            "accepted_verified_ratio": (
                accepted_count / total_items if total_items > 0 else 1.0
            ),
            "rework_rate": (
                rework_count / total_items if total_items > 0 else 0.0
            ),
            "overclaim_rate": (
                overclaimed_count / total_items if total_items > 0 else 0.0
            ),
            "continuation_state": e.get("continuation_state", False),
            "exit_code": e.get("exit_code", -1),
            "has_govblock": any(
                "GOV_BLOCK" in str(r) for r in rework_items
            ),
            "govblock_items": [r for r in rework_items if "GOV_BLOCK" in str(r)],
        }
        sprints.append(sprint)
    return sprints


def compute_summary(sprints: list[dict]) -> dict:
    """Compute aggregate summary statistics over all sprints."""
    if not sprints:
        return {}
    n = len(sprints)
    verdicts = Counter(s["verdict"] for s in sprints)
    avg_quality = sum(s["evidence_quality_score"] for s in sprints) / n
    avg_rework = sum(s["rework_rate"] for s in sprints) / n
    avg_accepted_ratio = sum(s["accepted_verified_ratio"] for s in sprints) / n
    govblock_count = sum(1 for s in sprints if s["has_govblock"])
    recent_5 = sprints[-5:] if len(sprints) >= 5 else sprints
    recent_quality = (
        sum(s["evidence_quality_score"] for s in recent_5) / len(recent_5)
        if recent_5 else 0.0
    )
    return {
        "sprint_count": n,
        "verdict_distribution": dict(verdicts),
        "avg_evidence_quality_score": round(avg_quality, 3),
        "avg_rework_rate": round(avg_rework, 3),
        "avg_accepted_verified_ratio": round(avg_accepted_ratio, 3),
        "govblock_sprint_count": govblock_count,
        "govblock_rate": round(govblock_count / n, 3),
        "recent_5_avg_quality": round(recent_quality, 3),
        "trend_direction": (
            "improving" if recent_quality > avg_quality + 0.05
            else "declining" if recent_quality < avg_quality - 0.05
            else "stable"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sprint maturity trend extractor")
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help=f"Input JSONL path (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Output JSON path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--last",
        type=int,
        default=None,
        help="Limit to last N sprints",
    )
    parser.add_argument(
        "--print",
        action="store_true",
        dest="print_output",
        help="Print output to stdout instead of writing to file",
    )
    args = parser.parse_args(argv)

    entries = load_history(Path(args.input), last=args.last)
    if not entries:
        print(f"WARNING: No entries found in {args.input}", file=sys.stderr)
        return 1

    sprints = compute_trend(entries)
    summary = compute_summary(sprints)
    output = {
        "schema_version": "1.0",
        "generated_from": args.input,
        "sprint_count": len(sprints),
        "summary": summary,
        "sprints": sprints,
    }

    if args.print_output:
        print(json.dumps(output, indent=2))
    else:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
        print(f"Maturity trend written: {out_path}")
        print(f"  Sprints: {len(sprints)}, avg quality: {summary.get('avg_evidence_quality_score')}, trend: {summary.get('trend_direction')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
