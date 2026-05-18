"""Spool manager — manages local telemetry spool lifecycle.

Phase 1: local spool only. No external Agent Metrics posting.
Spool replay design placeholder for Phase 2+.
"""

from __future__ import annotations

import json
from pathlib import Path


DEFAULT_SPOOL_PATH = Path(".local/ai/spool")


def get_spool_path() -> Path:
    """Return the canonical spool path."""
    return DEFAULT_SPOOL_PATH


def spool_exists() -> bool:
    """Check if spool file exists."""
    return (DEFAULT_SPOOL_PATH / "ai-telemetry.jsonl").exists()


def spool_record_count() -> int:
    """Count records in the spool."""
    spool_file = DEFAULT_SPOOL_PATH / "ai-telemetry.jsonl"
    if not spool_file.exists():
        return 0
    count = 0
    with open(spool_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def rotate_spool() -> Path | None:
    """Rotate the spool file by renaming with timestamp.

    Returns the path to the rotated file, or None if no spool exists.
    """
    from datetime import datetime, timezone
    spool_file = DEFAULT_SPOOL_PATH / "ai-telemetry.jsonl"
    if not spool_file.exists():
        return None
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rotated = DEFAULT_SPOOL_PATH / f"ai-telemetry-{ts}.jsonl"
    spool_file.rename(rotated)
    return rotated


# Phase 2+ placeholder: replay_spool() would POST records to Agent Metrics.
# Not implemented in Phase 1 — posted_to_agent_metrics remains False.
