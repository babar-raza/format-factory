"""Evidence ingestor: .local/evidences/*/evidence-declaration.yaml → sprints + sprint_work_items.

TC-OCRD-A1-05: Also ingests gap_attempts rows from planned_work_items with gap_ledger_ref set.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

import yaml

from . import BaseIngestor
from ..sync import IngestResult, get_manifest_row, update_manifest, register_ingestor
from ..gap_selection import classify_outcome as _classify_outcome


@register_ingestor
class EvidenceIngestor(BaseIngestor):
    entity_type = "sprint"
    source_paths = [".local/evidences"]

    def get_adapter(self, source_path: Path):
        # Not used — custom sync() override
        return None

    def delete_existing(self, conn, source_file: str):
        conn.execute("DELETE FROM sprint_work_items WHERE sprint_id IN "
                      "(SELECT sprint_id FROM sprints WHERE source_file = ?)",
                      (source_file,))
        conn.execute("DELETE FROM sprints WHERE source_file = ?", (source_file,))

    def sync(self, *, force: bool = False) -> IngestResult:
        """Custom sync: scan evidence directories individually."""
        result = IngestResult(entity_type=self.entity_type)
        evidences_dir = self.repo_root / ".local" / "evidences"
        if not evidences_dir.exists():
            return result

        now = datetime.now(timezone.utc).isoformat()
        for subdir in sorted(evidences_dir.iterdir()):
            if not subdir.is_dir():
                continue
            decl_path = subdir / "evidence-declaration.yaml"
            if not decl_path.exists():
                continue

            rel_path = decl_path.relative_to(self.repo_root).as_posix()
            manifest = get_manifest_row(self.conn, rel_path)

            if not force and manifest:
                # Evidence declarations are immutable once created — skip if seen
                result.skipped = True
                continue

            try:
                content = decl_path.read_text(encoding="utf-8", errors="replace")
                rec = yaml.safe_load(content)
                if not isinstance(rec, dict):
                    continue
            except Exception:
                continue

            import hashlib
            source_hash = hashlib.sha256(
                decl_path.read_bytes()
            ).hexdigest()

            sprint_id = rec.get("sprint_id") or rec.get("run_id") or subdir.name

            def _str(val):
                """Coerce non-scalar values to JSON strings for SQLite binding."""
                if val is None or isinstance(val, (str, int, float)):
                    return val
                return json.dumps(val, default=str)

            self.conn.execute(
                """INSERT OR REPLACE INTO sprints
                   (sprint_id, run_id, evidence_root, declared_scope,
                    start_time, end_time, git_head_start, git_head_end,
                    verdict, test_count, fail_count, worker_self_grade,
                    raw_yaml, source_file, ingested_at, source_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    sprint_id,
                    _str(rec.get("run_id")),
                    _str(rec.get("evidence_root")),
                    _str(rec.get("declared_scope")),
                    _str(rec.get("start_time")),
                    _str(rec.get("end_time")),
                    _str(rec.get("git_head_start")),
                    _str(rec.get("git_head_end")),
                    _str(rec.get("worker_self_verdict") or rec.get("verdict")),
                    _str(rec.get("tests_run") or rec.get("test_count")),
                    _str(rec.get("tests_failed") or rec.get("fail_count")),
                    _str(rec.get("worker_self_grade")),
                    json.dumps(rec, default=str),
                    rel_path,
                    now,
                    source_hash,
                ),
            )
            result.inserted += 1

            # Insert work items; also write gap_attempts for items linked to a gap
            for item in rec.get("planned_work_items", []) or []:
                if not isinstance(item, dict):
                    continue
                item_id = item.get("item_id", "")
                if not item_id:
                    continue
                self.conn.execute(
                    """INSERT OR IGNORE INTO sprint_work_items
                       (sprint_id, item_id, title, item_type, status, gap_ledger_ref)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        sprint_id,
                        item_id,
                        item.get("title"),
                        item.get("item_type"),
                        item.get("status"),
                        item.get("gap_ledger_ref"),
                    ),
                )
                # TC-OCRD-A1-05: Record gap attempt when item references a gap
                gap_ref = item.get("gap_ledger_ref")
                if gap_ref:
                    outcome = _classify_outcome(item.get("status"))
                    attempt_id = f"{sprint_id}:{item_id}"
                    self.conn.execute(
                        """INSERT OR IGNORE INTO gap_attempts
                           (attempt_id, gap_id, sprint_id, item_id, outcome,
                            rework_reason, attempted_at, source_file)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            attempt_id,
                            gap_ref,
                            sprint_id,
                            item_id,
                            outcome,
                            item.get("rework_reason"),
                            _str(rec.get("start_time")) or now,
                            rel_path,
                        ),
                    )

            try:
                file_size = decl_path.stat().st_size
            except OSError:
                file_size = 0
            update_manifest(
                self.conn, rel_path, self.entity_type,
                source_hash, 1, file_size,
            )

        return result
