"""Tests for the TC-OCRD-A4 Schema Migration Framework.

Tests:
  1. Fresh DB at SCHEMA_VERSION=3
  2. Simulate v2 DB → apply_migrations → version advances
  3. _add_column_if_missing on missing column → column appears
  4. _add_column_if_missing on existing column → no error, no duplicate
  5. apply_migrations called twice is idempotent
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

from tools.supervisor.control_index import SCHEMA_VERSION
from tools.supervisor.control_index.db import (
    MIGRATION_FUNCS,
    MIGRATIONS,
    _add_column_if_missing,
    apply_migrations,
    ensure_db,
    get_schema_version,
    init_db,
)


class TestSchemaVersion:
    def test_fresh_db_has_current_schema_version(self, tmp_path):
        """Test 1: Fresh DB at SCHEMA_VERSION."""
        db_path = tmp_path / "test.db"
        init_db(db_path)
        assert get_schema_version(db_path) == SCHEMA_VERSION
        assert SCHEMA_VERSION == 3

    def test_schema_version_constant_is_3(self):
        """SCHEMA_VERSION must be 3 (TC-OCRD-A4-01-04)."""
        assert SCHEMA_VERSION == 3


class TestApplyMigrations:
    def test_simulate_v2_db_migrations_advance_version(self, tmp_path):
        """Test 2: Simulate v2 DB; register a migration; call apply_migrations; version advances."""
        db_path = tmp_path / "test.db"
        init_db(db_path)

        # Manually downgrade version to simulate a v2 DB
        conn = sqlite3.connect(str(db_path))
        conn.execute("UPDATE schema_meta SET value = '2' WHERE key = 'schema_version'")
        conn.commit()
        conn.close()
        assert get_schema_version(db_path) == 2

        # Register a test migration (2→3)
        def migration_2_to_3(c: sqlite3.Connection) -> None:
            _add_column_if_missing(c, "schema_meta", "_migration_test_col", "TEXT DEFAULT NULL")

        orig_funcs = MIGRATION_FUNCS[:]
        try:
            MIGRATION_FUNCS.append((2, 3, migration_2_to_3))
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            new_version = apply_migrations(conn, 2)
            conn.close()
        finally:
            MIGRATION_FUNCS[:] = orig_funcs

        assert new_version == 3

    def test_apply_migrations_idempotent(self, tmp_path):
        """Test 5: apply_migrations called twice on the same DB is idempotent."""
        db_path = tmp_path / "test.db"
        init_db(db_path)

        calls = []

        def idempotent_migration(c: sqlite3.Connection) -> None:
            calls.append(1)
            _add_column_if_missing(c, "schema_meta", "_idempotent_col", "TEXT DEFAULT NULL")

        orig_funcs = MIGRATION_FUNCS[:]
        try:
            MIGRATION_FUNCS.append((2, 3, idempotent_migration))

            # Manually set version to 2 to trigger migration
            conn_raw = sqlite3.connect(str(db_path))
            conn_raw.execute("UPDATE schema_meta SET value = '2' WHERE key = 'schema_version'")
            conn_raw.commit()
            conn_raw.close()

            conn1 = sqlite3.connect(str(db_path))
            conn1.row_factory = sqlite3.Row
            apply_migrations(conn1, 2)
            conn1.close()

            # Second call: version is now 3, no pending migrations from 2
            conn2 = sqlite3.connect(str(db_path))
            conn2.row_factory = sqlite3.Row
            apply_migrations(conn2, 3)
            conn2.close()
        finally:
            MIGRATION_FUNCS[:] = orig_funcs

        # Migration should have run exactly once (version 2→3, second call has version 3)
        assert len(calls) == 1, f"Migration ran {len(calls)} times, expected 1"


class TestAddColumnIfMissing:
    def _make_db(self, tmp_path: Path) -> Path:
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
        conn.execute("CREATE TABLE schema_meta (key TEXT PRIMARY KEY, value TEXT)")
        conn.commit()
        conn.close()
        return db_path

    def test_adds_missing_column(self, tmp_path):
        """Test 3: _add_column_if_missing on missing column → column appears."""
        db_path = self._make_db(tmp_path)
        conn = sqlite3.connect(str(db_path))
        result = _add_column_if_missing(conn, "test_table", "new_col", "TEXT DEFAULT NULL")
        conn.commit()
        conn.close()

        assert result is True, "Should return True when column was added"

        # Verify column exists
        conn2 = sqlite3.connect(str(db_path))
        cols = {row[1] for row in conn2.execute("PRAGMA table_info(test_table)").fetchall()}
        conn2.close()
        assert "new_col" in cols

    def test_no_error_on_existing_column(self, tmp_path):
        """Test 4: _add_column_if_missing on existing column → no error, no duplicate."""
        db_path = self._make_db(tmp_path)
        conn = sqlite3.connect(str(db_path))

        # Add column first time
        _add_column_if_missing(conn, "test_table", "existing_col", "TEXT DEFAULT NULL")
        conn.commit()

        # Add same column second time — must not raise and must return False
        result = _add_column_if_missing(conn, "test_table", "existing_col", "TEXT DEFAULT NULL")
        conn.commit()
        conn.close()

        assert result is False, "Should return False when column already exists"

        # Verify no duplicate columns
        conn2 = sqlite3.connect(str(db_path))
        cols = [row[1] for row in conn2.execute("PRAGMA table_info(test_table)").fetchall()]
        conn2.close()
        assert cols.count("existing_col") == 1, "Column must not be duplicated"


class TestMigrationFrameworkStructure:
    def test_migrations_list_exists(self):
        """MIGRATIONS and MIGRATION_FUNCS lists must exist and be lists."""
        assert isinstance(MIGRATIONS, list)
        assert isinstance(MIGRATION_FUNCS, list)

    def test_ensure_db_calls_apply_migrations(self, tmp_path):
        """ensure_db must return a connection after applying migrations."""
        db_path = tmp_path / "test.db"
        conn = ensure_db(db_path)
        assert conn is not None
        # Should be a valid connection
        row = conn.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()
        assert row is not None
        conn.close()

    def test_add_column_if_missing_importable(self):
        """_add_column_if_missing must be importable from db module."""
        from tools.supervisor.control_index.db import _add_column_if_missing
        assert callable(_add_column_if_missing)

    def test_apply_migrations_importable(self):
        """apply_migrations must be importable from db module."""
        from tools.supervisor.control_index.db import apply_migrations
        assert callable(apply_migrations)
