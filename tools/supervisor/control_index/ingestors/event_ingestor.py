"""Event ingestor: .local/supervisor/continuation-ledger.jsonl → events table."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from . import BaseIngestor
from ..adapters.json_adapter import JsonlAdapter
from ..sync import register_ingestor


@register_ingestor
class EventIngestor(BaseIngestor):
    entity_type = "event"
    source_paths = [".local/supervisor/continuation-ledger.jsonl"]

    def get_adapter(self, source_path: Path):
        return JsonlAdapter(source_path)

    def delete_existing(self, conn, source_file: str):
        conn.execute("DELETE FROM events WHERE source = ?", (source_file,))

    def ingest_records(self, conn, records: Iterator[dict],
                       source_path: str, source_hash: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        rows = []
        for rec in records:
            ts = rec.get("timestamp", "")
            event_type = rec.get("event_type", "")
            if not ts or not event_type:
                continue
            # Extract known fields, put rest in detail
            detail_fields = {k: v for k, v in rec.items()
                             if k not in ("timestamp", "event_type", "session_id",
                                          "sprint_id", "artifact_path")}
            rows.append((
                ts,
                event_type,
                source_path,
                rec.get("session_id"),
                rec.get("sprint_id"),
                rec.get("artifact_path"),
                json.dumps(detail_fields) if detail_fields else None,
                now,
            ))

        conn.executemany(
            """INSERT INTO events
               (timestamp, event_type, source, session_id,
                sprint_id, artifact_path, detail, ingested_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
        return len(rows)
