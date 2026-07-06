"""command_invocations_ingestor.py — Ingest .py file references from .claude/commands/*.md.

Creates command_invocations table and scans all .md files under .claude/commands/ for
lines referencing tools/supervisor/*.py files.
"""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ..sync import register_ingestor


TABLE_DDL = """
CREATE TABLE IF NOT EXISTS command_invocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_file TEXT NOT NULL,
    referenced_stem TEXT,
    referenced_path TEXT,
    line_number INTEGER,
    ingested_at TEXT NOT NULL
)
"""


@register_ingestor
class CommandInvocationsIngestor:
    """Scans .claude/commands/**/*.md for tools/supervisor/*.py references."""

    entity_type = "command_invocation"
    source_paths: list[str] = []  # Not used -- scans directory

    def __init__(self, conn: sqlite3.Connection, repo_root: Path):
        self.conn = conn
        self.repo_root = Path(repo_root)
        self._ensure_table()

    def _ensure_table(self):
        self.conn.execute(TABLE_DDL)

    def sync(self, *, force: bool = False):
        from ..sync import IngestResult
        result = IngestResult(entity_type=self.entity_type)

        commands_dir = self.repo_root / ".claude" / "commands"
        if not commands_dir.is_dir():
            return result

        now = datetime.now(timezone.utc).isoformat()
        count = 0
        py_pattern = re.compile(r'(tools/supervisor/[\w/.-]+\.py|[\w.-]+\.py)')

        for md_file in sorted(commands_dir.rglob("*.md")):
            try:
                src = md_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            rel_command = str(md_file.relative_to(self.repo_root).as_posix())
            for i, line in enumerate(src.splitlines(), 1):
                for match in py_pattern.finditer(line):
                    ref = match.group(1)
                    stem = Path(ref).stem
                    self.conn.execute(
                        """INSERT INTO command_invocations
                           (command_file, referenced_stem, referenced_path, line_number, ingested_at)
                           VALUES (?, ?, ?, ?, ?)""",
                        (rel_command, stem, ref, i, now)
                    )
                    count += 1

        result.inserted = count
        return result
