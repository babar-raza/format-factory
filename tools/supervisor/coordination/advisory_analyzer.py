"""advisory_analyzer.py — SFC-GAP-C (2026-07-17): observe-only would-block analyzer.

gate.py's `_advisory()` has always been write-only: every advisory-mode event
(coordination or, since Gap C, skill_resolution) is appended to
`<coord-root>/advisory-log.jsonl`, and nothing in this codebase ever read it
back. There is currently ZERO incident-rate data anywhere for a would-be
`enforcing` promotion decision -- this module exists to produce that evidence
BEFORE any promotion, rather than promoting on a "looks fine" guess.

This module is intentionally READ-ONLY and OBSERVE-ONLY: it never calls
set_check_mode, never recommends a specific promotion threshold (there is no
real traffic-volume baseline yet to calibrate one against), and never takes
automatic action. Promotion stays a deliberate, evidence-reviewed,
human/governed-skill decision (docs/governance/skill-only-policy.yaml EP-013
Gap C design: "no automatic rollback on day one" applies symmetrically to
promotion too).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SAMPLE_LIMIT = 10


def _parse_ts(raw: Any) -> "datetime | None":
    if not isinstance(raw, str):
        return None
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def analyze(root: Path, check_id: str,
           window_hours: "float | None" = None) -> dict[str, Any]:
    """Read advisory-log.jsonl filtered to `check == check_id`. Returns total
    events, would-block count/rate, a tier breakdown, a bounded sample of
    would-block events, and distinct agents/paths affected.

    A missing log file is a valid, common state (no events yet) -- returns an
    empty-but-well-formed report, not an error; this module has nothing to
    promote/demote and must never be mistaken for a config/registry loader
    that should fail closed on absence.
    """
    log_path = root / "advisory-log.jsonl"
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=window_hours)
             if window_hours else None)

    events: list[dict] = []
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if not isinstance(rec, dict) or rec.get("check") != check_id:
                continue
            if cutoff is not None:
                ts = _parse_ts(rec.get("ts"))
                if ts is not None and ts < cutoff:
                    continue
            events.append(rec)

    total = len(events)
    would_block = [e for e in events if e.get("would_block")]
    tier_counts = Counter(e.get("tier", "UNKNOWN") for e in would_block)
    agents = {e.get("agent") for e in events if e.get("agent")}
    paths = {e.get("file") for e in events if e.get("file")}

    return {
        "check_id": check_id,
        "window_hours": window_hours,
        "total_events": total,
        "would_block_count": len(would_block),
        "would_block_rate": (len(would_block) / total) if total else None,
        "tier_breakdown": dict(tier_counts),
        "distinct_agents": len(agents),
        "distinct_paths": len(paths),
        "sample_would_block_events": would_block[-SAMPLE_LIMIT:],
        "note": (
            "Observe-only. No promotion/rollback recommendation is computed "
            "here -- review this evidence and use "
            "`python -m tools.supervisor.coordination check-mode set` "
            "as a deliberate, separate, attributed decision."
        ),
    }


def _main(argv=None) -> int:
    from .root import resolve_coordination_root

    ap = argparse.ArgumentParser(description="SFC-GAP-C advisory-log analyzer")
    ap.add_argument("--check", required=True, help="check_id to filter (e.g. skill_resolution)")
    ap.add_argument("--root", default=None)
    ap.add_argument("--window-hours", type=float, default=None)
    args = ap.parse_args(argv)

    root = Path(args.root) if args.root else resolve_coordination_root()
    report = analyze(root, args.check, args.window_hours)
    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
