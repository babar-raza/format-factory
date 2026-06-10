"""autonomy_route_ledger.py — Route decision audit trail.

Writes JSONL records of route decisions for traceability.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.supervisor.autonomy_route_models import ROUTE_DECISIONS_DIR

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LEDGER_PATH = _REPO_ROOT / ROUTE_DECISIONS_DIR / "route-ledger.jsonl"


def append_decision(decision: dict[str, Any]) -> None:
    """Append a route decision record to the JSONL ledger."""
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "decision_id": decision.get("task_id", ""),
        "task_id": decision.get("task_id", ""),
        "task_category": decision.get("task_category", ""),
        "final_route": decision.get("final_route", ""),
        "autonomous_allowed": decision.get("autonomous_allowed", False),
        "blocked": decision.get("blocked", False),
        "reason": decision.get("reason", ""),
        "timestamp": decision.get("timestamp", datetime.now(timezone.utc).isoformat()),
    }
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def read_ledger() -> list[dict[str, Any]]:
    """Read all decisions from the JSONL ledger."""
    if not LEDGER_PATH.exists():
        return []
    records = []
    for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return records


def get_decision_summary() -> dict[str, Any]:
    """Return summary counts by final_route and task_category."""
    records = read_ledger()
    by_route: dict[str, int] = {}
    by_category: dict[str, int] = {}
    for r in records:
        route = r.get("final_route", "UNKNOWN")
        by_route[route] = by_route.get(route, 0) + 1
        cat = r.get("task_category", "UNKNOWN")
        by_category[cat] = by_category.get(cat, 0) + 1
    return {
        "total": len(records),
        "by_route": by_route,
        "by_category": by_category,
    }
