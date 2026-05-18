"""Telemetry call logger — writes AIUsageRecords to local JSONL spool.

No external posting in Phase 1. Local spool is evidence/replay/offline buffer.
Never logs raw secrets, prompts, or responses by default.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from tools.ai.schemas.models import AIUsageRecord


def _serialize_record(record: AIUsageRecord) -> str:
    """Serialize a telemetry record to JSON string."""
    data = record.model_dump(mode="json")
    # Ensure no secret fields leak
    for key in list(data.keys()):
        if "key" in key.lower() and "hash" not in key.lower():
            if isinstance(data[key], str) and len(data[key]) > 5:
                data[key] = "[REDACTED]"
    return json.dumps(data, default=str)


def log_call(record: AIUsageRecord, spool_path: Path) -> Path:
    """Append a telemetry record to the JSONL spool file.

    Creates spool directory and file if needed.
    Returns the path to the spool file written to.
    """
    spool_path.mkdir(parents=True, exist_ok=True)
    spool_file = spool_path / "ai-telemetry.jsonl"
    line = _serialize_record(record)
    with open(spool_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return spool_file


def read_spool(spool_path: Path) -> list[dict]:
    """Read all records from the spool file."""
    spool_file = spool_path / "ai-telemetry.jsonl"
    if not spool_file.exists():
        return []
    records = []
    with open(spool_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records
