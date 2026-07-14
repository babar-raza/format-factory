"""Contradiction ingestor: reports/supervisor/contradictions.json → events table.

TC-OCRD-C4-03: If the contradiction report shows CLEAN, deletes prior contradiction
events. If not CLEAN, inserts one event per critical contradiction.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from . import BaseIngestor
from ..sync import register_ingestor

_SOURCE = "reports/supervisor/contradictions.json"


def _file_hash(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


@register_ingestor
class ContradictionIngestor(BaseIngestor):
    """Ingest contradiction report into events table."""

    entity_type = "contradiction"
    source_paths = [_SOURCE]

    def get_adapter(self, source_path: Path):
        return _JsonFileAdapter(source_path)

    def ingest_records(self, conn, records, source_path: str, source_hash: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        abs_path = self.repo_root / _SOURCE

        if not abs_path.exists():
            return 0

        try:
            data = json.loads(abs_path.read_text(encoding="utf-8"))
        except Exception:
            return 0

        # Delete prior contradiction events
        try:
            conn.execute(
                "DELETE FROM events WHERE event_type = 'contradiction_detected'"
            )
        except Exception:
            pass

        overall = data.get("overall", "CLEAN")
        if overall == "CLEAN":
            return 0

        contradictions = data.get("contradictions", [])
        count = 0
        for c in contradictions:
            severity = c.get("severity", "")
            if severity != "CRITICAL":
                continue
            cid = c.get("id") or c.get("contradiction_id") or f"c{count}"
            conn.execute(
                """INSERT INTO events
                   (timestamp, event_type, source, session_id, sprint_id,
                    artifact_path, detail, ingested_at)
                   VALUES (?, 'contradiction_detected', ?, NULL, NULL, ?, ?, ?)""",
                (
                    now,
                    source_path,
                    source_path,
                    json.dumps({"contradiction_id": cid, "severity": severity,
                                "description": c.get("description", "")}),
                    now,
                ),
            )
            count += 1

        return count

    def delete_existing(self, conn, source_file: str) -> None:
        # Handled inside ingest_records
        pass


class _JsonFileAdapter:
    def __init__(self, path: Path):
        self._path = path

    def needs_sync(self, manifest: dict | None) -> bool:
        if not self._path.exists():
            return False
        current_hash = self.file_hash()
        if manifest is None:
            return True
        return manifest.get("last_hash") != current_hash

    def file_hash(self) -> str:
        return _file_hash(self._path)

    def file_size(self) -> int:
        return self._path.stat().st_size if self._path.exists() else 0

    def read_records(self):
        return iter([])
