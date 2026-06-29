"""Failure ingestor: .local/supervisor/failure-memory.json → failures table."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from . import BaseIngestor
from ..adapters.json_adapter import JsonAdapter
from ..sync import register_ingestor


@register_ingestor
class FailureIngestor(BaseIngestor):
    entity_type = "failure"
    source_paths = [".local/supervisor/failure-memory.json"]

    def get_adapter(self, source_path: Path):
        return JsonAdapter(source_path, records_key="failures")

    def ingest_records(self, conn, records: Iterator[dict],
                       source_path: str, source_hash: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        for rec in records:
            fid = rec.get("id")
            if not fid:
                continue
            conn.execute(
                """INSERT OR REPLACE INTO failures
                   (failure_id, category, root_cause, correction, severity,
                    sprint_discovered, last_seen_sprint,
                    discovered_at, last_seen_at,
                    occurrence_count, escalated, resolved,
                    resolution, resolved_at,
                    raw_json, source_file, ingested_at, source_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    fid,
                    rec.get("category"),
                    rec.get("root_cause"),
                    rec.get("correction"),
                    rec.get("severity"),
                    rec.get("sprint_discovered"),
                    rec.get("last_seen_sprint"),
                    rec.get("discovered_at"),
                    rec.get("last_seen_at"),
                    rec.get("occurrence_count"),
                    1 if rec.get("escalated") else 0,
                    1 if rec.get("resolved") else 0,
                    rec.get("resolution"),
                    rec.get("resolved_at"),
                    json.dumps(rec),
                    source_path,
                    now,
                    source_hash,
                ),
            )
            count += 1
        return count
