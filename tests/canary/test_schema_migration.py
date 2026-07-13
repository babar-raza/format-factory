"""Tests for SQLite canary shadow table schema (TC-TEST-001-02).

4 tests verifying that the canary shadow tables (validator_shadow_observations,
grader_shadow_observations) exist and are queryable after init_db.
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "tools" / "supervisor"))

from control_index.db import init_db, get_schema_version
from control_index import SCHEMA_VERSION


# ---------------------------------------------------------------------------
# Test 1: both canary tables exist after init_db
# ---------------------------------------------------------------------------

def test_v3_migration_creates_both_tables(tmp_path):
    """init_db creates both validator_shadow_observations and grader_shadow_observations."""
    db_path = tmp_path / "test-control.db"
    init_db(db_path)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    finally:
        conn.close()

    assert "validator_shadow_observations" in tables
    assert "grader_shadow_observations" in tables


# ---------------------------------------------------------------------------
# Test 2: init_db is idempotent (second call is safe)
# ---------------------------------------------------------------------------

def test_v3_migration_idempotent(tmp_path):
    """Calling init_db twice does not raise and tables still exist."""
    db_path = tmp_path / "test-control.db"
    init_db(db_path)
    init_db(db_path)  # second call must not raise

    conn = sqlite3.connect(str(db_path))
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    finally:
        conn.close()

    assert "validator_shadow_observations" in tables
    assert "grader_shadow_observations" in tables


# ---------------------------------------------------------------------------
# Test 3: schema version matches SCHEMA_VERSION constant after init_db
# ---------------------------------------------------------------------------

def test_current_schema_version(tmp_path):
    """After init_db, get_schema_version returns the current SCHEMA_VERSION."""
    db_path = tmp_path / "test-control.db"
    init_db(db_path)
    version = get_schema_version(db_path)
    assert version == SCHEMA_VERSION


# ---------------------------------------------------------------------------
# Test 4: both tables accept inserts and round-trip correctly
# ---------------------------------------------------------------------------

def test_v3_table_insert_and_query(tmp_path):
    """Rows inserted into canary shadow tables round-trip with correct field values."""
    db_path = tmp_path / "test-control.db"
    init_db(db_path)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    now = datetime.now(timezone.utc).isoformat()

    try:
        # Insert into validator_shadow_observations
        conn.execute(
            """INSERT INTO validator_shadow_observations
               (run_id, sprint_id, validator_name, format_scope,
                stable_result, stable_blocks_sprint,
                candidate_result, candidate_blocks_sprint, agreement, error, observed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("run-001", "sprint-42", "validate_something", None,
             "FAIL", 1, None, None, None, None, now)
        )
        conn.commit()

        row = conn.execute(
            "SELECT * FROM validator_shadow_observations WHERE run_id='run-001'"
        ).fetchone()
        assert row["sprint_id"] == "sprint-42"
        assert row["validator_name"] == "validate_something"
        assert row["stable_result"] == "FAIL"
        assert row["stable_blocks_sprint"] == 1
        assert row["candidate_result"] is None  # NULL for failed shadow call
        assert row["agreement"] is None          # NULL when shadow call failed

        # Insert into grader_shadow_observations
        conn.execute(
            """INSERT INTO grader_shadow_observations
               (run_id, sprint_id, work_item_id, primary_provider, shadow_provider,
                primary_grade, shadow_grade, agreement, error, observed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("run-002", "sprint-42", "item-1", "gpt-4o", "claude-3-5-sonnet",
             "ACCEPTED", None, None, "ConnectionError: timeout", now)
        )
        conn.commit()

        row2 = conn.execute(
            "SELECT * FROM grader_shadow_observations WHERE run_id='run-002'"
        ).fetchone()
        assert row2["work_item_id"] == "item-1"
        assert row2["primary_provider"] == "gpt-4o"
        assert row2["shadow_provider"] == "claude-3-5-sonnet"
        assert row2["primary_grade"] == "ACCEPTED"
        assert row2["shadow_grade"] is None   # failed shadow call
        assert row2["agreement"] is None       # NULL when shadow call failed
        assert "timeout" in row2["error"]

    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Test 5: migration from previous schema — shadow tables added to existing DB
# ---------------------------------------------------------------------------

def test_init_db_adds_shadow_tables_to_existing_db(tmp_path):
    """init_db creates shadow tables when called on a database that had none.

    Proves the migration-from-previous-schema path: init_db running schema.sql
    with CREATE TABLE IF NOT EXISTS adds shadow tables to any existing DB that
    was created before the shadow tables were introduced. The test simulates this
    by creating a fresh DB (init_db creates all tables) and then manually dropping
    only the shadow tables to emulate an older-schema state.
    """
    db_path = tmp_path / "test-existing.db"

    # Initialize normally — creates all tables
    init_db(db_path)

    # Drop shadow tables to simulate an older-schema database
    conn = sqlite3.connect(str(db_path))
    conn.execute("DROP TABLE IF EXISTS validator_shadow_observations")
    conn.execute("DROP TABLE IF EXISTS grader_shadow_observations")
    conn.commit()
    tables_after_drop = {
        row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn.close()
    assert "validator_shadow_observations" not in tables_after_drop
    assert "grader_shadow_observations" not in tables_after_drop

    # Re-run init_db — CREATE TABLE IF NOT EXISTS must restore the shadow tables
    init_db(db_path)

    conn2 = sqlite3.connect(str(db_path))
    tables_restored = {
        row[0] for row in conn2.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    conn2.close()

    assert "validator_shadow_observations" in tables_restored, \
        "init_db must restore validator_shadow_observations to a database that lost it"
    assert "grader_shadow_observations" in tables_restored, \
        "init_db must restore grader_shadow_observations to a database that lost it"
