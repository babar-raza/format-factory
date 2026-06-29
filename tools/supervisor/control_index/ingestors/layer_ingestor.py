"""Layer ingestor: plans/layers/index.yaml → layers + layer_dependencies tables."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from . import BaseIngestor
from ..adapters.yaml_adapter import YamlAdapter
from ..sync import register_ingestor


@register_ingestor
class LayerIngestor(BaseIngestor):
    entity_type = "layer"
    source_paths = ["plans/layers/index.yaml"]

    def get_adapter(self, source_path: Path):
        return YamlAdapter(source_path, records_key="layers")

    def delete_existing(self, conn, source_file: str):
        conn.execute("DELETE FROM layers WHERE source_file = ?", (source_file,))
        conn.execute("DELETE FROM layer_dependencies WHERE upstream_layer_id IN "
                      "(SELECT layer_id FROM layers WHERE source_file = ?) "
                      "OR downstream_layer_id IN "
                      "(SELECT layer_id FROM layers WHERE source_file = ?)",
                      (source_file, source_file))

    def ingest_records(self, conn, records: Iterator[dict],
                       source_path: str, source_hash: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        dep_rows = []
        for rec in records:
            lid = rec.get("layer_id")
            if not lid:
                continue
            conn.execute(
                """INSERT OR REPLACE INTO layers
                   (layer_id, canonical_name, permanent_plan_path, plane,
                    status, health, maturity_current, maturity_target,
                    active_task_count, next_task_id, next_action,
                    raw_yaml, source_file, ingested_at, source_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    lid,
                    rec.get("canonical_name", ""),
                    rec.get("permanent_plan_path"),
                    rec.get("plane"),
                    rec.get("status"),
                    rec.get("health"),
                    rec.get("maturity_current"),
                    rec.get("maturity_target"),
                    rec.get("active_task_count"),
                    rec.get("next_task_id"),
                    rec.get("next_action"),
                    json.dumps(rec),
                    source_path,
                    now,
                    source_hash,
                ),
            )
            count += 1
            # Collect dependency edges
            for down in rec.get("downstream_layers", []) or []:
                dep_rows.append((lid, down))

        # Insert dependency edges
        for upstream, downstream in dep_rows:
            conn.execute(
                "INSERT OR IGNORE INTO layer_dependencies "
                "(upstream_layer_id, downstream_layer_id) VALUES (?, ?)",
                (upstream, downstream),
            )
        return count
