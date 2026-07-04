"""plan_lock_gc.py — Garbage collection for SUPERSEDED plan lock files.

TC-PGI-044: Auto-delete SUPERSEDED locks older than N days during pre-cycle housekeeping.
Extracted from autonomous_cycle.py run_cycle() to keep that file within its LOC cap.

Only deletes locks with status == "SUPERSEDED". Never touches TERMINAL_CLOSED,
DEFERRED, IN_PROGRESS, or COMPLETE locks.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path


def gc_superseded_locks(plan_locks_dir: Path, days: int = 30) -> int:
    """Delete SUPERSEDED plan locks older than N days.

    Non-blocking — all errors are suppressed. Returns count of deleted files.
    """
    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0
    try:
        for lf in plan_locks_dir.glob("*.json"):
            try:
                lk = json.loads(lf.read_text(encoding="utf-8"))
                if lk.get("status") == "SUPERSEDED":
                    upd_str = lk.get("updated_at", "")
                    try:
                        upd = datetime.fromisoformat(
                            upd_str.rstrip("Z").replace("+00:00", "")
                        )
                    except Exception:
                        continue
                    if upd < cutoff:
                        lf.unlink()
                        deleted += 1
            except Exception:
                continue
    except Exception:
        pass
    return deleted
