"""
continuation_ledger.py — Append-Only Continuation Event Ledger (CCI)

Records every state transition in continuation artifacts as JSONL events.
This enables audit, conflict detection, and consumed-state tracking.

Event types:
  CREATED    — a new continuation artifact was produced
  CONSUMED   — a continuation artifact was read and acted upon
  SUPERSEDED — a newer artifact replaced this one
  QUARANTINED — artifact moved to quarantine due to conflict/staleness
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LEDGER_PATH = _REPO_ROOT / ".local" / "supervisor" / "continuation-ledger.jsonl"


def append_event(
    event_type: str,
    artifact_path: str,
    session_id: Optional[str] = None,
    sprint_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Append a continuation event to the ledger.

    Returns the event dict that was written.
    """
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "artifact_path": artifact_path,
        "session_id": session_id,
        "sprint_id": sprint_id,
    }
    if metadata:
        event["metadata"] = metadata

    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    return event


def query_active(
    session_id: Optional[str] = None,
    artifact_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Query events that are CREATED but not yet CONSUMED or SUPERSEDED.

    Optionally filter by session_id and/or artifact_path.
    """
    if not LEDGER_PATH.exists():
        return []

    events: List[Dict[str, Any]] = []
    consumed_or_superseded: set = set()

    for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        events.append(evt)

    # Build set of consumed/superseded/quarantined artifact+session combos
    for evt in events:
        if evt.get("event_type") in ("CONSUMED", "SUPERSEDED", "QUARANTINED"):
            key = (evt.get("artifact_path"), evt.get("session_id"))
            consumed_or_superseded.add(key)

    # Filter to active CREATED events
    active = []
    for evt in events:
        if evt.get("event_type") != "CREATED":
            continue
        key = (evt.get("artifact_path"), evt.get("session_id"))
        if key in consumed_or_superseded:
            continue
        if session_id and evt.get("session_id") != session_id:
            continue
        if artifact_path and evt.get("artifact_path") != artifact_path:
            continue
        active.append(evt)

    return active


def mark_consumed(
    artifact_path: str,
    session_id: Optional[str] = None,
    sprint_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Mark a continuation artifact as consumed."""
    return append_event("CONSUMED", artifact_path, session_id=session_id, sprint_id=sprint_id)


def mark_superseded(
    artifact_path: str,
    session_id: Optional[str] = None,
    sprint_id: Optional[str] = None,
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    """Mark a continuation artifact as superseded by a newer one."""
    return append_event(
        "SUPERSEDED", artifact_path,
        session_id=session_id, sprint_id=sprint_id,
        metadata={"reason": reason} if reason else None,
    )


def detect_conflicts(artifact_path: str) -> List[Dict[str, Any]]:
    """Find active CREATED events for the same artifact from different sessions."""
    active = query_active(artifact_path=artifact_path)
    if len(active) <= 1:
        return []

    # Group by session_id
    sessions = {}
    for evt in active:
        sid = evt.get("session_id", "unknown")
        sessions.setdefault(sid, []).append(evt)

    if len(sessions) > 1:
        return active  # Multiple sessions have active claims on same artifact
    return []
