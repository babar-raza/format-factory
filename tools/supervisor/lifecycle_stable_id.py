"""
lifecycle_stable_id.py — Reads machinery plan Taskcard Status Table to detect pre-closed IDs.
Prevents duplicate work on rerun. Read-only utility; makes no writes.
"""
from pathlib import Path
import json


def get_closed_taskcard_ids(plan_path: str) -> set:
    """Return set of taskcard IDs that are CLOSED in the plan's Taskcard Status Table."""
    plan_file = Path(plan_path)
    if not plan_file.exists():
        return set()
    closed = set()
    in_table = False
    for line in plan_file.read_text(encoding="utf-8").splitlines():
        if "| Taskcard | Status |" in line:
            in_table = True
            continue
        if in_table and line.startswith("|") and "---" not in line:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2 and parts[1].upper() == "CLOSED":
                closed.add(parts[0])
        elif in_table and not line.startswith("|"):
            in_table = False
    return closed


def report_idempotency(plan_path: str) -> dict:
    closed = get_closed_taskcard_ids(plan_path)
    return {
        "closed_count": len(closed),
        "closed_ids": sorted(closed),
        "verdict": "FIRST_RUN" if not closed else "HAS_PRIOR_CLOSED_TASKCARDS",
    }


if __name__ == "__main__":
    import sys
    plan = sys.argv[1] if len(sys.argv) > 1 else "plans/.claude/velvet-swinging-wreath.md"
    print(json.dumps(report_idempotency(plan), indent=2))
