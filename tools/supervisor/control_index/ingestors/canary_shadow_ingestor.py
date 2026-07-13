"""Canary shadow ingestor: JSONL shadow logs → validator/grader shadow tables."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from . import BaseIngestor
from ..adapters.json_adapter import JsonlAdapter
from ..sync import register_ingestor

_VALIDATOR_LOG = ".local/supervisor/validator-shadow-log.jsonl"
_GRADER_LOG = ".local/supervisor/grader-shadow-log.jsonl"


@register_ingestor
class CanaryShadowIngestor(BaseIngestor):
    entity_type = "canary_shadow"
    source_paths = [_VALIDATOR_LOG, _GRADER_LOG]

    def get_adapter(self, source_path: Path):
        return JsonlAdapter(source_path)

    def delete_existing(self, conn, source_file: str):
        if "validator" in source_file:
            conn.execute(
                "DELETE FROM validator_shadow_observations WHERE source_file = ?",
                (source_file,),
            )
        else:
            conn.execute(
                "DELETE FROM grader_shadow_observations WHERE source_file = ?",
                (source_file,),
            )

    def ingest_records(
        self, conn, records: Iterator[dict], source_path: str, source_hash: str
    ) -> int:
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        is_validator = "validator" in source_path

        for rec in records:
            if not rec:
                continue
            if is_validator:
                conn.execute(
                    """INSERT OR IGNORE INTO validator_shadow_observations
                       (validator_id, observed_at, sprint_id, result,
                        would_have_blocked, finding_count, mode,
                        raw_json, source_file, ingested_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        rec.get("validator_id", ""),
                        rec.get("ts", now),
                        rec.get("sprint_id", ""),
                        rec.get("result", ""),
                        1 if rec.get("would_have_blocked") else 0,
                        rec.get("finding_count", 0),
                        rec.get("mode", "shadow"),
                        json.dumps(rec),
                        source_path,
                        now,
                    ),
                )
            else:
                conn.execute(
                    """INSERT OR IGNORE INTO grader_shadow_observations
                       (item_id, sprint_id, shadow_provider, stable_grade,
                        shadow_grade, agreement, shadow_latency_ms, error,
                        raw_json, source_file, ingested_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        rec.get("item_id", ""),
                        rec.get("sprint_id", ""),
                        rec.get("shadow_provider", ""),
                        rec.get("stable_grade"),
                        rec.get("shadow_grade"),
                        rec.get("agreement"),
                        rec.get("shadow_latency_ms"),
                        rec.get("error"),
                        json.dumps(rec),
                        source_path,
                        now,
                    ),
                )
            count += 1

        return count
