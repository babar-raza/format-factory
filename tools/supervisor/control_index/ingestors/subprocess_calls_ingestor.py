"""subprocess_calls_ingestor.py — Ingest subprocess.run() calls from tools/supervisor/*.py.

Creates subprocess_invocations table and scans all .py files for subprocess.run() or
subprocess.call() invocations that reference other .py files.
"""
from __future__ import annotations

import ast
import glob
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from ..sync import register_ingestor


TABLE_DDL = """
CREATE TABLE IF NOT EXISTS subprocess_invocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_file TEXT NOT NULL,
    callee_stem TEXT,
    call_args TEXT,
    line_number INTEGER,
    ingested_at TEXT NOT NULL
)
"""


@register_ingestor
class SubprocessCallsIngestor:
    """Scans tools/supervisor/**/*.py for subprocess.run/call invocations."""

    entity_type = "subprocess_invocation"
    source_paths: list[str] = []  # Not used — scans directory

    def __init__(self, conn: sqlite3.Connection, repo_root: Path):
        self.conn = conn
        self.repo_root = Path(repo_root)
        self._ensure_table()

    def _ensure_table(self):
        self.conn.execute(TABLE_DDL)

    def sync(self, *, force: bool = False):
        from ..sync import IngestResult
        result = IngestResult(entity_type=self.entity_type)

        sup_dir = self.repo_root / "tools" / "supervisor"
        if not sup_dir.is_dir():
            return result

        now = datetime.now(timezone.utc).isoformat()
        count = 0
        pattern = re.compile(r'subprocess\.(run|call|Popen|check_output)\s*\(')

        for py_file in sorted(sup_dir.rglob("*.py")):
            parts = py_file.parts
            if "__pycache__" in parts or "_quarantine" in parts:
                continue
            try:
                src = py_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            for i, line in enumerate(src.splitlines(), 1):
                if not pattern.search(line):
                    continue
                # Look for .py file references in the call arguments
                py_refs = re.findall(r'[\w/\\.-]+\.py', line)
                for ref in py_refs or [None]:
                    stem = Path(ref).stem if ref else None
                    rel_caller = str(py_file.relative_to(self.repo_root).as_posix())
                    self.conn.execute(
                        """INSERT INTO subprocess_invocations
                           (caller_file, callee_stem, call_args, line_number, ingested_at)
                           VALUES (?, ?, ?, ?, ?)""",
                        (rel_caller, stem, line.strip()[:200], i, now)
                    )
                    count += 1
                    if py_refs:
                        break  # one row per line with py ref

        result.inserted = count
        return result
