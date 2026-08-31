"""Breadth/depth scheduler for the FF6 mission.

Selects the next work item across all six formats, balancing:
- Unresolved obligations (highest priority)
- Nonpromoting proof (needs test execution to promote)
- Missing evidence freshness (stale hashes)
- Anti-starvation (no format ignored for >N consecutive selections)

Each work item declares its expected measurable product delta.

Usage::

    python -m tools.ff6.scheduler          # print next work item
    python -m tools.ff6.scheduler --all    # print ranked work queue
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.ff6.goal_driver import evaluate, REPO_ROOT, _obligation_total, _reconciliation

HISTORY_PATH = REPO_ROOT / ".local" / "ff6" / "scheduler-history.json"
MAX_CONSECUTIVE_SAME_FORMAT = 3


@dataclass
class WorkItem:
    format_id: str
    category: str
    priority: int
    description: str
    expected_delta: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "format_id": self.format_id,
            "category": self.category,
            "priority": self.priority,
            "description": self.description,
            "expected_delta": self.expected_delta,
            **self.details,
        }


def _load_history() -> dict[str, Any]:
    if HISTORY_PATH.exists():
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    return {"selections": [], "format_counts": {}}


def _consecutive_same_format(history: dict[str, Any], format_id: str) -> int:
    count = 0
    for sel in reversed(history.get("selections", [])):
        if sel.get("format_id") == format_id:
            count += 1
        else:
            break
    return count


def generate_work_items() -> list[WorkItem]:
    """Generate a priority-sorted list of work items across all formats."""
    result = evaluate()
    items: list[WorkItem] = []
    history = _load_history()

    for fmt_state in result["formats"]:
        fid = fmt_state["format_id"]
        total = fmt_state.get("obligations_total")
        unresolved = fmt_state.get("obligations_unresolved")
        certified = fmt_state.get("certified", False)
        recon = fmt_state.get("reconciliation", "NOT_RUN")

        if certified:
            continue

        starvation_penalty = 0
        consecutive = _consecutive_same_format(history, fid)
        if consecutive >= MAX_CONSECUTIVE_SAME_FORMAT:
            starvation_penalty = 50

        if recon == "NOT_RUN":
            items.append(WorkItem(
                format_id=fid,
                category="reconciliation_missing",
                priority=10 + starvation_penalty,
                description=f"Run obligation reconciliation for {fid}",
                expected_delta=f"{fid} reconciliation report created, obligation status classified",
            ))
            continue

        if isinstance(unresolved, int) and unresolved > 0:
            items.append(WorkItem(
                format_id=fid,
                category="unresolved_obligations",
                priority=20 + starvation_penalty,
                description=f"Close {unresolved} unresolved {fid} obligations",
                expected_delta=f"{fid} unresolved count reduced from {unresolved}",
                details={"unresolved": unresolved, "total": total},
            ))

        report = _reconciliation(fid)
        if report:
            proof = report.get("proof_strength", "")
            effect = report.get("promotion_effect", "")
            if "nonpromoting" in str(proof).lower() or effect == "none":
                items.append(WorkItem(
                    format_id=fid,
                    category="proof_promotion",
                    priority=30 + starvation_penalty,
                    description=f"Promote {fid} proof from nonpromoting to promoting",
                    expected_delta=f"{fid} proof_strength changes to promoting, promotion_effect changes to certifiable",
                    details={"current_proof": proof, "current_effect": effect},
                ))

    items.sort(key=lambda w: w.priority)
    return items


def select_next() -> WorkItem | None:
    """Select the single highest-priority work item."""
    items = generate_work_items()
    return items[0] if items else None


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        prog="python -m tools.ff6.scheduler",
        description="FF6 breadth/depth scheduler",
    )
    parser.add_argument("--all", action="store_true", help="Show all work items")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    items = generate_work_items()
    if not items:
        print("No work items — all formats certified or goal achieved.")
        return 0

    if args.json:
        print(json.dumps([w.to_dict() for w in items], indent=2))
        return 0

    if args.all:
        print(f"{'Pri':>3}  {'Format':<12} {'Category':<25} Description")
        print("-" * 80)
        for w in items:
            print(f"{w.priority:>3}  {w.format_id:<12} {w.category:<25} {w.description}")
        return 0

    next_item = items[0]
    print(f"NEXT WORK ITEM")
    print(f"  Format:   {next_item.format_id}")
    print(f"  Category: {next_item.category}")
    print(f"  Priority: {next_item.priority}")
    print(f"  Task:     {next_item.description}")
    print(f"  Delta:    {next_item.expected_delta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
