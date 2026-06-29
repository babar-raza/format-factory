"""Capability ingestor: .governance/capabilities/registry.yaml → capabilities table."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from . import BaseIngestor
from ..adapters.yaml_adapter import YamlAdapter
from ..sync import register_ingestor


@register_ingestor
class CapabilityIngestor(BaseIngestor):
    entity_type = "capability"
    source_paths = [".governance/capabilities/registry.yaml"]

    def get_adapter(self, source_path: Path):
        return YamlAdapter(source_path, records_key="capabilities")

    def ingest_records(self, conn, records: Iterator[dict],
                       source_path: str, source_hash: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        for rec in records:
            cid = rec.get("capability_id")
            if not cid:
                continue
            surfaces = rec.get("agent_surfaces", {}) or {}
            conn.execute(
                """INSERT OR REPLACE INTO capabilities
                   (capability_id, command_file, parity_status, product_track,
                    purpose, status, claude_code, codex, ci,
                    raw_yaml, source_file, ingested_at, source_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    cid,
                    rec.get("command_file"),
                    rec.get("parity_status"),
                    rec.get("product_track"),
                    rec.get("purpose"),
                    rec.get("status"),
                    1 if surfaces.get("claude_code") else 0,
                    1 if surfaces.get("codex") else 0,
                    1 if surfaces.get("ci") else 0,
                    json.dumps(rec),
                    source_path,
                    now,
                    source_hash,
                ),
            )
            count += 1
        return count
