"""QName ingestor: shared/qname-registry/*.yaml → qnames table."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from . import BaseIngestor
from ..adapters.yaml_adapter import MultiFileYamlAdapter
from ..sync import register_ingestor


@register_ingestor
class QNameIngestor(BaseIngestor):
    entity_type = "qname"
    source_paths = ["shared/qname-registry"]

    def get_adapter(self, source_path: Path):
        return MultiFileYamlAdapter(source_path, glob_pattern="*.yaml",
                                     exclude=["schema.yaml"])

    def ingest_records(self, conn, records: Iterator[dict],
                       source_path: str, source_hash: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        for rec in records:
            qname = rec.get("qname")
            if not qname:
                continue
            # Derive format_id from source filename (e.g., fods.yaml → fods)
            source_file = rec.get("_source_file", "")
            format_id = source_file.replace(".yaml", "") if source_file else None
            conn.execute(
                """INSERT OR REPLACE INTO qnames
                   (qname, format_id, namespace_uri, local_name,
                    canonical_class, spec_fact_ref, status,
                    source_layer, python_file, dotnet_file, facade_names,
                    raw_yaml, source_file, ingested_at, source_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    qname,
                    format_id,
                    rec.get("namespace_uri"),
                    rec.get("local_name"),
                    rec.get("canonical_class"),
                    rec.get("spec_fact_ref"),
                    rec.get("status"),
                    rec.get("source_layer"),
                    rec.get("python_file"),
                    rec.get("dotnet_file"),
                    json.dumps(rec.get("facade_names", [])),
                    json.dumps(rec),
                    source_path,
                    now,
                    source_hash,
                ),
            )
            count += 1
        return count
