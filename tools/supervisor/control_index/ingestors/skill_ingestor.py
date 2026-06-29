"""Skill ingestor: .supervisor/skill-registry.yaml → skills table."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from . import BaseIngestor
from ..adapters.yaml_adapter import YamlAdapter
from ..sync import register_ingestor


@register_ingestor
class SkillIngestor(BaseIngestor):
    entity_type = "skill"
    source_paths = [".supervisor/skill-registry.yaml"]

    def get_adapter(self, source_path: Path):
        return YamlAdapter(source_path, records_key="skills")

    def ingest_records(self, conn, records: Iterator[dict],
                       source_path: str, source_hash: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        for rec in records:
            command = rec.get("command", "")
            if not command:
                continue
            skill_id = rec.get("skill_id") or command.lstrip("/")
            conn.execute(
                """INSERT OR REPLACE INTO skills
                   (skill_id, command, command_file, idempotency, product_track,
                    purpose, status, overflow_split_allowed,
                    raw_yaml, source_file, ingested_at, source_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    skill_id,
                    command,
                    rec.get("command_file"),
                    rec.get("idempotency"),
                    rec.get("product_track"),
                    rec.get("purpose"),
                    rec.get("status"),
                    1 if rec.get("overflow_split_allowed") else 0,
                    json.dumps(rec),
                    source_path,
                    now,
                    source_hash,
                ),
            )
            count += 1
        return count
