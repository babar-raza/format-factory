"""Operational Control Index — SQLite overlay for Format Factory.

Non-destructive read-only index over scattered JSON/YAML/JSONL/Markdown
operational state files. Source files remain authoritative. The index is
disposable and reconstructible.

Location: .local/supervisor/control-index.db (gitignored)
"""

from pathlib import Path

DEFAULT_DB_PATH = Path(".local/supervisor/control-index.db")
SCHEMA_VERSION = 1


class ControlIndex:
    """Main entry point for the operational control index."""

    def __init__(self, db_path: Path | None = None, repo_root: Path | None = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.repo_root = Path(repo_root) if repo_root else Path(".")

    def get_db_path(self) -> Path:
        """Return the resolved database path."""
        if self.db_path.is_absolute():
            return self.db_path
        return self.repo_root / self.db_path
