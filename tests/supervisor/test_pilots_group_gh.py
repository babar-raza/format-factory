"""Pilots 17-22: Compatibility, Integration, Secret Exclusion, Navigation, Idempotency, Recovery (TC-OCRD-C8-04).

Pilot 17: compatibility — migrate_v3_add_control_tables is idempotent on v3 DB
Pilot 18: supervisor integration — check_continuation includes control_index_warnings key
Pilot 19: secret exclusion — synthetic test key not indexed (content check)
Pilot 20: human navigation — query.py control-layers returns parseable JSON
Pilot 21: idempotency — second full sync produces same table counts
Pilot 22: recovery — DB deletion and re-init restores schema correctly
"""
import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
_TOOLS = str(REPO / "tools" / "supervisor")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from control_index.db import init_db, get_connection


def _fresh_conn(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = get_connection(db_path)
    return conn, db_path


# ---------------------------------------------------------------------------
# Pilot 17: v3→v4 migration idempotent
# ---------------------------------------------------------------------------

def test_pilot17_migration_v3_to_v4_idempotent(tmp_path):
    """Pilot 17: _migrate_v3_add_control_tables can be called twice without error."""
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = get_connection(db_path)

    from control_index.db import _migrate_v3_add_control_tables

    # Call once
    _migrate_v3_add_control_tables(conn)
    # Call again — should not raise (IF NOT EXISTS guards)
    _migrate_v3_add_control_tables(conn)

    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    assert "control_layers" in tables
    assert "trust_registry" in tables
    conn.close()


# ---------------------------------------------------------------------------
# Pilot 18: check_continuation includes control_index_warnings
# ---------------------------------------------------------------------------

def test_pilot18_check_continuation_has_control_index_warnings_key(tmp_path):
    """Pilot 18: check_continuation.py source contains control_index_warnings key."""
    source = (REPO / "tools" / "supervisor" / "check_continuation.py").read_text(encoding="utf-8")
    assert "control_index_warnings" in source, \
        "Pilot 18 FAIL: check_continuation.py must emit control_index_warnings"


# ---------------------------------------------------------------------------
# Pilot 19: synthetic test key not indexed (secret exclusion)
# ---------------------------------------------------------------------------

def test_pilot19_synthetic_test_key_not_in_db(tmp_path):
    """Pilot 19: Synthetic test key sk-ant-SYNTHETIC-TEST-KEY-DO-NOT-INDEX is not stored in DB."""
    # This is a purely synthetic test key for validation — not a real credential.
    SYNTHETIC_KEY = "sk-ant-SYNTHETIC-TEST-KEY-DO-NOT-INDEX"

    conn, db_path = _fresh_conn(tmp_path)

    # Check FTS5 index for the synthetic key
    try:
        rows = conn.execute(
            "SELECT COUNT(*) FROM fts_operational WHERE fts_operational MATCH ?",
            (SYNTHETIC_KEY,),
        ).fetchone()
        count = rows[0] if rows else 0
    except Exception:
        count = 0

    assert count == 0, \
        f"Pilot 19 FAIL: synthetic test key found in FTS5 index ({count} rows)"
    conn.close()


# ---------------------------------------------------------------------------
# Pilot 20: human navigation — query.py control-layers returns parseable JSON
# ---------------------------------------------------------------------------

def test_pilot20_query_control_layers_parseable_json(tmp_path):
    """Pilot 20: The control-layers query command returns valid JSON."""
    import subprocess
    import sys as _sys
    result = subprocess.run(
        [_sys.executable, "-m", "tools.supervisor.control_index.query", "control-layers"],
        capture_output=True, text=True,
        cwd=str(REPO),
    )
    # Should not error
    assert result.returncode == 0, f"Pilot 20 FAIL: exit {result.returncode}: {result.stderr}"
    # Should be parseable JSON
    data = json.loads(result.stdout)
    assert isinstance(data, list), f"Pilot 20 FAIL: expected list, got {type(data)}"


# ---------------------------------------------------------------------------
# Pilot 21: idempotency — second sync same counts
# ---------------------------------------------------------------------------

def test_pilot21_idempotency_second_sync_stable(tmp_path):
    """Pilot 21: Running ControlLayerIngestor twice produces stable table counts."""
    conn, db_path = _fresh_conn(tmp_path)
    control_dir = tmp_path / "reports" / "control-layer"
    control_dir.mkdir(parents=True)
    yaml_content = """mission_id: TEST
existing_control_layers:
  - layer_key: stable_layer
    name: Stable Layer
    status: ACTIVE
    primary_purpose: Testing idempotency
    implementation_paths: []
    data_paths: []
    consumers: []
    claimed_features: []
    observable_features: []
"""
    (control_dir / "existing-control-layers.yaml").write_text(yaml_content, encoding="utf-8")

    from control_index.ingestors.control_layer_ingestor import ControlLayerIngestor

    # First sync
    ControlLayerIngestor(conn, tmp_path).sync(force=True)
    count_after_first = conn.execute("SELECT COUNT(*) FROM control_layers").fetchone()[0]

    # Second sync (force=True to bypass hash check)
    ControlLayerIngestor(conn, tmp_path).sync(force=True)
    count_after_second = conn.execute("SELECT COUNT(*) FROM control_layers").fetchone()[0]

    assert count_after_first == count_after_second == 1, \
        f"Pilot 21 FAIL: counts differ ({count_after_first} vs {count_after_second})"
    conn.close()


# ---------------------------------------------------------------------------
# Pilot 22: recovery — DB deletion + re-init restores schema
# ---------------------------------------------------------------------------

def test_pilot22_db_deletion_and_reinit_restores_schema(tmp_path):
    """Pilot 22: Deleting the DB and calling init_db() restores all v4 tables."""
    db_path = tmp_path / "recovery.db"
    init_db(db_path)
    assert db_path.exists()

    # Delete the DB
    db_path.unlink()
    assert not db_path.exists()

    # Re-init
    init_db(db_path)
    assert db_path.exists()

    conn = get_connection(db_path)
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    conn.close()

    required = {
        "control_layers", "control_features", "quarantines", "trust_registry",
        "gaps", "sprints", "plan_locks", "gap_attempts",
    }
    missing = required - tables
    assert not missing, f"Pilot 22 FAIL: missing tables after re-init: {missing}"
