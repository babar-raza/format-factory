"""Plan lock ingestor: .local/supervisor/plan-locks/*.json → plan_locks table."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from . import BaseIngestor
from ..adapters.json_adapter import MultiFileJsonAdapter
from ..sync import register_ingestor


@register_ingestor
class PlanLockIngestor(BaseIngestor):
    entity_type = "plan_lock"
    source_paths = [".local/supervisor/plan-locks"]

    def get_adapter(self, source_path: Path):
        return MultiFileJsonAdapter(source_path, glob_pattern="*.json")

    def delete_existing(self, conn, source_file: str):
        conn.execute("DELETE FROM plan_locks WHERE source_file = ?", (source_file,))

    def ingest_records(self, conn, records: Iterator[dict],
                       source_path: str, source_hash: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        for rec in records:
            lock_file = rec.get("_source_file", "")
            status = rec.get("status", "")
            if not lock_file or not status:
                continue
            conn.execute(
                """INSERT OR REPLACE INTO plan_locks
                   (lock_file, plan_path, status, session_id,
                    track_type, last_taskcard, updated_at, terminal_reason,
                    raw_json, source_file, ingested_at, source_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    lock_file,
                    rec.get("plan_path"),
                    status,
                    rec.get("session_id"),
                    rec.get("track_type"),
                    rec.get("last_taskcard"),
                    rec.get("updated_at"),
                    rec.get("terminal_reason"),
                    json.dumps(rec),
                    source_path,
                    now,
                    source_hash,
                ),
            )
            count += 1
        return count
