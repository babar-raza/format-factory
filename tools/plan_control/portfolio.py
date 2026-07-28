from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


_DISPOSITIONS = {"LINKED", "COMPLETE", "CANCELLED", "ALREADY_SATISFIED", "STILL_OPEN"}


def _validated_disposition(task: dict[str, Any]) -> tuple[str, str | None]:
    raw = str(task.get("disposition") or "").upper()
    if raw not in _DISPOSITIONS:
        return "STILL_OPEN", "MISSING_OR_UNKNOWN_DISPOSITION"
    if raw == "LINKED" and not task.get("canonical_task_id"):
        return "STILL_OPEN", "LINKED_WITHOUT_CANONICAL_TASK"
    if raw in {"COMPLETE", "ALREADY_SATISFIED"} and not re.fullmatch(
        r"[a-fA-F0-9]{64}", str(task.get("evidence_digest") or "")
    ):
        return "STILL_OPEN", f"{raw}_WITHOUT_EVIDENCE"
    authority = str(task.get("cancellation_authority") or "")
    if raw == "CANCELLED" and not re.fullmatch(
        r"(?:decision|record|delegation):\S+", authority
    ):
        return "STILL_OPEN", "CANCELLED_WITHOUT_AUTHORITY"
    return raw, None


def read_source_items(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    document = json.loads(path.read_text(encoding="utf-8"))
    items: list[dict[str, Any]] = []
    for plan in document.get("plans", []):
        source_plan = str(plan.get("source_plan", "unknown"))
        for position, task in enumerate(plan.get("taskcards", [])):
            external_id = str(task.get("taskcard_id") or f"item-{position}")
            disposition, contradiction = _validated_disposition(task)
            identity = hashlib.sha256(
                f"{source_plan}:{external_id}:{position}".encode("utf-8")
            ).hexdigest()[:24]
            items.append(
                {
                    "source_item_id": f"source-v1-{identity}",
                    "source_plan": source_plan,
                    "external_id": external_id,
                    "canonical_task_id": task.get("canonical_task_id"),
                    "master_state": task.get("master_state", "UNRECONCILED"),
                    "disposition": disposition,
                    "occurrence_count": len(task.get("occurrences") or []),
                    "contradiction": contradiction,
                }
            )
    return items
