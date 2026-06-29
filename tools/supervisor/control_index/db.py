"""Database connection manager for the control index.

Handles WAL mode, busy timeout, schema creation, and version tracking.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from . import SCHEMA_VERSION

_SCHEMA_SQL = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")


def get_connection(db_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection with WAL mode and foreign keys."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


@contextmanager
def connect(db_path: Path):
    """Context-managed connection that auto-closes."""
    conn = get_connection(db_path)
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Path) -> None:
    """Create the database with the full schema.

    Safe to call on an existing database — uses IF NOT EXISTS.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(db_path)
    try:
        conn.executescript(_SCHEMA_SQL)
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT OR REPLACE INTO schema_meta (key, value) VALUES (?, ?)",
            ("schema_version", str(SCHEMA_VERSION)),
        )
        conn.execute(
            "INSERT OR IGNORE INTO schema_meta (key, value) VALUES (?, ?)",
            ("created_at", now),
        )
        conn.execute(
            "INSERT OR REPLACE INTO schema_meta (key, value) VALUES (?, ?)",
            ("last_init", now),
        )
        conn.commit()
    finally:
        conn.close()


def get_schema_version(db_path: Path) -> int:
    """Return current schema version, or 0 if DB doesn't exist or has no meta."""
    if not db_path.exists():
        return 0
    try:
        conn = get_connection(db_path)
        try:
            row = conn.execute(
                "SELECT value FROM schema_meta WHERE key = 'schema_version'"
            ).fetchone()
            return int(row["value"]) if row else 0
        finally:
            conn.close()
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        return 0


def ensure_db(db_path: Path) -> sqlite3.Connection:
    """Create DB if needed, verify schema version, return connection."""
    if not db_path.exists() or get_schema_version(db_path) < SCHEMA_VERSION:
        init_db(db_path)
    return get_connection(db_path)


def get_table_names(conn: sqlite3.Connection) -> list[str]:
    """Return all table names in the database (excluding internal SQLite tables)."""
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [r["name"] for r in rows]
