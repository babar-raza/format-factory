"""Format ingestor: registry/format-registry.yaml → formats table."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from . import BaseIngestor
from ..adapters.yaml_adapter import YamlAdapter
from ..sync import register_ingestor


@register_ingestor
class FormatIngestor(BaseIngestor):
    entity_type = "format"
    source_paths = ["registry/format-registry.yaml"]

    def get_adapter(self, source_path: Path):
        return YamlAdapter(source_path, records_key="formats")

    def ingest_records(self, conn, records: Iterator[dict],
                       source_path: str, source_hash: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        for rec in records:
            fid = rec.get("format_id")
            if not fid:
                continue
            scoring = rec.get("scoring", {}) or {}
            conn.execute(
                """INSERT OR REPLACE INTO formats
                   (format_id, display_name, family, extensions, mime_type,
                    spec_body, spec_version, legal_category, tier_target,
                    visibility, scoring_total, raw_json, source_file, ingested_at, source_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    fid,
                    rec.get("display_name", fid),
                    rec.get("family"),
                    json.dumps(rec.get("extensions", [])),
                    rec.get("mime_type"),
                    rec.get("spec_body"),
                    rec.get("spec_version"),
                    rec.get("legal_category"),
                    rec.get("tier_target"),
                    rec.get("visibility"),
                    scoring.get("total_points"),
                    json.dumps(rec),
                    source_path,
                    now,
                    source_hash,
                ),
            )
            count += 1
        return count
