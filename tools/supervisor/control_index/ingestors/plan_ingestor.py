"""Plan ingestor: plans/ directory → plans table.

TC-OCRD-C4-04: Scans plans/ for *.md files. Reads YAML frontmatter (if present)
for type/status/title. Counts TC-* items by status via regex. Classifies plan type
by directory: plans/strategic/ → strategic, plans/.claude/ → per_chat,
plans/layers/ → layer, other → general.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

from . import BaseIngestor
from ..sync import register_ingestor

_PLANS_DIRS = ["plans"]

_TC_OPEN_RE = re.compile(
    r"^\|\s*(TC-[A-Z0-9\-]+)\s*\|.*\|\s*(OPEN|open)\s*\|",
    re.MULTILINE,
)
_TC_CLOSED_RE = re.compile(
    r"^\|\s*(TC-[A-Z0-9\-]+)\s*\|.*\|\s*(CLOSED|closed|COMPLETE|complete|TERMINAL_CLOSED)\s*\|",
    re.MULTILINE,
)
_STATUS_INLINE_RE = re.compile(r"\*\*Status:\*\*\s*(\w+)", re.MULTILINE)
_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def _plan_type(path: Path) -> str:
    parts = path.parts
    if "strategic" in parts:
        return "strategic"
    if ".claude" in parts:
        return "per_chat"
    if "layers" in parts:
        return "layer"
    return "general"


def _infer_status(text: str, open_count: int, closed_count: int) -> str:
    # Check inline Status field
    m = _STATUS_INLINE_RE.search(text)
    if m:
        s = m.group(1).upper()
        if s in ("OPEN", "ACTIVE", "IN_PROGRESS"):
            return "active"
        if s in ("CLOSED", "COMPLETE", "TERMINAL_CLOSED", "DONE"):
            return "closed"
    if open_count == 0 and closed_count > 0:
        return "closed"
    if open_count > 0:
        return "active"
    return "unknown"


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@register_ingestor
class PlanIngestor(BaseIngestor):
    """Ingest plans directory into the plans table."""

    entity_type = "plan_file"
    source_paths = []  # Dynamic — discovered at sync time

    def get_adapter(self, source_path: Path):
        return _DirAdapter(source_path)

    def sync(self, *, force: bool = False) -> "IngestResult":
        from ..sync import IngestResult
        now = datetime.now(timezone.utc).isoformat()
        plans_dir = self.repo_root / "plans"

        if not plans_dir.exists():
            return IngestResult(entity_type=self.entity_type)

        # Clear existing plan rows before re-ingesting
        try:
            self.conn.execute("DELETE FROM plans")
        except Exception:
            pass

        count = 0
        for plan_path in sorted(plans_dir.rglob("*.md")):
            try:
                text = plan_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            rel = plan_path.relative_to(self.repo_root).as_posix()
            plan_id = plan_path.stem
            ptype = _plan_type(plan_path)

            # Extract title from first H1
            title_m = _TITLE_RE.search(text)
            title = title_m.group(1).strip() if title_m else plan_id

            # Count taskcards from table rows
            open_tc = len(_TC_OPEN_RE.findall(text))
            closed_tc = len(_TC_CLOSED_RE.findall(text))
            status = _infer_status(text, open_tc, closed_tc)

            try:
                self.conn.execute(
                    """INSERT OR REPLACE INTO plans
                       (plan_id, plan_path, plan_type, title, status,
                        open_taskcards, closed_taskcards, ingested_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (plan_id, rel, ptype, title, status, open_tc, closed_tc, now),
                )
                count += 1
            except Exception:
                continue

        return IngestResult(entity_type=self.entity_type, inserted=count)

    def delete_existing(self, conn, source_file: str) -> None:
        pass  # Handled in sync()

    def ingest_records(self, conn, records, source_path: str, source_hash: str) -> int:
        return 0  # Not used — sync() is overridden directly


class _DirAdapter:
    def __init__(self, path: Path):
        self._path = path

    def needs_sync(self, manifest):
        return True  # Always re-scan plans

    def file_hash(self) -> str:
        return ""

    def file_size(self) -> int:
        return 0

    def read_records(self):
        return iter([])
