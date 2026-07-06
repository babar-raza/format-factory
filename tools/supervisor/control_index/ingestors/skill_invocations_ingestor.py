"""skill_invocations_ingestor.py — Ingest skill-registry .py file references.

Creates skill_invocations table by reading .supervisor/skill-registry.yaml and extracting
any command: or command_file: values that reference .py files.
"""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ..sync import register_ingestor


TABLE_DDL = """
CREATE TABLE IF NOT EXISTS skill_invocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id TEXT,
    referenced_stem TEXT,
    referenced_path TEXT,
    field_path TEXT,
    ingested_at TEXT NOT NULL
)
"""


@register_ingestor
class SkillInvocationsIngestor:
    """Reads .supervisor/skill-registry.yaml for command_file .py references."""

    entity_type = "skill_invocation"
    source_paths: list[str] = []  # Not used -- reads YAML directly

    def __init__(self, conn: sqlite3.Connection, repo_root: Path):
        self.conn = conn
        self.repo_root = Path(repo_root)
        self._ensure_table()

    def _ensure_table(self):
        self.conn.execute(TABLE_DDL)

    def sync(self, *, force: bool = False):
        from ..sync import IngestResult
        result = IngestResult(entity_type=self.entity_type)

        registry_path = self.repo_root / ".supervisor" / "skill-registry.yaml"
        if not registry_path.exists():
            return result

        try:
            import yaml  # type: ignore[import]
            data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        except Exception:
            return result

        now = datetime.now(timezone.utc).isoformat()
        count = 0
        py_pattern = re.compile(r'[\w/\\.-]+\.py')
        skills = data.get("skills", []) if isinstance(data, dict) else []

        for skill in skills:
            skill_id = skill.get("skill_id") or skill.get("command", "")
            for field in ("command_file", "command", "script", "runner"):
                val = skill.get(field, "")
                if val and py_pattern.search(str(val)):
                    refs = py_pattern.findall(str(val))
                    for ref in refs:
                        stem = Path(ref).stem
                        self.conn.execute(
                            """INSERT INTO skill_invocations
                               (skill_id, referenced_stem, referenced_path, field_path, ingested_at)
                               VALUES (?, ?, ?, ?, ?)""",
                            (skill_id, stem, ref, field, now)
                        )
                        count += 1

        result.inserted = count
        return result
