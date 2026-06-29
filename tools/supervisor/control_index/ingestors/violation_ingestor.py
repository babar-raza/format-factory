"""Violation ingestor: registry/source-structure-baseline.json → source_violations table."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from . import BaseIngestor
from ..adapters.json_adapter import DictAdapter
from ..sync import register_ingestor


class _ViolationAdapter(DictAdapter):
    """Custom adapter that reads known_violations dict from baseline file."""

    def read_records(self) -> Iterator[dict]:
        data = json.loads(self.source_path.read_text(encoding="utf-8"))
        violations = data.get("known_violations", {})
        if isinstance(violations, dict):
            for file_path, info in violations.items():
                if isinstance(info, dict):
                    yield {"_key": file_path, **info}


@register_ingestor
class ViolationIngestor(BaseIngestor):
    entity_type = "source_violation"
    source_paths = ["registry/source-structure-baseline.json"]

    def get_adapter(self, source_path: Path):
        return _ViolationAdapter(source_path)

    def ingest_records(self, conn, records: Iterator[dict],
                       source_path: str, source_hash: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        for rec in records:
            fp = rec.get("_key")
            if not fp:
                continue
            conn.execute(
                """INSERT OR REPLACE INTO source_violations
                   (file_path, loc, baseline_loc_cap, functions,
                    baseline_functions_cap, category, healing_priority,
                    healing_sprint,
                    raw_json, source_file, ingested_at, source_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    fp,
                    rec.get("loc"),
                    rec.get("baseline_loc_cap"),
                    rec.get("functions"),
                    rec.get("baseline_functions_cap"),
                    rec.get("category"),
                    rec.get("healing_priority"),
                    rec.get("healing_sprint"),
                    json.dumps(rec),
                    source_path,
                    now,
                    source_hash,
                ),
            )
            count += 1
        return count
