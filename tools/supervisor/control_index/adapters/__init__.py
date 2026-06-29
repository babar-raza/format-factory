"""Source adapters for reading JSON, JSONL, and YAML operational files.

Each adapter reads a source file and yields normalized records.
All adapters support hash-based change detection via needs_sync().
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


class SourceAdapter:
    """Base class for source file adapters."""

    def __init__(self, source_path: Path):
        self.source_path = Path(source_path)

    def file_hash(self) -> str:
        """SHA-256 hash of file content."""
        return hashlib.sha256(
            self.source_path.read_bytes()
        ).hexdigest()

    def file_mtime(self) -> str:
        """ISO-8601 modification time."""
        ts = self.source_path.stat().st_mtime
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

    def file_size(self) -> int:
        """File size in bytes."""
        return self.source_path.stat().st_size

    def needs_sync(self, manifest_row: dict | None) -> bool:
        """Check if file has changed since last sync.

        Returns True if sync is needed (file changed or never synced).
        """
        if manifest_row is None:
            return True
        stored_hash = manifest_row.get("last_hash")
        if not stored_hash:
            return True
        return self.file_hash() != stored_hash

    def read_records(self) -> Iterator[dict]:
        """Yield records from the source file. Must be overridden."""
        raise NotImplementedError
