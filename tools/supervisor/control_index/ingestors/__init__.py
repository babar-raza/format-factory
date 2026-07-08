"""Entity ingestors for populating the control index from source files.

Each ingestor reads a specific source file type and populates its target table(s).
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from ..adapters import SourceAdapter
from ..sync import IngestResult, get_manifest_row, update_manifest


class BaseIngestor:
    """Base class for entity ingestors.

    Subclasses must set:
        entity_type: str — name of the entity type
        source_paths: list[str] — relative paths from repo root

    And implement:
        get_adapter(source_path) -> SourceAdapter
        ingest_records(conn, records, source_path, source_hash) -> int
    """

    entity_type: str = ""
    source_paths: list[str] = []

    def __init__(self, conn, repo_root: Path):
        self.conn = conn
        self.repo_root = Path(repo_root)

    def get_adapter(self, source_path: Path) -> SourceAdapter:
        """Return the appropriate adapter for the source file."""
        raise NotImplementedError

    def ingest_records(self, conn, records: Iterator[dict],
                       source_path: str, source_hash: str) -> int:
        """Ingest records into the database. Return count of rows inserted."""
        raise NotImplementedError

    def delete_existing(self, conn, source_file: str):
        """Delete existing rows for this source file before re-ingesting."""
        # Default: delete from the entity's primary table
        table = self.entity_type + "s" if not self.entity_type.endswith("s") else self.entity_type
        # Map entity_type to actual table name
        table_map = {
            "format": "formats",
            "gap": "gaps",
            "qname": "qnames",
            "capability": "capabilities",
            "skill": "skills",
            "sprint": "sprints",
            "failure": "failures",
            "layer": "layers",
            "plan_lock": "plan_locks",
            "source_violation": "source_violations",
            "event": "events",
            "maintenance_obligation": "maintenance_obligations",
        }
        table_name = table_map.get(self.entity_type, table)
        try:
            conn.execute(f"DELETE FROM [{table_name}] WHERE source_file = ?", (source_file,))
        except Exception:
            pass

    def sync(self, *, force: bool = False) -> IngestResult:
        """Sync this ingestor's source files to the database."""
        result = IngestResult(entity_type=self.entity_type)
        now = datetime.now(timezone.utc).isoformat()

        for rel_path in self.source_paths:
            abs_path = self.repo_root / rel_path
            if not abs_path.exists():
                continue

            adapter = self.get_adapter(abs_path)
            manifest = get_manifest_row(self.conn, rel_path)

            if not force and not adapter.needs_sync(manifest):
                result.skipped = True
                continue

            source_hash = adapter.file_hash()

            # Delete existing rows for this source
            self.delete_existing(self.conn, rel_path)

            # Ingest new records
            count = self.ingest_records(
                self.conn, adapter.read_records(), rel_path, source_hash
            )
            result.inserted += count

            # Update manifest
            try:
                file_size = adapter.file_size()
            except OSError:
                file_size = 0
            update_manifest(
                self.conn, rel_path, self.entity_type,
                source_hash, count, file_size,
            )

        return result
