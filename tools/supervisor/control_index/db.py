"""Database connection manager for the control index.

Handles WAL mode, busy timeout, schema creation, and version tracking.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from . import SCHEMA_VERSION

_SCHEMA_SQL = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# TC-OCRD-A4: Schema Migration Framework
# ---------------------------------------------------------------------------
# MIGRATIONS: list of (from_version, to_version, description) for documentation.
# MIGRATION_FUNCS: list of (from_version, to_version, callable) for execution.
# Each callable receives a sqlite3.Connection and must be idempotent.
# ---------------------------------------------------------------------------
MIGRATIONS: list[tuple[int, int, str]] = [
    (2, 3, "Add gap_attempts table for gap selection tracking (TC-OCRD-A1)"),
    (3, 4, "Add control layer discovery tables: control_layers, control_features, "
           "control_feature_consumers, feature_parity_results, quarantines, "
           "trust_registry, plans (TC-OCRD-C3)"),
]
MIGRATION_FUNCS: list[tuple[int, int, object]] = []


def _migrate_v2_add_gap_attempts(conn: sqlite3.Connection) -> None:
    """Migration 2→3: Add gap_attempts table for existing databases (TC-OCRD-A1)."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS gap_attempts (
            attempt_id     TEXT PRIMARY KEY,
            gap_id         TEXT NOT NULL,
            sprint_id      TEXT NOT NULL,
            item_id        TEXT,
            outcome        TEXT,
            rework_reason  TEXT,
            attempted_at   TEXT NOT NULL,
            source_file    TEXT,
            ingested_at    TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_ga_gap ON gap_attempts(gap_id);
        CREATE INDEX IF NOT EXISTS idx_ga_sprint ON gap_attempts(sprint_id);
        CREATE INDEX IF NOT EXISTS idx_ga_outcome ON gap_attempts(outcome);
    """)


MIGRATION_FUNCS.append((2, 3, _migrate_v2_add_gap_attempts))


def _migrate_v3_add_control_tables(conn: sqlite3.Connection) -> None:
    """Migration 3→4: Add control layer discovery tables (TC-OCRD-C3)."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS control_layers (
            layer_key                TEXT PRIMARY KEY,
            name                     TEXT NOT NULL,
            status                   TEXT NOT NULL,
            authority_scope          TEXT,
            primary_purpose          TEXT,
            implementation_paths     TEXT,
            data_paths               TEXT,
            consumers                TEXT,
            observable_features_count INTEGER DEFAULT 0,
            last_assessed            TEXT,
            ingested_at              TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS control_features (
            feature_id               TEXT PRIMARY KEY,
            control_layer_key        TEXT REFERENCES control_layers(layer_key),
            feature_name             TEXT NOT NULL,
            category                 TEXT,
            entry_points             TEXT,
            current_status           TEXT NOT NULL,
            authority_effect         TEXT,
            observable_behavior      TEXT,
            ingested_at              TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS control_feature_consumers (
            id                       INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_id               TEXT REFERENCES control_features(feature_id),
            consumer_id              TEXT NOT NULL,
            consumer_type            TEXT,
            consumer_path            TEXT,
            expected_contract        TEXT,
            dependency_strength      TEXT,
            migration_risk           TEXT
        );
        CREATE TABLE IF NOT EXISTS feature_parity_results (
            feature_id               TEXT PRIMARY KEY REFERENCES control_features(feature_id),
            reuse_strategy           TEXT,
            parity_status            TEXT NOT NULL,
            intentional_changes      TEXT,
            verified_at              TEXT
        );
        CREATE TABLE IF NOT EXISTS quarantines (
            quarantine_id            TEXT PRIMARY KEY,
            artifact_path            TEXT NOT NULL,
            detected_at              TEXT DEFAULT (datetime('now')),
            validation_failures      TEXT,
            severity                 TEXT,
            status                   TEXT DEFAULT 'ACTIVE'
        );
        CREATE TABLE IF NOT EXISTS trust_registry (
            artifact_path            TEXT PRIMARY KEY,
            authority_level          TEXT NOT NULL,
            trusted                  INTEGER NOT NULL DEFAULT 0,
            reason                   TEXT,
            assessed_at              TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS plans (
            plan_id                  TEXT PRIMARY KEY,
            plan_path                TEXT NOT NULL,
            plan_type                TEXT,
            title                    TEXT,
            status                   TEXT,
            open_taskcards           INTEGER DEFAULT 0,
            closed_taskcards         INTEGER DEFAULT 0,
            ingested_at              TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_cf_layer ON control_features(control_layer_key);
        CREATE INDEX IF NOT EXISTS idx_cfc_feature ON control_feature_consumers(feature_id);
        CREATE INDEX IF NOT EXISTS idx_q_status ON quarantines(status);
        CREATE INDEX IF NOT EXISTS idx_tr_trusted ON trust_registry(trusted);
        CREATE INDEX IF NOT EXISTS idx_plans_type ON plans(plan_type);
    """)


MIGRATION_FUNCS.append((3, 4, _migrate_v3_add_control_tables))


def _add_column_if_missing(
    conn: sqlite3.Connection, table: str, column: str, definition: str
) -> bool:
    """Add a column to a table if it does not already exist.

    Args:
        conn: Open SQLite connection.
        table: Table name.
        column: Column name to add.
        definition: SQL type + constraints (e.g. "TEXT DEFAULT NULL").

    Returns:
        True if the column was added, False if it already existed.
    """
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        return True
    return False


def apply_migrations(conn: sqlite3.Connection, current_version: int) -> int:
    """Apply all pending migrations in ascending order.

    Reads MIGRATION_FUNCS and executes each migration whose from_version >= current_version.
    Updates schema_meta.schema_version after each successful migration.
    Silently skips migrations that have already been applied (idempotent).

    Args:
        conn: Open SQLite connection.
        current_version: The schema version currently stored in the database.

    Returns:
        The new schema version after all applicable migrations have run.
    """
    pending = sorted(
        [(fv, tv, fn) for fv, tv, fn in MIGRATION_FUNCS if fv >= current_version],
        key=lambda x: x[0],
    )
    new_version = current_version
    for _from_v, to_v, migration_fn in pending:
        try:
            migration_fn(conn)
            conn.execute(
                "UPDATE schema_meta SET value = ? WHERE key = 'schema_version'",
                (str(to_v),),
            )
            conn.commit()
            new_version = to_v
        except sqlite3.OperationalError:
            # Migration may already be applied — continue safely
            pass
    return new_version


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
    """Create DB if needed, apply migrations, return connection.

    TC-OCRD-A4: After init_db(), apply_migrations() is called to handle
    column additions to existing tables (ALTER TABLE) that CREATE TABLE IF NOT EXISTS
    would silently skip on an already-initialized database.
    """
    if not db_path.exists() or get_schema_version(db_path) < SCHEMA_VERSION:
        init_db(db_path)
    conn = get_connection(db_path)
    current_v = get_schema_version(db_path)
    apply_migrations(conn, current_v)
    return conn


def get_table_names(conn: sqlite3.Connection) -> list[str]:
    """Return all table names in the database (excluding internal SQLite tables)."""
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [r["name"] for r in rows]
