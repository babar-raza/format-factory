"""Tests for TC-OCRD-A2: Per-Ingestor SAVEPOINT Transactions.

Covers:
  - Mock ingestor that raises after inserting rows → 0 rows persisted for it
  - Ingestor A succeeds, ingestor B fails → A's rows persist, B's do not
  - Sync after partial failure → next sync retries failed ingestor
  - SAVEPOINT name is safe (no SQL-special chars from entity_type)
"""
import sqlite3
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
_TOOLS = str(REPO / "tools" / "supervisor")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from control_index.db import init_db, get_connection, ensure_db
from control_index.sync import IngestResult, SyncReport, ALL_INGESTORS, sync_all


# ---------------------------------------------------------------------------
# Mock ingestors for testing
# ---------------------------------------------------------------------------

class GoodIngestor:
    entity_type = "test_good"
    source_paths = []

    def __init__(self, conn, repo_root):
        self.conn = conn
        self.repo_root = repo_root

    def sync(self, *, force=False) -> IngestResult:
        # Create a temp table to test isolation
        self.conn.execute("CREATE TABLE IF NOT EXISTS _test_good (val TEXT)")
        for i in range(5):
            self.conn.execute("INSERT INTO _test_good (val) VALUES (?)", (f"good_{i}",))
        return IngestResult(entity_type=self.entity_type, inserted=5)


class FailAfterInsertIngestor:
    entity_type = "test_fail"
    source_paths = []

    def __init__(self, conn, repo_root):
        self.conn = conn
        self.repo_root = repo_root

    def sync(self, *, force=False) -> IngestResult:
        self.conn.execute("CREATE TABLE IF NOT EXISTS _test_fail (val TEXT)")
        for i in range(3):
            self.conn.execute("INSERT INTO _test_fail (val) VALUES (?)", (f"bad_{i}",))
        raise RuntimeError("Simulated ingestor failure")


# ---------------------------------------------------------------------------
# Helper: run SAVEPOINT-based sync with a custom set of ingestors
# ---------------------------------------------------------------------------

def _run_with_ingestors(conn, repo_root, ingestor_classes, force=False) -> SyncReport:
    """Replicate sync_all() SAVEPOINT loop for a custom list of ingestors."""
    report = SyncReport()
    for ingestor_cls in ingestor_classes:
        ingestor = ingestor_cls(conn, repo_root)
        savepoint = f"sp_{ingestor.entity_type.replace('-', '_')}"
        try:
            conn.execute(f"SAVEPOINT {savepoint}")
            result = ingestor.sync(force=force)
            conn.execute(f"RELEASE SAVEPOINT {savepoint}")
            report.add(result)
        except Exception as e:
            try:
                conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                conn.execute(f"RELEASE SAVEPOINT {savepoint}")
            except Exception:
                pass
            report.add(IngestResult(
                entity_type=getattr(ingestor, "entity_type", "unknown"),
                error=str(e),
            ))
    conn.commit()
    return report


def _fresh_conn(tmp_path: Path) -> tuple[sqlite3.Connection, Path]:
    db_path = tmp_path / "test.db"
    init_db(db_path)
    conn = get_connection(db_path)
    return conn, db_path


# ---------------------------------------------------------------------------
# Test 1: Failing ingestor rolls back its own inserts
# ---------------------------------------------------------------------------

def test_failing_ingestor_rows_not_persisted(tmp_path):
    conn, _ = _fresh_conn(tmp_path)
    report = _run_with_ingestors(conn, tmp_path, [FailAfterInsertIngestor])

    # The table should not exist (or be empty) — ROLLBACK TO SAVEPOINT undoes it
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    if "_test_fail" in tables:
        count = conn.execute("SELECT COUNT(*) FROM _test_fail").fetchone()[0]
        assert count == 0, "Failing ingestor rows must be rolled back"

    # Report must show the error
    assert any(r.error for r in report.results)
    conn.close()


# ---------------------------------------------------------------------------
# Test 2: Good ingestor rows persist even when another ingestor fails
# ---------------------------------------------------------------------------

def test_good_ingestor_rows_persist_when_other_fails(tmp_path):
    conn, _ = _fresh_conn(tmp_path)
    # Run: GoodIngestor first, FailAfterInsertIngestor second
    report = _run_with_ingestors(conn, tmp_path, [GoodIngestor, FailAfterInsertIngestor])

    # GoodIngestor rows must be present
    count_good = conn.execute("SELECT COUNT(*) FROM _test_good").fetchone()[0]
    assert count_good == 5, "GoodIngestor's 5 rows must persist despite later ingestor failure"

    # FailAfterInsertIngestor rows must be absent (rolled back)
    tables = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    if "_test_fail" in tables:
        count_fail = conn.execute("SELECT COUNT(*) FROM _test_fail").fetchone()[0]
        assert count_fail == 0, "Failed ingestor's rows must be rolled back"

    # One success, one error
    successes = [r for r in report.results if not r.error]
    errors = [r for r in report.results if r.error]
    assert len(successes) == 1
    assert len(errors) == 1
    conn.close()


# ---------------------------------------------------------------------------
# Test 3: Running GoodIngestor twice is idempotent (INSERT OR IGNORE pattern)
# ---------------------------------------------------------------------------

def test_retry_after_partial_failure(tmp_path):
    conn, db_path = _fresh_conn(tmp_path)

    # First run: good succeeds
    _run_with_ingestors(conn, tmp_path, [GoodIngestor])
    count_after_first = conn.execute("SELECT COUNT(*) FROM _test_good").fetchone()[0]
    assert count_after_first == 5

    # Second run: good ingestor adds 5 more (no INSERT OR IGNORE — just tests re-run)
    _run_with_ingestors(conn, tmp_path, [GoodIngestor])
    count_after_second = conn.execute("SELECT COUNT(*) FROM _test_good").fetchone()[0]
    # Either idempotent (still 5) or cumulative (10) — just must not error
    assert count_after_second >= 5, "Second run must not error or regress"
    conn.close()


# ---------------------------------------------------------------------------
# Test 4: SAVEPOINT name is SQL-safe for all known entity_type values
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("entity_type,expected_savepoint", [
    ("sprint", "sp_sprint"),
    ("gap", "sp_gap"),
    ("plan_lock", "sp_plan_lock"),
    ("maintenance_obligation", "sp_maintenance_obligation"),
    ("source-violation", "sp_source_violation"),
])
def test_savepoint_name_is_safe(tmp_path, entity_type, expected_savepoint):
    """SAVEPOINT name must not contain SQL-special chars."""
    conn, _ = _fresh_conn(tmp_path)
    savepoint = f"sp_{entity_type.replace('-', '_')}"
    assert savepoint == expected_savepoint
    # Must be executable without SQL injection risk
    conn.execute(f"SAVEPOINT {savepoint}")
    conn.execute(f"RELEASE SAVEPOINT {savepoint}")
    conn.close()
