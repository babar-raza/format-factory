"""Tests for control_index database initialization and connection management."""

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from control_index import SCHEMA_VERSION
from control_index.db import (
    get_connection,
    get_schema_version,
    get_table_names,
    init_db,
    ensure_db,
)

# Expected user-defined tables (excluding FTS5 internal shadow tables)
EXPECTED_TABLES = {
    "capabilities",
    "events",
    "failures",
    "formats",
    "fts_operational",
    "fts_operational_config",
    "fts_operational_content",
    "fts_operational_data",
    "fts_operational_docsize",
    "fts_operational_idx",
    "gap_spec_facts",
    "gaps",
    "layer_dependencies",
    "layers",
    "plan_locks",
    "qnames",
    "schema_meta",
    "skills",
    "source_manifest",
    "source_violations",
    "sprint_work_items",
    "sprints",
}


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test.db"


def test_init_creates_db(db_path):
    """init_db creates the database file."""
    assert not db_path.exists()
    init_db(db_path)
    assert db_path.exists()


def test_init_creates_all_tables(db_path):
    """init_db creates all expected tables."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        tables = set(get_table_names(conn))
        assert tables == EXPECTED_TABLES
    finally:
        conn.close()


def test_schema_version_set(db_path):
    """init_db sets the schema version correctly."""
    init_db(db_path)
    assert get_schema_version(db_path) == SCHEMA_VERSION


def test_schema_version_zero_when_no_db(tmp_path):
    """get_schema_version returns 0 for non-existent DB."""
    assert get_schema_version(tmp_path / "nonexistent.db") == 0


def test_wal_mode_active(db_path):
    """Database uses WAL journal mode."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode == "wal"
    finally:
        conn.close()


def test_foreign_keys_enabled(db_path):
    """Foreign keys are enabled."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        assert fk == 1
    finally:
        conn.close()


def test_init_idempotent(db_path):
    """Calling init_db twice does not error or change schema version."""
    init_db(db_path)
    v1 = get_schema_version(db_path)
    init_db(db_path)
    v2 = get_schema_version(db_path)
    assert v1 == v2 == SCHEMA_VERSION


def test_ensure_db_creates_if_missing(db_path):
    """ensure_db creates DB if it doesn't exist and returns connection."""
    assert not db_path.exists()
    conn = ensure_db(db_path)
    try:
        assert db_path.exists()
        assert get_schema_version(db_path) == SCHEMA_VERSION
    finally:
        conn.close()


def test_ensure_db_returns_connection(db_path):
    """ensure_db returns a working connection."""
    conn = ensure_db(db_path)
    try:
        row = conn.execute("SELECT 1 + 1 AS result").fetchone()
        assert row["result"] == 2
    finally:
        conn.close()


def test_row_factory_returns_dict_like(db_path):
    """Connection row_factory produces dict-like Row objects."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT value FROM schema_meta WHERE key = 'schema_version'"
        ).fetchone()
        assert row["value"] == str(SCHEMA_VERSION)
    finally:
        conn.close()


def test_created_at_recorded(db_path):
    """init_db records created_at timestamp."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT value FROM schema_meta WHERE key = 'created_at'"
        ).fetchone()
        assert row is not None
        assert "T" in row["value"]  # ISO 8601 format
    finally:
        conn.close()
