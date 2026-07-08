"""Maintenance obligation ingestor: reports/supervisor/maintenance-obligations.json
-> maintenance_obligations table.

TC-MOR-C6: Control index ingestion for the Maintenance Obligation Register.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from . import BaseIngestor
from ..sync import register_ingestor


class _MorAdapter:
    """Read maintenance-obligations.json and yield one dict per obligation."""

    def __init__(self, path: Path):
        self._path = path

    def needs_sync(self, manifest) -> bool:
        if not self._path.exists():
            return False
        if manifest is None:
            return True
        import hashlib
        current_hash = hashlib.sha256(self._path.read_bytes()).hexdigest()[:16]
        return current_hash != manifest.get("source_hash", "")

    def file_hash(self) -> str:
        import hashlib
        return hashlib.sha256(self._path.read_bytes()).hexdigest()[:16]

    def file_size(self) -> int:
        return self._path.stat().st_size

    def read_records(self) -> Iterator[dict]:
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            for ob in data.get("obligations", []):
                yield ob
        except Exception:
            return


@register_ingestor
class MaintenanceObligationIngestor(BaseIngestor):
    entity_type = "maintenance_obligation"
    source_paths = ["reports/supervisor/maintenance-obligations.json"]

    def get_adapter(self, source_path: Path):
        return _MorAdapter(source_path)

    def delete_existing(self, conn, source_file: str):
        conn.execute(
            "DELETE FROM maintenance_obligations WHERE source_file = ?",
            (source_file,),
        )

    def ingest_records(
        self, conn, records: Iterator[dict], source_path: str, source_hash: str
    ) -> int:
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        for ob in records:
            oid = ob.get("obligation_id")
            if not oid:
                continue
            conn.execute(
                """INSERT OR REPLACE INTO maintenance_obligations
                   (obligation_id, type, status, scheduled_date, owner,
                    source_plan, source_taskcard, action, reason,
                    created_at, completed_at, completion_evidence,
                    raw_json, source_file, ingested_at, source_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    oid,
                    ob.get("type"),
                    ob.get("status", "open"),
                    ob.get("scheduled_date"),
                    ob.get("owner"),
                    ob.get("source_plan"),
                    ob.get("source_taskcard"),
                    ob.get("action"),
                    ob.get("reason"),
                    ob.get("created_at"),
                    ob.get("completed_at"),
                    ob.get("completion_evidence"),
                    json.dumps(ob),
                    source_path,
                    now,
                    source_hash,
                ),
            )
            count += 1
        return count
