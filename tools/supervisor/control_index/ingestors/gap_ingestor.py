"""Gap ingestor: reports/capability-layer/gap-ledger.json → gaps + gap_spec_facts tables."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from . import BaseIngestor
from ..adapters.json_adapter import JsonAdapter
from ..sync import register_ingestor


@register_ingestor
class GapIngestor(BaseIngestor):
    entity_type = "gap"
    source_paths = ["reports/capability-layer/gap-ledger.json"]

    def get_adapter(self, source_path: Path):
        return JsonAdapter(source_path, records_key="gaps")

    def delete_existing(self, conn, source_file: str):
        conn.execute("DELETE FROM gap_spec_facts WHERE gap_id IN "
                      "(SELECT gap_id FROM gaps WHERE source_file = ?)",
                      (source_file,))
        conn.execute("DELETE FROM gaps WHERE source_file = ?", (source_file,))

    def ingest_records(self, conn, records: Iterator[dict],
                       source_path: str, source_hash: str) -> int:
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        fact_rows = []
        for rec in records:
            gid = rec.get("gap_id")
            if not gid:
                continue
            conn.execute(
                """INSERT OR REPLACE INTO gaps
                   (gap_id, format, product_type, capability_name,
                    current_state, gap_type, status, priority,
                    blocks_poc, blocks_readiness,
                    commercial_impact, foss_impact,
                    owning_lane, related_capability_id, notes,
                    raw_json, source_file, ingested_at, source_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    gid,
                    rec.get("format"),
                    rec.get("product_type"),
                    rec.get("capability_name"),
                    rec.get("current_state"),
                    rec.get("gap_type"),
                    rec.get("status", ""),
                    rec.get("priority"),
                    1 if rec.get("blocks_poc") else 0,
                    1 if rec.get("blocks_readiness") else 0,
                    rec.get("commercial_impact"),
                    rec.get("foss_impact"),
                    rec.get("owning_lane"),
                    rec.get("related_capability_id"),
                    rec.get("notes"),
                    json.dumps(rec),
                    source_path,
                    now,
                    source_hash,
                ),
            )
            count += 1
            # Collect spec_facts
            for fact in rec.get("spec_facts", []) or []:
                fact_rows.append((gid, fact))

        # Batch insert spec facts
        conn.executemany(
            "INSERT OR IGNORE INTO gap_spec_facts (gap_id, spec_fact_ref) VALUES (?, ?)",
            fact_rows,
        )
        return count
